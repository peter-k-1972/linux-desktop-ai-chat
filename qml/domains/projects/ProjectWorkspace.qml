import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import themes 1.0

/**
 * Mitte: War-Room-Übersicht — Chats, Workflows, Agenten, Dateien + Sprung zu Chat/Workflows.
 */
Rectangle {
    id: root
    property var vm: null
    property var shellBridge: null

    color: Theme.surfaces.architectural
    radius: Theme.radius.md
    border.width: 1
    border.color: Theme.divider.borderSoft

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: Theme.spacing.sm
        spacing: Theme.spacing.sm

        RowLayout {
            Layout.fillWidth: true
            spacing: Theme.spacing.sm

            Label {
                text: vm && vm.selectedProjectId >= 0
                    ? vm.selectedProject
                    : qsTr("Kein Projekt gewählt")
                font.bold: true
                font.pixelSize: Theme.typography.domainTitle.pixelSize
                color: Theme.colors.textPrimary
                elide: Text.ElideRight
                Layout.fillWidth: true
            }

            Button {
                text: qsTr("Zum Chat")
                enabled: shellBridge !== null && vm !== null
                onClicked: {
                    if (vm && shellBridge)
                        vm.shellNavigateToOperationsChat(shellBridge)
                }
            }
            Button {
                text: qsTr("Zu Workflows (Projekt)")
                enabled: shellBridge !== null && vm !== null
                onClicked: {
                    if (vm && shellBridge)
                        vm.shellNavigateToOperationsWorkflowsProjectScope(shellBridge)
                }
            }
            Button {
                text: qsTr("Agent Tasks")
                enabled: shellBridge !== null && vm !== null
                onClicked: {
                    if (vm && shellBridge)
                        vm.shellNavigateToAgentTasksWithAgentId(shellBridge, "")
                }
            }
        }

        Label {
            visible: !vm || vm.selectedProjectId < 0
            text: qsTr("Wählen Sie links ein Projekt, um Chats, Workflows, Agenten und Dateien zu sehen.")
            wrapMode: Text.Wrap
            color: Theme.colors.textSecondary
            Layout.fillWidth: true
        }

        ScrollView {
            Layout.fillWidth: true
            Layout.fillHeight: true
            visible: vm && vm.selectedProjectId >= 0
            clip: true

            ColumnLayout {
                width: Math.max(120, root.width - Theme.spacing.sm * 4)
                spacing: Theme.spacing.md

                Loader {
                    Layout.fillWidth: true
                    source: "ProjectSection.qml"
                    onLoaded: if (item)
                        item.titleText = qsTr("Chats — letzte Sessions")
                }

                ListView {
                    Layout.fillWidth: true
                    Layout.preferredHeight: Math.min(220, chatLv.count * 56 + 8)
                    clip: true
                    id: chatLv
                    spacing: 2
                    model: vm ? vm.chats : null

                    delegate: Rectangle {
                        required property int chatId
                        required property string title
                        required property string subline

                        width: chatLv.width
                        height: rchat.implicitHeight + Theme.spacing.sm
                        radius: Theme.radius.sm
                        color: Theme.surfaces.panelSide
                        border.width: 1
                        border.color: Theme.divider.borderSoft

                        ColumnLayout {
                            id: rchat
                            anchors.left: parent.left
                            anchors.right: parent.right
                            anchors.verticalCenter: parent.verticalCenter
                            anchors.margins: Theme.spacing.xs
                            spacing: 2
                            Label {
                                text: title
                                font.bold: true
                                color: Theme.colors.textPrimary
                                elide: Text.ElideRight
                                Layout.fillWidth: true
                            }
                            Label {
                                text: subline
                                font.pixelSize: Theme.fontSizeSmall
                                color: Theme.colors.textSecondary
                                Layout.fillWidth: true
                            }
                        }
                        MouseArea {
                            anchors.fill: parent
                            cursorShape: Qt.PointingHandCursor
                            onClicked: {
                                if (vm && shellBridge)
                                    vm.shellNavigateToOperationsChatWithChatId(shellBridge, chatId)
                            }
                        }
                    }
                }

                Loader {
                    Layout.fillWidth: true
                    source: "ProjectSection.qml"
                    onLoaded: if (item)
                        item.titleText = qsTr("Workflows")
                }

                ListView {
                    Layout.fillWidth: true
                    Layout.preferredHeight: Math.min(200, wfLv.count * 52 + 8)
                    clip: true
                    id: wfLv
                    spacing: 2
                    model: vm ? vm.workflows : null

                    delegate: Rectangle {
                        required property string workflowId
                        required property string name
                        required property string subline

                        width: wfLv.width
                        height: rwf.implicitHeight + Theme.spacing.sm
                        radius: Theme.radius.sm
                        color: Theme.surfaces.panelSide
                        border.width: 1
                        border.color: Theme.divider.borderSoft

                        RowLayout {
                            id: rwf
                            anchors.fill: parent
                            anchors.margins: Theme.spacing.xs
                            Label {
                                text: name
                                font.bold: true
                                color: Theme.colors.textPrimary
                                elide: Text.ElideRight
                                Layout.fillWidth: true
                            }
                            Label {
                                text: subline
                                font.pixelSize: Theme.fontSizeSmall
                                color: Theme.colors.textSecondary
                            }
                        }
                        MouseArea {
                            anchors.fill: parent
                            cursorShape: Qt.PointingHandCursor
                            onClicked: {
                                if (vm && shellBridge)
                                    vm.shellNavigateToOperationsWorkflowWithId(shellBridge, workflowId)
                            }
                        }
                    }
                }

                Loader {
                    Layout.fillWidth: true
                    source: "ProjectSection.qml"
                    onLoaded: if (item)
                        item.titleText = qsTr("Aktive Agenten")
                }

                ListView {
                    Layout.fillWidth: true
                    Layout.preferredHeight: Math.min(180, agLv.count * 48 + 8)
                    clip: true
                    id: agLv
                    spacing: 2
                    model: vm ? vm.agents : null

                    delegate: Rectangle {
                        required property string agentId
                        required property string name
                        required property string subline

                        width: agLv.width
                        height: rag.implicitHeight + Theme.spacing.sm
                        radius: Theme.radius.sm
                        color: Theme.surfaces.panelSide
                        border.width: 1
                        border.color: Theme.divider.borderSoft

                        ColumnLayout {
                            id: rag
                            anchors.left: parent.left
                            anchors.right: parent.right
                            anchors.verticalCenter: parent.verticalCenter
                            anchors.margins: Theme.spacing.xs
                            spacing: 2
                            Label {
                                text: name
                                font.bold: true
                                color: Theme.colors.textPrimary
                                elide: Text.ElideRight
                                Layout.fillWidth: true
                            }
                            Label {
                                text: subline
                                font.pixelSize: Theme.fontSizeSmall
                                color: Theme.colors.textSecondary
                                Layout.fillWidth: true
                            }
                        }
                        MouseArea {
                            anchors.fill: parent
                            cursorShape: Qt.PointingHandCursor
                            onClicked: {
                                if (vm && shellBridge)
                                    vm.shellNavigateToAgentTasksWithAgentId(shellBridge, agentId)
                            }
                        }
                    }
                }

                Loader {
                    Layout.fillWidth: true
                    source: "ProjectSection.qml"
                    onLoaded: if (item)
                        item.titleText = qsTr("Dateien")
                }

                ListView {
                    Layout.fillWidth: true
                    Layout.preferredHeight: Math.min(200, fileLv.count * 48 + 8)
                    clip: true
                    id: fileLv
                    spacing: 2
                    model: vm ? vm.files : null

                    delegate: Rectangle {
                        required property int fileId
                        required property string name
                        required property string subline

                        width: fileLv.width
                        height: rfl.implicitHeight + Theme.spacing.sm
                        radius: Theme.radius.sm
                        color: Theme.surfaces.panelSide
                        border.width: 1
                        border.color: Theme.divider.borderSoft

                        ColumnLayout {
                            id: rfl
                            anchors.left: parent.left
                            anchors.right: parent.right
                            anchors.verticalCenter: parent.verticalCenter
                            anchors.margins: Theme.spacing.xs
                            spacing: 2
                            Label {
                                text: name
                                font.bold: true
                                color: Theme.colors.textPrimary
                                elide: Text.ElideRight
                                Layout.fillWidth: true
                            }
                            Label {
                                text: subline
                                font.pixelSize: Theme.fontSizeSmall
                                color: Theme.colors.textSecondary
                                elide: Text.ElideMiddle
                                Layout.fillWidth: true
                            }
                        }
                    }
                }

                Item {
                    Layout.fillWidth: true
                    Layout.minimumHeight: Theme.spacing.lg
                }
            }
        }
    }
}
