"""The CLI: parse the user's command, pick a mode, run the harness.

This is the top of the one path the README traces end to end:

    ./wiki ask "..."  ->  cli.main  ->  modes.ask.run  ->  retrieval.retrieve
                      ->  prompts.build_ask_prompt  ->  model.generate_local
                      ->  citations.check  ->  evidence.save_ask_card  ->  stdout
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

from . import config, index, model, vaultcheck
from .documents import repo_relative

EPILOG = """\
examples
  ./wiki doctor                                   check runtime, models, index
  ./wiki ingest ./vault/raw                       read sources, write notes, index
  ./wiki ingest "./vault/raw/Data Mining Syllabus.pdf"    one source only
  ./wiki reindex                                  rebuild the index, no model prose
  ./wiki search "participation points"            original passages, no answer
  ./wiki search "hedge funds" --no-vectors        keyword-only (works with model off)
  ./wiki ask "How many points is participation worth in Negotiations?"
  ./wiki ask "..." --top-k 8 --scope raw          tune retrieval for one question
  ./wiki chat                                     start the assistant
  ./wiki check                                    verify links and source references
  ./wiki test                                     run the four saved ask-mode evals

configuration
  instructions/persona.md            chat personality and capability description
  instructions/wiki-instructions.md  research rules used by ask mode
  instructions/ingest-instructions.md  the note contract used during ingestion
  environment: WIKI_MODEL, WIKI_EMBED_MODEL, WIKI_OLLAMA_HOST override defaults

layout
  vault/raw/    original sources, never modified
  vault/wiki/   generated + reviewed notes (open vault/ as the Obsidian vault)
  .wiki_index/  retrieval chunks, vectors, source catalog  (outside the vault)
  evidence/     saved runs: ask cards, mode checks, offline proof
