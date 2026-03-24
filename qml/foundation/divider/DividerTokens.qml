import QtQuick

/** Trennlinien — Farben referenzieren Palette über required property. */
QtObject {
    required property var palette

    readonly property color line: palette.divider
    readonly property color borderSoft: palette.borderSoft
    readonly property color borderStrong: palette.borderStrong
    readonly property real lineOpacity: 0.35
}
