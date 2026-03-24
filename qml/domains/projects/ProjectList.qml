import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import themes 1.0

/**
 * Linke Spalte: Projekte mit Aktivität und Status.
 */
Rectangle {
    id: root
    property var vm: null

    readonly property string _deleteInformative: qsTr(
        "Chats bleiben erhalten, verlieren aber die Projektzuordnung. "
        + "Prompts, Agenten und Workflows werden global (ohne Projekt). "
        + "Der Knowledge-Unterordner des Projekts wird entfernt; "
        + "Dateien auf der Festplatte werden dabei nicht gelöscht.")

    color: Theme.surfaces.panelSide
    radius: Theme.radius.md
    border.width: 1
    border.color: Theme.divider.borderSoft

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: Theme.spacing.sm
        spacing: Theme.spacing.sm

        Label {
            text: qsTr("Projektliste")
            font.bold: true
            font.pixelSize: Theme.typography.domainTitle.pixelSize
            color: Theme.colors.textPrimary
            Layout.fillWidth: true
        }

        Label {
            visible: vm && vm.lastError.length > 0
            text: vm ? vm.lastError : ""
            wrapMode: Text.Wrap
            font.pixelSize: Theme.fontSizeSmall
            color: Theme.states.error
            Layout.fillWidth: true
        }

        RowLayout {
            Layout.fillWidth: true
            spacing: Theme.spacing.xs
            TextField {
                id: newNameField
                Layout.fillWidth: true
                placeholderText: qsTr("Neues Projekt …")
                color: Theme.colors.textPrimary
            }
            Button {
                text: qsTr("Anlegen")
                onClicked: {
                    if (vm)
                        vm.createProject(newNameField.text, "")
                }
            }
        }

        RowLayout {
            Layout.fillWidth: true
            spacing: Theme.spacing.xs
            Button {
                text: qsTr("Aktualisieren")
                onClicked: {
                    if (vm)
                        vm.reload()
                }
                Layout.fillWidth: true
            }
            Button {
                text: qsTr("Löschen")
                enabled: vm && vm.selectedProjectId >= 0
                onClicked: {
                    if (vm && vm.selectedProjectId >= 0) {
                        confirmDeleteDialog.pendingProjectId = vm.selectedProjectId
                        confirmDeleteDialog.pendingName = vm.selectedProject || qsTr("(ohne Namen)")
                        confirmDeleteDialog.open()
                    }
                }
            }
        }

        ListView {
            id: projList
            Layout.fillWidth: true
            Layout.fillHeight: true
            clip: true
            spacing: 2
            model: vm ? vm.projects : null

            delegate: Rectangle {
                required property int projectId
                required property string name
                required property string activity
                required property string status
                required property bool isSelected

                width: projList.width
                height: col.implicitHeight + Theme.spacing.sm
                radius: Theme.radius.sm
                color: isSelected ? Theme.surfaces.architectural : Theme.colors.transparent
                border.width: isSelected ? 1 : 0
                border.color: Theme.states.focusRing

                ColumnLayout {
                    id: col
                    anchors.left: parent.left
                    anchors.right: parent.right
                    anchors.verticalCenter: parent.verticalCenter
                    anchors.leftMargin: Theme.spacing.xs
                    anchors.rightMargin: Theme.spacing.xs
                    spacing: 2

                    Label {
                        text: name
                        font.bold: true
                        color: Theme.colors.textPrimary
                        elide: Text.ElideRight
                        Layout.fillWidth: true
                    }
                    Label {
                        text: activity
                        font.pixelSize: Theme.fontSizeSmall
                        color: Theme.colors.textSecondary
                        wrapMode: Text.Wrap
                        Layout.fillWidth: true
                    }
                    Label {
                        text: status
                        font.pixelSize: Theme.fontSizeSmall
                        color: Theme.colors.accentSecondary
                        elide: Text.ElideRight
                        Layout.fillWidth: true
                    }
                }

                MouseArea {
                    anchors.fill: parent
                    cursorShape: Qt.PointingHandCursor
                    onClicked: {
                        if (vm)
                            vm.selectProject(projectId)
                    }
                }
            }
        }
    }

    Dialog {
        id: confirmDeleteDialog
        parent: root
        modal: true
        title: qsTr("Projekt löschen")
        standardButtons: Dialog.Yes | Dialog.No
        width: Math.min(480, 440)

        property int pendingProjectId: -1
        property string pendingName: ""

        onAboutToShow: {
            var ov = Overlay.overlay
            if (ov) {
                parent = ov
                x = Math.round((ov.width - width) / 2)
                y = Math.round((ov.height - height) / 2)
            } else {
                parent = root
                x = Math.round((root.width - width) / 2)
                y = Math.round((root.height - height) / 2)
            }
        }

        onAccepted: {
            if (vm && pendingProjectId >= 0)
                vm.deleteProject(pendingProjectId)
            pendingProjectId = -1
            pendingName = ""
        }

        onRejected: {
            pendingProjectId = -1
            pendingName = ""
        }

        Label {
            width: parent.width
            wrapMode: Text.Wrap
            text: qsTr("Projekt „%1“ wirklich löschen?\n\n%2").arg(confirmDeleteDialog.pendingName).arg(root._deleteInformative)
            color: Theme.colors.textPrimary
        }
    }
}