"""


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="wiki",
        description="Personal course wiki: local Gemma + RAG over your own sources. "
                    "Local execution is the default and works with no network.",
        epilog=EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--version", action="version", version="wiki 1.0 (local-first)")
    subparsers = parser.add_subparsers(dest="command", metavar="<command>")

    def add_execution(sub: argparse.ArgumentParser) -> None:
        sub.add_argument(
            "--mode", dest="execution", choices=("local", "online"), default="local",
            help="where the model runs. local (default) needs no network.",
        )

    ingest = subparsers.add_parser("ingest", help="read sources, generate notes, rebuild index")
    ingest.add_argument("path", nargs="?", default=str(config.RAW_DIR),
                        help="file or directory of sources (default: vault/raw)")
    add_execution(ingest)

    reindex = subparsers.add_parser(
        "reindex", help="rebuild the retrieval index only (no note generation)")
    reindex.add_argument("--no-embed", action="store_true",
                         help="skip vectors; keyword-only index, no model needed")

    search = subparsers.add_parser("search", help="show original passages, no generated answer")
    search.add_argument("query", help="search terms")
    search.add_argument("-k", "--top-k", type=int, default=config.SEARCH_K)
    search.add_argument("--scope", choices=("all", "raw", "wiki"), default="all")
    search.add_argument("--no-vectors", action="store_true",
                        help="keyword (BM25) only; runs with the model stopped")
    search.add_argument("--full", action="store_true", help="print untruncated passages")
    search.add_argument("--save", action="store_true", help="write an evidence record")

    ask = subparsers.add_parser("ask", help="standalone factual answer with citations")
    ask.add_argument("question")
    ask.add_argument("-k", "--top-k", type=int, default=config.TOP_K)
    ask.add_argument("--scope", choices=("all", "raw", "wiki"), default="all")
    ask.add_argument("--no-save", action="store_true", help="do not write an evidence card")
    ask.add_argument("--test-id", help="label the saved evidence card, e.g. test-1")
    add_execution(ask)

    chat = subparsers.add_parser("chat", help="start the personal assistant")
    chat.add_argument("--quiet", action="store_true",
                      help="hide the retrieval decision line")
    add_execution(chat)

    subparsers.add_parser("doctor", help="check runtime, models, index and vault health")
    subparsers.add_parser("check", help="verify wiki links and source references")
    subparsers.add_parser("catalog", help="print the source catalog")

    test = subparsers.add_parser("test", help="run the saved ask-mode eval set")
    test.add_argument("--only", help="run one test id, e.g. test-3")
    add_execution(test)

    return parser


def cmd_doctor() -> int:
    print("\033[1mRUNTIME\033[0m")
    status = model.local_runtime_status()
    if status["reachable"]:
        print(f"  ollama              reachable at {config.OLLAMA_HOST} (v{status['version']})")
    else:
        print(f"  ollama              \033[31mUNREACHABLE\033[0m at {config.OLLAMA_HOST}")
        print(f"                      {status['error']}")
        print("                      start it: brew services start ollama")
    for label, name in (("generation model", config.LOCAL_CHAT_MODEL),
                        ("embedding model", config.LOCAL_EMBED_MODEL)):
        present = name in status["models"]
        mark = "installed" if present else "\033[31mMISSING\033[0m (ollama pull " + name + ")"
        print(f"  {label:<19} {name}  —  {mark}")

    print("\n\033[1mINDEX\033[0m")
    if config.CHUNKS_FILE.exists():
        passages = index.load_passages()
        vectors = index.load_vectors()
        raw = sum(1 for p in passages if p.source_type == "raw")
        print(f"  passages            {len(passages)} ({raw} raw, {len(passages) - raw} wiki)")
        print(f"  vectors             {len(vectors)}"
              + ("" if len(vectors) == len(passages) else "  \033[33m(stale — run reindex)\033[0m"))
        print(f"  chunks file         {repo_relative(config.CHUNKS_FILE)}")
    else:
        print("  \033[33mno index yet\033[0m — run: ./wiki ingest ./vault/raw")

    print("\n\033[1mVAULT\033[0m")
    raw_files = [p for p in config.RAW_DIR.glob("*") if p.is_file() and not p.name.startswith(".")]
    notes = sorted(config.WIKI_DIR.rglob("*.md"))
    print(f"  original sources    {len(raw_files)} in {repo_relative(config.RAW_DIR)}")
    print(f"  wiki notes          {len(notes)} in {repo_relative(config.WIKI_DIR)}")
    print(f"  index page          {'present' if config.INDEX_PAGE.exists() else 'MISSING'}")
    for name in ("persona.md", "wiki-instructions.md", "ingest-instructions.md"):
        path = config.INSTRUCTIONS_DIR / name
        print(f"  {name:<19} {'present' if path.exists() else '\033[31mMISSING\033[0m'}")

    print("\n\033[1mDISK\033[0m")
    usage = shutil.disk_usage(config.ROOT)
    print(f"  free space          {usage.free / 1e9:.0f} GB")
    return 0 if status["reachable"] else 1


def cmd_catalog() -> int:
    import json
    if not config.CATALOG_FILE.exists():
        print("No catalog yet. Run: ./wiki ingest ./vault/raw")
        return 1
    catalog = json.loads(config.CATALOG_FILE.read_text())
    print(f"\033[1mSOURCE CATALOG\033[0m  ({len(catalog)} entries)\n")
    print(f"{'machine id':<12} {'layer':<6} {'pgs':>4}  path")
    print("-" * 96)
    for entry in catalog:
        print(f"{entry['source_id']:<12} {entry['source_type']:<6} "
              f"{entry.get('pages', 0):>4}  {entry['source_path']}")
    print("\nThe machine id is a content hash of the file. It appears in each note's"
          "\nfront matter as `source_id`, which is how re-ingestion updates a note"
          "\nin place instead of creating a duplicate.")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not args.command:
        parser.print_help()
        return 0

    try:
        if args.command == "ingest":
            from . import ingest
            ingest.run(Path(args.path), execution_mode=args.execution)
            return 0

        if args.command == "reindex":
            config.ensure_dirs()
            print("\033[1mREINDEX\033[0m")
            stats = index.build(verbose=True, embed=not args.no_embed)
            print(f"  {stats['passages']} passages from {stats['sources']} sources, "
                  f"{stats['vectors']} vectors")
            return 0

        if args.command == "search":
            from .modes import search
            search.run(args.query, top_k=args.top_k, scope=args.scope,
                       use_vectors=not args.no_vectors, save=args.save, full=args.full)
            return 0

        if args.command == "ask":
            from .modes import ask
            record = ask.run(args.question, top_k=args.top_k, scope=args.scope,
                             execution_mode=args.execution, save=not args.no_save,
                             test_id=args.test_id)
            if record.get("evidence_card"):
                print(f"\033[2mevidence card: {record['evidence_card']}\033[0m")
            return 0

        if args.command == "chat":
            from .modes import chat
            chat.run(execution_mode=args.execution, verbose=not args.quiet)
            return 0

        if args.command == "doctor":
            return cmd_doctor()

        if args.command == "check":
            return vaultcheck.run()

        if args.command == "catalog":
            return cmd_catalog()

        if args.command == "test":
            from . import evals
            return evals.run(only=args.only, execution_mode=args.execution)

    except model.ModelUnavailable as exc:
        print(f"\033[31mmodel error:\033[0m {exc}", file=sys.stderr)
        return 2
    except (RuntimeError, ValueError, FileNotFoundError) as exc:
        print(f"\033[31merror:\033[0m {exc}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("\ninterrupted.", file=sys.stderr)
        return 130
    return 0
