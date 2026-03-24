import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import themes 1.0

/**
 * LINKS: Liste aller Agenten (Name, Rolle, Modell, Status).
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
        anchors.margins: Theme.spacing.sm
        spacing: Theme.spacing.sm

        RowLayout {
            Layout.fillWidth: true
            spacing: Theme.spacing.sm

            Label {
                text: qsTr("Dienstliste")
                font.pixelSize: Theme.fontSizeSmall
                font.bold: true
                color: Theme.textOnDark
                Layout.fillWidth: true
            }

            Button {
                text: qsTr("Aktualisieren")
                flat: true
                onClicked: {
                    if (vm) {
                        vm.reload_roster();
                    }
                }
            }
        }

        ListView {
            id: rosterList
            Layout.fillWidth: true
            Layout.fillHeight: true
            clip: true
            spacing: Theme.spacing.xs
            model: vm ? vm.agents : null

            delegate: AgentCard {
                width: rosterList.width
                selected: model.isSelected === true
                nameText: model.name || ""
                roleText: model.role || ""
                modelText: model.assignedModel || ""
                statusText: model.status || ""

                MouseArea {
                    anchors.fill: parent
                    cursorShape: Qt.PointingHandCursor
                    onClicked: {
                        if (vm) {
                            vm.selectAgent(model.agentId || "");
                        }
                    }
                }
            }
        }
    }
}
