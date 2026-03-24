import QtQuick

/**
 * Primitive semantic palette — library atmosphere (warm dark shell, paper work).
 * Single source of truth for hex values; surfaces and legacy Theme aliases map here.
 */
QtObject {
    readonly property color transparent: "#00000000"

    readonly property color appBackground: "#1e1c19"
    readonly property color roomBackground: "#222019"
    readonly property color ambientLayer: "#252220"

    readonly property color workSurface: "#ede8df"
    readonly property color paperSurface: "#ede8df"
    readonly property color sideSurface: "#2a2622"
    readonly property color overlaySurface: "#2f2b26"

    readonly property color textPrimary: "#1a1815"
    readonly property color textSecondary: "#5c564c"
    readonly property color textMuted: "#7a7268"
    readonly property color textOnDarkPrimary: "#e8e4dc"
    readonly property color textOnDarkSecondary: "#c4bfb4"

    readonly property color accentPrimary: "#b8935c"
    readonly property color accentSecondary: "#3d6b6e"

    readonly property color focus: "#b8935c"
    readonly property color selectionBackground: "#3a342e"
    readonly property color selectionText: "#f2efe6"

    readonly property color divider: "#4a4540"
    readonly property color borderSoft: "#4a4540"
    readonly property color borderStrong: "#6a6358"

    readonly property color success: "#5a8f6e"
    readonly property color warning: "#c9a227"
    readonly property color danger: "#c45c4a"
    readonly property color info: "#4a7d8c"

    readonly property color subtleHighlightSurface: "#e3ddd2"
    readonly property color surfaceMutedTray: "#dbd4c8"
}
