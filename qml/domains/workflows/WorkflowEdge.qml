import QtQuick
import QtQuick.Shapes
import themes 1.0

/**
 * Bezier-Kante zwischen Ports (Datenfluss / Kontrollfluss).
 */
Shape {
    id: root
    required property real sx
    required property real sy
    required property real tx
    required property real ty
    required property string flowKind
    required property string edgeId

    readonly property bool _control: flowKind === "control"
    readonly property color _stroke: _control ? "#ea580c" : "#0d9488"

    antialiasing: true
    containsMode: Shape.FillContains

    ShapePath {
        strokeWidth: 2
        strokeColor: root._stroke
        fillColor: "transparent"
        capStyle: ShapePath.RoundCap
        joinStyle: ShapePath.RoundJoin
        strokeStyle: root._control ? ShapePath.DashLine : ShapePath.SolidLine
        dashPattern: [6, 4]
        startX: root.sx
        startY: root.sy
        PathCubic {
            x: root.tx
            y: root.ty
            control1X: root.sx + (root.tx - root.sx) * 0.55
            control1Y: root.sy
            control2X: root.sx + (root.tx - root.sx) * 0.45
            control2Y: root.ty
        }
    }
}
