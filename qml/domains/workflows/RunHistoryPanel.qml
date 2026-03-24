import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import themes 1.0

/**
 * Untere Leiste: letzte Runs, Status, Dauer.
 */
Rectangle {
    id: root
    property var vm

    color: Theme.surfaces.panelSide
    border.color: Theme.divider.borderSoft
    border.width: 1
    radius: Theme.radius.md

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: Theme.spacing.sm
        spacing: Theme.spacing.xs

        Label {
            text: qsTr("Run-Historie")
            font.bold: true
            font.pixelSize: Theme.typography.body.pixelSize
            color: Theme.colors.textPrimary
            Layout.fillWidth: true
        }

        RowLayout {
            Layout.fillWidth: true
            spacing: Theme.spacing.md
            Label {
                text: qsTr("Run-ID")
                font.bold: true
                font.pixelSize: Theme.typography.caption.pixelSize
                color: Theme.colors.textSecondary
                Layout.preferredWidth: 220
            }
            Label {
                text: qsTr("Status")
                font.bold: true
                font.pixelSize: Theme.typography.caption.pixelSize
                color: Theme.colors.textSecondary
                Layout.preferredWidth: 100
            }
            Label {
                text: qsTr("Dauer")
                font.bold: true
                font.pixelSize: Theme.typography.caption.pixelSize
                color: Theme.colors.textSecondary
                Layout.preferredWidth: 80
            }
            Label {
                text: qsTr("Start")
                font.bold: true
                font.pixelSize: Theme.typography.caption.pixelSize
                color: Theme.colors.textSecondary
                Layout.fillWidth: true
            }
        }

        Rectangle {
            Layout.fillWidth: true
            height: 1
            color: Theme.divider.borderSoft
        }

        ListView {
            id: runList
            Layout.fillWidth: true
            Layout.fillHeight: true
            clip: true
            model: vm ? vm.runs : null
            spacing: 0

            delegate: Rectangle {
                required property int index
                required property string runId
                required property string status
                required property string duration
                required property string started

                width: runList.width
                height: 32
                color: index % 2 === 0 ? Theme.colors.transparent : Theme.surfaces.architectural
                opacity: 0.35

                RowLayout {
                    anchors.fill: parent
                    anchors.leftMargin: Theme.spacing.xs
                    anchors.rightMargin: Theme.spacing.xs
                    Label {
                        text: runId
                        font.pixelSize: Theme.typography.caption.pixelSize
                        color: Theme.colors.textPrimary
                        elide: Text.ElideMiddle
                        Layout.preferredWidth: 220
                    }
                    Label {
                        text: status
                        font.pixelSize: Theme.typography.caption.pixelSize
                        color: Theme.colors.textPrimary
                        Layout.preferredWidth: 100
                    }
                    Label {
                        text: duration
                        font.pixelSize: Theme.typography.caption.pixelSize
                        color: Theme.colors.textPrimary
                        Layout.preferredWidth: 80
                    }
                    Label {
                        text: started
                        font.pixelSize: Theme.typography.caption.pixelSize
                        color: Theme.colors.textSecondary
                        Layout.fillWidth: true
                        elide: Text.ElideRight
                    }
                }
            }
        }
    }
}
