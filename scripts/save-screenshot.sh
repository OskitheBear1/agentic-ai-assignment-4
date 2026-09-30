#!/usr/bin/env bash
# Move the screenshot you just took into evidence/screenshots/ under the right name.
#
#   ./scripts/save-screenshot.sh note-with-sources
#   ./scripts/save-screenshot.sh index-and-page-list
#   ./scripts/save-screenshot.sh graph-view
#
# It finds the newest .png in wherever macOS is configured to drop screenshots
# (this machine: ~/Documents/UC Berkeley Haas MBA/2027/CS160), falling back to
# ~/Desktop, so you never have to go looking for the file.
set -uo pipefail
cd "$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

name="${1:-}"
case "$name" in
  note-with-sources|note-related-links|index-and-page-list|graph-view) ;;
  *)
    echo "usage: ./scripts/save-screenshot.sh <name>"
    echo "  where <name> is one of:"
    echo "    note-with-sources      (note header: filename, H1, Properties/source metadata)"
    echo "    note-related-links     (same note scrolled down: Source Reference + Related Notes)"
    echo "    index-and-page-list    (index.md beside the file list)"
    echo "    graph-view             (graph, labels readable)"
    exit 1 ;;
esac

dest="evidence/screenshots/${name}.png"
mkdir -p evidence/screenshots

# Where does macOS put screenshots on this machine?
configured="$(defaults read com.apple.screencapture location 2>/dev/null || true)"
configured="${configured/#\~/$HOME}"

newest=""
for dir in "$configured" "$HOME/Desktop"; do
  [[ -n "$dir" && -d "$dir" ]] || continue
  while IFS= read -r candidate; do
    [[ -n "$candidate" ]] || continue
    if [[ -z "$newest" || "$candidate" -nt "$newest" ]]; then newest="$candidate"; fi
  done < <(find "$dir" -maxdepth 1 -name "*.png" -mmin -20 2>/dev/null)
done

if [[ -z "$newest" ]]; then
  echo "No screenshot from the last 20 minutes found in:"
  [[ -n "$configured" ]] && echo "  $configured"
  echo "  $HOME/Desktop"
  echo
  echo "Take the screenshot first (Cmd-Shift-4, then drag over the window), then re-run this."
  exit 1
fi

echo "Found:  $newest"
if [[ -f "$dest" ]]; then
  echo "Note:   $dest already exists and will be replaced."
fi
mv "$newest" "$dest"
size="$(/usr/bin/stat -f%z "$dest")"
dims="$(/usr/bin/sips -g pixelWidth -g pixelHeight "$dest" 2>/dev/null | awk '/pixel/{print $2}' | paste -sd'x' -)"
echo "Saved:  $dest  (${dims}px, $((size/1024)) KB)"
if [[ "$size" -lt 40000 ]]; then
  echo "WARNING: that file is small. Make sure the labels are actually legible,"
  echo "         and that you captured the window rather than a thin strip."
fi

echo
echo "Progress:"
for want in note-with-sources note-related-links index-and-page-list graph-view; do
  if [[ -f "evidence/screenshots/${want}.png" ]]; then echo "  [x] ${want}.png"; else echo "  [ ] ${want}.png"; fi
done
