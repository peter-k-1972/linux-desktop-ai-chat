import QtQuick
import themes 1.0

/**
 * Zeichenfläche: Kanten unter Knoten, GPU-freundlich (Shape-CurveRenderer).
 */
Item {
    id: root
    property var vm

    layer.enabled: true
    layer.smooth: true

    Repeater {
        model: vm ? vm.edges : null
        delegate: WorkflowEdge {
            required property string edgeId
            required property real sx
            required property real sy
            required property real tx
            required property real ty
            required property string flowKind
            z: -1
        }
    }

    Repeater {
        model: vm ? vm.nodes : null
        delegate: WorkflowNode {
            required property string nodeId
            required property string title
            required property string roleKey
            required property real posX
            required property real posY
            required property bool isSelected
            vm: root.vm
            z: 0
        }
    }
}
