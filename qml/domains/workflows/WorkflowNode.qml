import QtQuick
import QtQuick.Controls
import themes 1.0

/**
 * Planungstafel-Knoten: Rolle, Titel, Ports, Drag, Hover, Auswahl.
 */
Item {
    id: root
    required property string nodeId
    required property string title
    required property string roleKey
    required property real posX
    required property real posY
    required property bool isSelected
    property var vm

    width: 168
    height: 80

    onPosXChanged: root.x = posX
    onPosYChanged: root.y = posY
    Component.onCompleted: {
        root.x = posX
        root.y = posY
    }

    readonly property bool _sel: isSelected

    readonly property color _roleTint: {
        switch (roleKey) {
        case "agent":
            return Theme.colors.accentPrimary
        case "prompt":
            return "#6366f1"
        case "tool":
            return "#a855f7"
        case "model":
            return "#0ea5e9"
        case "memory":
            return "#14b8a6"
        case "condition":
            return "#f59e0b"
        case "start":
            return "#22c55e"
        case "end":
            return "#64748b"
        default:
            return Theme.divider.borderSoft
        }
    }

    Rectangle {
        id: card
        anchors.fill: parent
        radius: Theme.radius.md
        color: Theme.surfaces.panelSide
        border.width: root._sel ? 2 : (dragArea.containsPress ? 1 : 1)
        border.color: root._sel ? Theme.states.focusRing : (dragArea.containsMouse ? Theme.colors.accentSecondary : Theme.divider.borderSoft)

        Column {
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.top: parent.top
            anchors.margins: Theme.spacing.sm
            spacing: 2
            Label {
                text: {
                    switch (roleKey) {
                    case "agent":
                        return qsTr("Agent")
                    case "prompt":
                        return qsTr("Prompt")
                    case "tool":
                        return qsTr("Tool")
                    case "model":
                        return qsTr("Modell")
                    case "memory":
                        return qsTr("Memory")
                    case "condition":
                        return qsTr("Bedingung")
                    case "start":
                        return qsTr("Start")
                    case "end":
                        return qsTr("Ende")
                    default:
                        return roleKey
                    }
                }
                font.pixelSize: Theme.typography.caption.pixelSize
                color: root._roleTint
                elide: Text.ElideRight
            }
            Label {
                text: title
                font.pixelSize: Theme.typography.body.pixelSize
                font.bold: true
                color: Theme.colors.textPrimary
                elide: Text.ElideRight
                width: parent.width
            }
            Label {
                text: nodeId
                font.pixelSize: Theme.typography.caption.pixelSize - 1
                color: Theme.colors.textSecondary
                elide: Text.ElideMiddle
                width: parent.width
            }
        }

        Rectangle {
            width: 8
            height: 8
            radius: 4
            color: Theme.surfaces.architectural
            border.width: 1
            border.color: Theme.divider.borderSoft
            anchors.verticalCenter: parent.verticalCenter
            anchors.left: parent.left
            anchors.leftMargin: -4
        }
        Rectangle {
            width: 8
            height: 8
            radius: 4
            color: Theme.surfaces.architectural
            border.width: 1
            border.color: Theme.divider.borderSoft
            anchors.verticalCenter: parent.verticalCenter
            anchors.right: parent.right
            anchors.rightMargin: -4
        }

        MouseArea {
            id: dragArea
            anchors.fill: parent
            hoverEnabled: true
            acceptedButtons: Qt.LeftButton
            drag.target: root
            drag.axis: Drag.XAndYAxis
            drag.minimumX: 0
            drag.minimumY: 0
            drag.maximumX: 10000
            drag.maximumY: 10000
            onClicked: {
                if (vm)
                    vm.selectNode(nodeId)
            }
            onReleased: {
                if (vm && (drag.active || true))
                    vm.moveNode(nodeId, root.x, root.y)
            }
        }
    }
}
