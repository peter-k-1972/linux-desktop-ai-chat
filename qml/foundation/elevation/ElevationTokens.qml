import QtQuick

/**
 * Semantische Tiefenstufen — pragmatisch (Luminanz + dezente Schattenparameter).
 */
QtObject {
    required property var palette

    readonly property QtObject base: QtObject {
        readonly property int z: 0
        readonly property color ambientShadow: palette.transparent
        readonly property real shadowOpacity: 0
        readonly property int shadowOffsetY: 0
        readonly property int shadowBlur: 0
    }
    readonly property QtObject raised: QtObject {
        readonly property int z: 1
        readonly property color ambientShadow: "#000000"
        readonly property real shadowOpacity: 0.14
        readonly property int shadowOffsetY: 2
        readonly property int shadowBlur: 12
    }
    readonly property QtObject overlay: QtObject {
        readonly property int z: 2
        readonly property color ambientShadow: "#000000"
        readonly property real shadowOpacity: 0.22
        readonly property int shadowOffsetY: 6
        readonly property int shadowBlur: 24
    }
    readonly property QtObject modal: QtObject {
        readonly property int z: 3
        readonly property color ambientShadow: "#000000"
        readonly property real shadowOpacity: 0.28
        readonly property int shadowOffsetY: 10
        readonly property int shadowBlur: 32
    }
}
