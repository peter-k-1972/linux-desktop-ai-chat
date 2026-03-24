import QtQuick
import QtQuick.Layouts
import themes 1.0

Item {
    id: root
    anchors.fill: parent

    property var shellBridge

    RowLayout {
        id: chromeRow
        anchors.fill: parent
        spacing: 0

        NavRail {
            id: rail
            Layout.preferredWidth: Theme.sizing.navWidthPreferred
            Layout.fillHeight: true
            shellBridge: root.shellBridge
        }

        Rectangle {
            Layout.preferredWidth: 1
            Layout.fillHeight: true
            color: Theme.divider.line
            opacity: Theme.divider.lineOpacity
        }

        StageHost {
            id: stage
            Layout.fillWidth: true
            Layout.fillHeight: true
            shellBridge: root.shellBridge
        }
    }

    OverlayHost {
        anchors.fill: parent
    }
}
