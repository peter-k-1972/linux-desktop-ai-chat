import QtQuick

/** Semantische Interaktionswerte — visuelles Minimum für Slice 0–2. */
QtObject {
    required property var palette

    readonly property color focusRing: palette.focus
    readonly property int focusRingWidth: 2

    readonly property real disabledOpacity: 0.45
    readonly property real hoverLighten: 0.06
    readonly property real pressedDarken: 0.08

    readonly property color selectedFill: palette.selectionBackground
    readonly property color selectedText: palette.selectionText

    readonly property color busyIndicator: palette.accentSecondary
    readonly property color error: palette.danger
    readonly property color warning: palette.warning
    readonly property color success: palette.success
    readonly property color info: palette.info
}
