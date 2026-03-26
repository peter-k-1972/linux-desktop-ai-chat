import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import themes 1.0

/**
 * Workflows — Planungstafel: Liste, Canvas, Inspector, Run-Historie.
 */
Item {
    id: root
    anchors.fill: parent

    readonly property bool studioOk: typeof workflowStudio !== "undefined" && workflowStudio !== null

    Connections {
        target: root.studioOk ? workflowStudio : null
        ignoreUnknownSignals: true
        function onShellPendingContextClearSuggested() {
            var sh = typeof shell !== "undefined" ? shell : null
            if (sh && sh.clearPendingContext)
                sh.clearPendingContext()
        }
    }

    function consumeShellPendingContext() {
        if (!root.studioOk)
            return
        var sh = typeof shell !== "undefined" ? shell : null
        if (!sh || !sh.pendingContextJson || sh.pendingContextJson.length === 0)
            return
        workflowStudio.applyShellPendingContextJson(sh.pendingContextJson)
        // Clear-Signal: nach erfolgreicher Anwendung oder nach Speichern/Verwerfen im Resolver — nicht nach Abbrechen.
    }

    Component.onCompleted: root.consumeShellPendingContext()

    Rectangle {
        anchors.fill: parent
        visible: !root.studioOk
        color: Theme.surfaces.architectural
        Label {
            anchors.centerIn: parent
            text: qsTr("Workflows ist nicht angebunden (kein „workflowStudio“).")
            color: Theme.colors.textPrimary
            wrapMode: Text.Wrap
            width: parent.width - Theme.spacing.lg * 2
            horizontalAlignment: Text.AlignHCenter
        }
    }

    ColumnLayout {
        anchors.fill: parent
        spacing: Theme.spacing.sm
        visible: root.studioOk

        Rectangle {
            visible: workflowStudio && workflowStudio.graphActionPending
            Layout.fillWidth: true
            Layout.preferredHeight: bannerCol.implicitHeight + Theme.spacing.md
            color: Theme.surfaces.architectural
            border.width: 1
            border.color: Theme.states.focusRing
            radius: Theme.radius.md
            ColumnLayout {
                id: bannerCol
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.top: parent.top
                anchors.margins: Theme.spacing.sm
                spacing: Theme.spacing.xs
                Label {
                    text: qsTr("Graph-Entscheidung erforderlich")
                    font.bold: true
                    color: Theme.colors.textPrimary
                    Layout.fillWidth: true
                }
                Label {
                    text: workflowStudio ? workflowStudio.graphActionPrompt : ""
                    wrapMode: Text.Wrap
                    Layout.fillWidth: true
                    color: Theme.colors.textSecondary
                    font.pixelSize: Theme.typography.caption.pixelSize
                }
                RowLayout {
                    spacing: Theme.spacing.sm
                    Button {
                        text: qsTr("Speichern & fortfahren")
                        onClicked: workflowStudio.resolveGraphActionSave()
                    }
                    Button {
                        text: qsTr("Verwerfen & fortfahren")
                        onClicked: workflowStudio.resolveGraphActionDiscard()
                    }
                    Button {
                        text: qsTr("Abbrechen")
                        flat: true
                        onClicked: workflowStudio.resolveGraphActionCancel()
                    }
                }
            }
        }

        RowLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            spacing: Theme.spacing.md

            Rectangle {
                Layout.preferredWidth: 280
                Layout.maximumWidth: 360
                Layout.fillHeight: true
                color: Theme.surfaces.panelSide
                radius: Theme.radius.md
                border.width: 1
                border.color: Theme.divider.borderSoft

                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: Theme.spacing.sm
                    spacing: Theme.spacing.xs

                    Label {
                        text: qsTr("Workflow-Liste")
                        font.bold: true
                        font.pixelSize: Theme.typography.body.pixelSize
                        color: Theme.colors.textPrimary
                        Layout.fillWidth: true
                    }

                    Button {
                        text: qsTr("Aktualisieren")
                        onClicked: workflowStudio.reload()
                        Layout.fillWidth: true
                    }

                    ListView {
                        id: wfList
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        clip: true
                        model: workflowStudio.workflows
                        spacing: 2

                        delegate: Rectangle {
                            required property string workflowId
                            required property string name
                            required property int version
                            required property string subline
                            required property bool isSelected

                            width: wfList.width
                            height: row.implicitHeight + Theme.spacing.sm
                            radius: Theme.radius.sm
                            color: isSelected ? Theme.surfaces.architectural : Theme.colors.transparent
                            border.width: isSelected ? 1 : 0
                            border.color: Theme.states.focusRing

                            ColumnLayout {
                                id: row
                                anchors.left: parent.left
                                anchors.right: parent.right
                                anchors.verticalCenter: parent.verticalCenter
                                anchors.leftMargin: Theme.spacing.xs
                                anchors.rightMargin: Theme.spacing.xs
                                Label {
                                    text: name
                                    font.bold: true
                                    color: Theme.colors.textPrimary
                                    elide: Text.ElideRight
                                    Layout.fillWidth: true
                                }
                                Label {
                                    text: subline
                                    font.pixelSize: Theme.typography.caption.pixelSize
                                    color: Theme.colors.textSecondary
                                    elide: Text.ElideRight
                                    Layout.fillWidth: true
                                }
                            }

                            MouseArea {
                                anchors.fill: parent
                                onClicked: workflowStudio.requestSelectWorkflow(workflowId)
                            }
                        }
                    }
                }
            }

            WorkflowCanvas {
                Layout.fillWidth: true
                Layout.fillHeight: true
                vm: workflowStudio
            }

            WorkflowInspector {
                Layout.preferredWidth: 300
                Layout.maximumWidth: 400
                Layout.fillHeight: true
                vm: workflowStudio
            }
        }

        RunHistoryPanel {
            Layout.fillWidth: true
            Layout.preferredHeight: 360
            Layout.minimumHeight: 260
            Layout.maximumHeight: 560
            vm: workflowStudio
        }

        ScheduleReadPanel {
            Layout.fillWidth: true
            Layout.preferredHeight: 200
            vm: workflowStudio
        }
    }
}
