import QtQuick

/**
 * Räumliche Surface-Rollen — Werte aus SemanticColors, semantisch benannt.
 */
QtObject {
    required property var palette

    readonly property color architectural: palette.appBackground
    readonly property color ambient: palette.ambientLayer
    readonly property color work: palette.workSurface
    readonly property color readingPaper: palette.paperSurface
    readonly property color panelSide: palette.sideSurface
    readonly property color overlay: palette.overlaySurface
    readonly property color selected: palette.selectionBackground
    readonly property color subtleHighlight: palette.subtleHighlightSurface
}
