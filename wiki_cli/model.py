"""The only place in the harness that talks to a language model.

Local mode drives Ollama's HTTP API on 127.0.0.1 using nothing but the Python
standard library, so an offline run has no third-party network code in the path
at all. Online mode is an optional extension and is never reached unless the
user explicitly passes ``--mode online``.
"""

from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field

from . import config


def detokenise(text: str) -> str:
    """Normalise the SentencePiece space glyph out of generated text.

    Gemma 3n intermittently emits U+2581 ('lower one eighth block') where a space
    belongs -- it is the tokenizer's internal space marker leaking into the
    decoded string. Substituting a real space is detokenisation, not editing:
    no word, number or citation is changed.
    """
    return text.replace("\u2581", " ")


class ModelUnavailable(RuntimeError):
    """Raised when the local runtime is not reachable or the model is missing."""


@dataclass
class Completion:
    text: str
    model: str
    mode: str
    seconds: float
    prompt_tokens: int = 0
    completion_tokens: int = 0
    options: dict = field(default_factory=dict)


def _post(url: str, payload: dict, timeout: int = 300) -> dict:
    data = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        url, data=data, headers={"Content-Type": "application/json"}, method="POST"
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


# --------------------------------------------------------------------------
# Local runtime (Ollama)
# --------------------------------------------------------------------------

def local_runtime_status() -> dict:
    """Report whether Ollama is up and which of our models it has pulled."""
    status = {"reachable": False, "version": None, "models": [], "error": None}
    try:
        with urllib.request.urlopen(
            f"{config.OLLAMA_HOST}/api/version", timeout=5
        ) as response:
            status["version"] = json.loads(response.read().decode())["version"]
        status["reachable"] = True
        with urllib.request.urlopen(f"{config.OLLAMA_HOST}/api/tags", timeout=10) as response:
            tags = json.loads(response.read().decode())
        status["models"] = sorted(m["name"] for m in tags.get("models", []))
    except (urllib.error.URLError, OSError, ValueError, KeyError) as exc:
        status["error"] = str(exc)
    return status


def require_local_model(model: str) -> None:
    """Fail early, with an actionable message, instead of mid-answer."""
    status = local_runtime_status()
    if not status["reachable"]:
        raise ModelUnavailable(
            "Cannot reach the local Ollama runtime at "
            f"{config.OLLAMA_HOST}.\n"
            "  Start it with:  brew services start ollama\n"
            "  Or run in the foreground:  ollama serve\n"
            "  Search mode does not need the model: try `wiki search \"<terms>\"`."
        )
    # A bare name like "gemma3n" may match any installed tag, but an explicit
    # "gemma3n:e99b" must match exactly -- otherwise a typo'd tag slipped past
    # this check and surfaced later as a raw 404 from the runtime.
    installed_bases = {name.split(":")[0] for name in status["models"]}
    tagged = ":" in model
    if model not in status["models"] and (tagged or model not in installed_bases):
        raise ModelUnavailable(
            f"The local runtime is up (Ollama {status['version']}) but model "
            f"'{model}' is not installed.\n"
            f"  Installed: {', '.join(status['models']) or '(none)'}\n"
            f"  Pull it while online with:  ollama pull {model}"
        )


def generate_local(
    system: str,
    user: str,
    options: dict,
    model: str | None = None,
    schema: dict | None = None,
) -> Completion:
    """``schema`` uses Ollama's structured-output support to constrain decoding to
    a JSON shape. Gemma 3n will otherwise occasionally emit its tokenizer's
    space glyph for indentation or misspell a key, which no amount of prompt
    wording reliably prevents."""
    model = model or config.LOCAL_CHAT_MODEL
    payload = {
        "model": model,
        "prompt": user,
        "system": system,
        "stream": False,
        "options": options,
    }
    if schema:
        payload["format"] = schema
    started = time.perf_counter()
    try:
        result = _post(f"{config.OLLAMA_HOST}/api/generate", payload)
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", "replace")[:400]
        raise ModelUnavailable(f"Local model call failed ({exc.code}): {detail}") from exc
    except (urllib.error.URLError, OSError) as exc:
        raise ModelUnavailable(
            f"Local model call to {config.OLLAMA_HOST} failed: {exc}.\n"
            "  Is `ollama serve` running? `wiki doctor` will check."
        ) from exc
    return Completion(
        text=detokenise(result.get("response") or "").strip(),
        model=model,
        mode="local",
        seconds=time.perf_counter() - started,
        prompt_tokens=result.get("prompt_eval_count", 0),
        completion_tokens=result.get("eval_count", 0),
        options=options,
    )


def embed_local(texts: list[str], model: str | None = None) -> list[list[float]]:
    """Embed a batch of strings with the local embedding model."""
    model = model or config.LOCAL_EMBED_MODEL
    try:
        result = _post(
            f"{config.OLLAMA_HOST}/api/embed",
            {"model": model, "input": texts},
            timeout=600,
        )
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", "replace")[:400]
        raise ModelUnavailable(
            f"Local embedding call failed ({exc.code}): {detail}\n"
            f"  Pull the embedding model while online:  ollama pull {model}"
        ) from exc
    except (urllib.error.URLError, OSError) as exc:
        raise ModelUnavailable(f"Local embedding call failed: {exc}") from exc
    return result["embeddings"]


# --------------------------------------------------------------------------
# Optional online extension
# --------------------------------------------------------------------------

def generate_online(system: str, user: str, options: dict) -> Completion:
    api_key = os.environ.get(config.ONLINE_API_KEY_ENV)
    if not api_key:
        raise ModelUnavailable(
            f"--mode online needs {config.ONLINE_API_KEY_ENV} in the environment.\n"
            "  Local mode is the default and needs no key."
        )
    model = config.ONLINE_CHAT_MODEL
    url = config.ONLINE_ENDPOINT.format(model=model) + f"?key={api_key}"
    payload = {
        "system_instruction": {"parts": [{"text": system}]},
        "contents": [{"role": "user", "parts": [{"text": user}]}],
        "generationConfig": {
            "temperature": options.get("temperature", 0.2),
            "maxOutputTokens": options.get("num_predict", 400),
        },
    }
    started = time.perf_counter()
    result = _post(url, payload)
    parts = result["candidates"][0]["content"]["parts"]
    usage = result.get("usageMetadata", {})
    return Completion(
        text=detokenise("".join(p.get("text", "") for p in parts)).strip(),
        model=model,
        mode="online",
        seconds=time.perf_counter() - started,
        prompt_tokens=usage.get("promptTokenCount", 0),
        completion_tokens=usage.get("candidatesTokenCount", 0),
        options=options,
    )


def generate(
    system: str, user: str, options: dict, mode: str = "local", schema: dict | None = None
) -> Completion:
    """Single entry point the rest of the harness uses. Local is the default."""
    if mode == "online":
        return generate_online(system, user, options)
    require_local_model(config.LOCAL_CHAT_MODEL)
    return generate_local(system, user, options, schema=schema)
