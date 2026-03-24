import QtQuick
import QtQuick.Controls
import themes 1.0

/**
 * Scrollbare Planungstfläche mit Zoom (Rad) und Pinch.
 */
Item {
    id: root
    property var vm

    property real zoom: 1.0
    readonly property real _zmin: 0.35
    readonly property real _zmax: 2.5

    Rectangle {
        anchors.fill: parent
        color: Theme.colors.appBackground
        border.width: 1
        border.color: Theme.divider.borderSoft
        radius: Theme.radius.md
    }

    Flickable {
        id: flick
        anchors.fill: parent
        anchors.margins: Theme.spacing.sm
        contentWidth: 4200
        contentHeight: 3400
        clip: true
        boundsBehavior: Flickable.StopAtBounds
        flickableDirection: Flickable.HorizontalAndVerticalFlick

        Item {
            id: world
            width: flick.contentWidth
            height: flick.contentHeight
            transform: Scale {
                origin.x: 0
                origin.y: 0
                xScale: root.zoom
                yScale: root.zoom
            }

            Rectangle {
                anchors.fill: parent
                color: Theme.surfaces.architectural
                opacity: 0.4
                border.color: Theme.divider.borderSoft
                border.width: 1
                radius: Theme.radius.sm
            }

            Label {
                x: Theme.spacing.lg
                y: Theme.spacing.lg
                text: qsTr("Prozessdiagramm — Forschungsraum")
                font.pixelSize: Theme.typography.caption.pixelSize
                color: Theme.colors.textSecondary
            }

            WorkflowGraph {
                anchors.fill: parent
                anchors.margins: Theme.spacing.md
                vm: root.vm
            }
        }
    }

    WheelHandler {
        target: null
        onWheel: function (event) {
            const dy = event.angleDelta.y
            if (dy > 0)
                root.zoom = Math.min(root._zmax, root.zoom * 1.09)
            else if (dy < 0)
                root.zoom = Math.max(root._zmin, root.zoom / 1.09)
            event.accepted = true
        }
    }

    Label {
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        anchors.margins: Theme.spacing.md
        text: qsTr("Zoom %1%").arg(Math.round(root.zoom * 100))
        font.pixelSize: Theme.typography.caption.pixelSize
        color: Theme.colors.textSecondary
    }
}
