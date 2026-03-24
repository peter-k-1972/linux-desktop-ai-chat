import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import themes 1.0

/**
 * RECHTS: Skills, Kontext, Konfiguration.
 */
Rectangle {
    id: root
    color: Theme.canvasElevated
    radius: Theme.radiusMd
    border.width: 1
    border.color: Theme.borderSubtle

    property var vm

    ScrollView {
        anchors.fill: parent
        anchors.margins: Theme.spacing.sm
        clip: true

        ColumnLayout {
            width: parent.width
            spacing: Theme.spacing.md

            Label {
                text: qsTr("Inspektor")
                font.pixelSize: Theme.fontSizeSmall
                font.bold: true
                color: Theme.textOnDark
                Layout.fillWidth: true
            }

            Label {
                visible: !vm || !vm.selectedAgent || vm.selectedAgent.agentId.length === 0
                text: qsTr("Wählen Sie einen Agenten in der Dienstliste.")
                font.pixelSize: Theme.fontSizeSmall
                color: Theme.colors.textSecondary
                wrapMode: Text.Wrap
                Layout.fillWidth: true
            }

            ColumnLayout {
                visible: vm && vm.selectedAgent && vm.selectedAgent.agentId.length > 0
                Layout.fillWidth: true
                spacing: Theme.spacing.md

                Label {
                    text: vm && vm.selectedAgent ? vm.selectedAgent.name : ""
                    font.pixelSize: Theme.typography.domainTitle.pixelSize
                    font.bold: true
                    color: Theme.colors.textPrimary
                    wrapMode: Text.Wrap
                    Layout.fillWidth: true
                }

                Label {
                    text: qsTr("Rolle · Modell · Status")
                    font.pixelSize: Theme.typography.caption.pixelSize
                    color: Theme.colors.textSecondary
                    Layout.fillWidth: true
                }
                Label {
                    text: vm && vm.selectedAgent
                        ? qsTr("%1 · %2 · %3").arg(vm.selectedAgent.role).arg(vm.selectedAgent.model).arg(vm.selectedAgent.status)
                        : ""
                    font.pixelSize: Theme.fontSizeSmall
                    color: Theme.colors.textPrimary
                    wrapMode: Text.Wrap
                    Layout.fillWidth: true
                }

                Label {
                    text: qsTr("Skills")
                    font.pixelSize: Theme.fontSizeSmall
                    font.bold: true
                    color: Theme.colors.textPrimary
                    Layout.fillWidth: true
                }
                TextArea {
                    Layout.fillWidth: true
                    Layout.preferredHeight: 120
                    readOnly: true
                    wrapMode: TextArea.Wrap
                    text: vm && vm.selectedAgent ? vm.selectedAgent.skillsText : ""
                    background: Rectangle {
                        color: Theme.surfaceMuted
                        radius: Theme.radiusSm
                        border.width: 1
                        border.color: Theme.borderSubtle
                    }
                }

                Label {
                    text: qsTr("Kontext")
                    font.pixelSize: Theme.fontSizeSmall
                    font.bold: true
                    color: Theme.colors.textPrimary
                    Layout.fillWidth: true
                }
                TextArea {
                    Layout.fillWidth: true
                    Layout.preferredHeight: 140
                    readOnly: true
                    wrapMode: TextArea.Wrap
                    text: vm && vm.selectedAgent ? vm.selectedAgent.contextText : ""
                    background: Rectangle {
                        color: Theme.surfaceMuted
                        radius: Theme.radiusSm
                        border.width: 1
                        border.color: Theme.borderSubtle
                    }
                }

                Label {
                    text: qsTr("Konfiguration")
                    font.pixelSize: Theme.fontSizeSmall
                    font.bold: true
                    color: Theme.colors.textPrimary
                    Layout.fillWidth: true
                }
                TextArea {
                    Layout.fillWidth: true
                    Layout.preferredHeight: 120
                    readOnly: true
                    wrapMode: TextArea.Wrap
                    text: vm && vm.selectedAgent ? vm.selectedAgent.configurationText : ""
                    background: Rectangle {
                        color: Theme.surfaceMuted
                        radius: Theme.radiusSm
                        border.width: 1
                        border.color: Theme.borderSubtle
                    }
                }
            }
        }
    }
}
