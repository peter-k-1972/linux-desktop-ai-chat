import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import themes 1.0

/**
 * Rechte Spalte: Beschreibung, Kontextregeln, Standard-Kontextmodus.
 */
Rectangle {
    id: root
    property var vm: null

    color: Theme.surfaces.panelSide
    radius: Theme.radius.md
    border.width: 1
    border.color: Theme.divider.borderSoft

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: Theme.spacing.sm
        spacing: Theme.spacing.sm

        Label {
            text: qsTr("Projekt-Inspector")
            font.bold: true
            font.pixelSize: Theme.typography.domainTitle.pixelSize
            color: Theme.colors.textPrimary
            Layout.fillWidth: true
        }

        ScrollView {
            Layout.fillWidth: true
            Layout.fillHeight: true
            clip: true

            ColumnLayout {
                width: parent.width
                spacing: Theme.spacing.md

                Label {
                    text: qsTr("Beschreibung")
                    font.bold: true
                    font.pixelSize: Theme.typography.body.pixelSize
                    color: Theme.colors.textSecondary
                    Layout.fillWidth: true
                }
                Label {
                    text: vm && vm.selectedProjectId >= 0 ? vm.description : qsTr("—")
                    wrapMode: Text.Wrap
                    color: Theme.colors.textPrimary
                    Layout.fillWidth: true
                }

                Label {
                    text: qsTr("Kontextregeln")
                    font.bold: true
                    font.pixelSize: Theme.typography.body.pixelSize
                    color: Theme.colors.textSecondary
                    Layout.fillWidth: true
                }
                Label {
                    text: vm && vm.selectedProjectId >= 0 ? vm.contextRules : qsTr("—")
                    wrapMode: Text.Wrap
                    color: Theme.colors.textPrimary
                    Layout.fillWidth: true
                }

                Label {
                    text: qsTr("Standard-Kontextmodus")
                    font.bold: true
                    font.pixelSize: Theme.typography.body.pixelSize
                    color: Theme.colors.textSecondary
                    Layout.fillWidth: true
                }
                Label {
                    text: vm && vm.selectedProjectId >= 0 ? vm.defaultContextMode : qsTr("—")
                    wrapMode: Text.Wrap
                    color: Theme.colors.textPrimary
                    Layout.fillWidth: true
                }

                Item {
                    Layout.fillHeight: true
                    Layout.minimumHeight: Theme.spacing.md
                }
            }
        }
    }
}
