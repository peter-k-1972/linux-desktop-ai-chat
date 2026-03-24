import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import themes 1.0

/**
 * MITTE: Aufgaben und letzte Aktivitäten.
 */
Rectangle {
    id: root
    color: Theme.surfaces.work
    radius: Theme.radiusMd
    border.width: 1
    border.color: Theme.divider.borderSoft

    property var vm

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: Theme.spacing.md
        spacing: Theme.spacing.md

        Label {
            text: qsTr("Schreibtisch")
            font.pixelSize: Theme.fontSizeTitle
            font.bold: true
            color: Theme.colors.textPrimary
            Layout.fillWidth: true
        }

        Label {
            text: qsTr("Auftrag an den gewählten Bibliothekar")
            font.pixelSize: Theme.typography.caption.pixelSize
            color: Theme.colors.textSecondary
            Layout.fillWidth: true
        }

        RowLayout {
            Layout.fillWidth: true
            spacing: Theme.spacing.sm

            TextField {
                id: taskField
                Layout.fillWidth: true
                placeholderText: qsTr("Aufgabe beschreiben …")
                enabled: vm && vm.selectedAgent && vm.selectedAgent.agentId.length > 0
            }

            Button {
                text: qsTr("Senden")
                enabled: taskField.text.length > 0 && vm && vm.selectedAgent && vm.selectedAgent.agentId.length > 0
                onClicked: {
                    if (vm) {
                        vm.dispatchTask(taskField.text);
                        taskField.text = "";
                    }
                }
            }
        }

        Label {
            text: qsTr("Aktuelle Aufgaben")
            font.pixelSize: Theme.fontSizeSmall
            font.bold: true
            color: Theme.colors.textPrimary
            Layout.fillWidth: true
        }

        ListView {
            id: taskList
            Layout.fillWidth: true
            Layout.preferredHeight: Math.min(220, Math.max(80, contentHeight))
            clip: true
            spacing: Theme.spacing.xs
            model: vm ? vm.tasks : null

            delegate: Rectangle {
                required property string taskId
                required property string title
                required property string state
                required property string agentLabel
                required property string timeLabel

                width: taskList.width
                height: taskRow.implicitHeight + Theme.spacing.sm * 2
                radius: Theme.radiusSm
                color: Theme.canvasElevated
                border.width: 1
                border.color: Theme.borderSubtle

                ColumnLayout {
                    id: taskRow
                    anchors.left: parent.left
                    anchors.right: parent.right
                    anchors.verticalCenter: parent.verticalCenter
                    anchors.leftMargin: Theme.spacing.sm
                    anchors.rightMargin: Theme.spacing.sm
                    spacing: Theme.spacing.xs

                    Label {
                        text: title
                        font.pixelSize: Theme.typography.body.pixelSize
                        color: Theme.colors.textPrimary
                        wrapMode: Text.Wrap
                        Layout.fillWidth: true
                    }
                    Label {
                        text: qsTr("%1 · %2 · %3").arg(agentLabel).arg(state).arg(timeLabel)
                        font.pixelSize: Theme.typography.caption.pixelSize
                        color: Theme.colors.textSecondary
                        Layout.fillWidth: true
                        elide: Text.ElideRight
                    }
                }
            }
        }

        Label {
            text: qsTr("Letzte Aktivitäten")
            font.pixelSize: Theme.fontSizeSmall
            font.bold: true
            color: Theme.colors.textPrimary
            Layout.fillWidth: true
        }

        ListView {
            id: actList
            Layout.fillWidth: true
            Layout.fillHeight: true
            clip: true
            spacing: Theme.spacing.xs
            model: vm ? vm.activityFeed : null

            delegate: RowLayout {
                required property string message
                required property string timeLabel

                width: actList.width
                spacing: Theme.spacing.sm

                Label {
                    text: timeLabel
                    font.pixelSize: Theme.typography.caption.pixelSize
                    color: Theme.colors.textSecondary
                    Layout.preferredWidth: 48
                }
                Label {
                    text: message
                    font.pixelSize: Theme.fontSizeSmall
                    color: Theme.colors.textPrimary
                    wrapMode: Text.Wrap
                    Layout.fillWidth: true
                }
            }
        }
    }
}
