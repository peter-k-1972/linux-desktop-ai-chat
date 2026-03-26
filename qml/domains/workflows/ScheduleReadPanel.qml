import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import themes 1.0

/**
 * Geplant — nur Lesen (Schedule-Read-Port). Kein CRUD.
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

        RowLayout {
            Layout.fillWidth: true
            Label {
                text: qsTr("Geplant (Lesen)")
                font.bold: true
                font.pixelSize: Theme.typography.body.pixelSize
                color: Theme.colors.textPrimary
                Layout.fillWidth: true
            }
            Button {
                text: qsTr("Aktualisieren")
                onClicked: root.vm.refreshSchedules()
            }
        }

        Label {
            text: qsTr("Aktives Projekt und globale Einträge — Bearbeitung nur in der Haupt-GUI.")
            wrapMode: Text.Wrap
            Layout.fillWidth: true
            font.pixelSize: Theme.typography.caption.pixelSize
            color: Theme.colors.textSecondary
        }

        ListView {
            Layout.fillWidth: true
            Layout.preferredHeight: 120
            clip: true
            model: vm ? vm.schedules : null
            spacing: 0

            delegate: Rectangle {
                required property string scheduleId
                required property string workflowId
                required property string workflowName
                required property bool enabled
                required property string nextRunAt

                width: parent.width
                height: 28
                color: index % 2 === 0 ? Theme.colors.transparent : Theme.surfaces.architectural
                opacity: 0.35
                RowLayout {
                    anchors.fill: parent
                    anchors.leftMargin: Theme.spacing.xs
                    anchors.rightMargin: Theme.spacing.xs
                    Label {
                        text: scheduleId
                        font.pixelSize: Theme.typography.caption.pixelSize
                        color: Theme.colors.textPrimary
                        Layout.preferredWidth: 120
                        elide: Text.ElideMiddle
                    }
                    Label {
                        text: workflowName.length ? workflowName : workflowId
                        font.pixelSize: Theme.typography.caption.pixelSize
                        color: Theme.colors.textSecondary
                        Layout.preferredWidth: 140
                        elide: Text.ElideRight
                    }
                    Label {
                        text: enabled ? qsTr("an") : qsTr("aus")
                        font.pixelSize: Theme.typography.caption.pixelSize
                        color: Theme.colors.textSecondary
                        Layout.preferredWidth: 36
                    }
                    Label {
                        text: nextRunAt
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
