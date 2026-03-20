#!/bin/bash
# Installiert den Desktop-Starter für Ollama Linux Desktop Chat
# - Startmenü: ~/.local/share/applications/
# - Optional: Desktop-Verknüpfung
# - Optional: Taskleiste (automatisch über .desktop)

set -e

PROJECT_DIR="$(cd "$(dirname "$(realpath "$0")")" && pwd)"
DESKTOP_SRC="$PROJECT_DIR/linux-desktop-chat.desktop"
APPS_DIR="$HOME/.local/share/applications"
DESKTOP_DEST="$APPS_DIR/linux-desktop-chat.desktop"
DESKTOP_DIR="$(xdg-user-dir DESKTOP 2>/dev/null || echo "$HOME/Desktop")"

# start.sh ausführbar machen
chmod +x "$PROJECT_DIR/start.sh"

# Projektpfad in .desktop einsetzen
DESKTOP_CONTENT=$(sed "s|PROJECT_DIR|$PROJECT_DIR|g" "$DESKTOP_SRC")

mkdir -p "$APPS_DIR"
echo "$DESKTOP_CONTENT" > "$DESKTOP_DEST"
chmod +x "$DESKTOP_DEST"

echo "✓ Startmenü: $DESKTOP_DEST installiert"

# Optional: Desktop-Verknüpfung
if [[ "$1" == "--desktop" ]] || [[ "$1" == "-d" ]]; then
    cp "$DESKTOP_DEST" "$DESKTOP_DIR/linux-desktop-chat.desktop"
    chmod +x "$DESKTOP_DIR/linux-desktop-chat.desktop"
    echo "✓ Desktop-Verknüpfung: $DESKTOP_DIR/linux-desktop-chat.desktop"
fi

# Desktop-Datenbank aktualisieren (damit neue Icons sofort erscheinen)
if command -v update-desktop-database &>/dev/null; then
    update-desktop-database "$APPS_DIR" 2>/dev/null || true
fi

echo ""
echo "Fertig! Du findest 'Linux Desktop Chat' jetzt im Startmenü."
echo "Für eine Desktop-Verknüpfung: ./install-desktop.sh --desktop"
