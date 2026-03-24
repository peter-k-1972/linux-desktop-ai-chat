import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import themes 1.0

/**
 * RECHTS: Fertige Artefakte (freigegebene Releases).
 */
Rectangle {
    id: root
    color: Theme.canvasElevated
    radius: Theme.radiusMd
    border.width: 1
    border.color: Theme.borderSubtle

    property var vm

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: Theme.spacing.md
        spacing: Theme.spacing.sm

        Label {
            text: qsTr("Artefaktregal")
            font.pixelSize: Theme.fontSizeSmall
            font.bold: true
            color: Theme.textOnDark
            Layout.fillWidth: true
        }

        Label {
            text: qsTr("Chains · Agentpakete · Modelle (ready)")
            font.pixelSize: Theme.typography.caption.pixelSize
            color: Theme.colors.textSecondary
            wrapMode: Text.Wrap
            Layout.fillWidth: true
        }

        ListView {
            id: rackList
            Layout.fillWidth: true
            Layout.fillHeight: true
            clip: true
            spacing: Theme.spacing.xs
            model: vm ? vm.artifacts : null

            delegate: Rectangle {
                required property string title
                required property string subtitle
                required property string releaseId

                width: rackList.width
                height: innerCol.implicitHeight + Theme.spacing.sm * 2
                radius: Theme.radiusSm
                color: Theme.surfaceWork
                border.width: 1
                border.color: Theme.borderSubtle

                ColumnLayout {
                    id: innerCol
                    anchors.left: parent.left
                    anchors.right: parent.right
                    anchors.verticalCenter: parent.verticalCenter
                    anchors.leftMargin: Theme.spacing.sm
                    anchors.rightMargin: Theme.spacing.sm
                    spacing: Theme.spacing.xs

                    Label {
                        text: title
                        font.pixelSize: Theme.fontSizeSmall
                        font.bold: true
                        color: Theme.colors.textPrimary
                        wrapMode: Text.Wrap
                        Layout.fillWidth: true
                    }
                    Label {
                        text: subtitle
                        font.pixelSize: Theme.typography.caption.pixelSize
                        color: Theme.colors.textSecondary
                        wrapMode: Text.Wrap
                        Layout.fillWidth: true
                    }
                    Label {
                        text: releaseId
                        font.pixelSize: Theme.typography.caption.pixelSize
                        color: Theme.colors.textSecondary
                        elide: Text.ElideMiddle
                        Layout.fillWidth: true
                    }
                }
            }
        }
    }
}
