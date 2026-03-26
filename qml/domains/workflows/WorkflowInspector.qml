import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import themes 1.0

/**
 * Rechte Spalte: ausgewählter Knoten, Kanten-Werkzeug, Speichern / Ausführen.
 */
Rectangle {
    id: root
    color: Theme.surfaces.panelSide
    radius: Theme.radius.md
    border.width: 1
    border.color: Theme.divider.borderSoft
    property var vm

    ScrollView {
        anchors.fill: parent
        anchors.margins: Theme.spacing.sm
        clip: true

        ColumnLayout {
            width: root.width - Theme.spacing.sm * 2
            spacing: Theme.spacing.md

            Label {
                text: qsTr("Workflow-Inspector")
                font.pixelSize: Theme.typography.domainTitle.pixelSize
                font.bold: true
                color: Theme.colors.textPrimary
                Layout.fillWidth: true
            }

            Label {
                visible: vm && vm.pendingEdgeSource.length > 0
                text: qsTr("Kante von: %1 — Ziel wählen, dann Daten- oder Kontroll-Kante.").arg(vm ? vm.pendingEdgeSource : "")
                wrapMode: Text.Wrap
                Layout.fillWidth: true
                color: Theme.colors.accentSecondary
                font.pixelSize: Theme.typography.caption.pixelSize
            }

            ColumnLayout {
                Layout.fillWidth: true
                spacing: Theme.spacing.xs
                Label {
                    text: qsTr("Ausgewählter Knoten")
                    font.pixelSize: Theme.typography.caption.pixelSize
                    color: Theme.colors.textSecondary
                }
                Label {
                    text: vm && vm.selectedNodeId.length ? vm.selectedNodeTitle : qsTr("—")
                    font.bold: true
                    color: Theme.colors.textPrimary
                    wrapMode: Text.Wrap
                    Layout.fillWidth: true
                }
                Label {
                    text: qsTr("Rolle: %1").arg(vm ? vm.selectedNodeRoleKey : "—")
                    color: Theme.colors.textSecondary
                    font.pixelSize: Theme.typography.caption.pixelSize
                }
                Label {
                    text: qsTr("Typ: %1").arg(vm ? vm.selectedNodeType : "—")
                    color: Theme.colors.textSecondary
                    font.pixelSize: Theme.typography.caption.pixelSize
                }
                Label {
                    text: vm ? vm.selectedNodeDescription : ""
                    visible: text.length > 0
                    wrapMode: Text.Wrap
                    Layout.fillWidth: true
                    color: Theme.colors.textSecondary
                    font.pixelSize: Theme.typography.caption.pixelSize
                }
            }

            ColumnLayout {
                Layout.fillWidth: true
                spacing: Theme.spacing.xs
                Label {
                    text: qsTr("Kanten")
                    font.pixelSize: Theme.typography.caption.pixelSize
                    color: Theme.colors.textSecondary
                }
                Button {
                    text: qsTr("Kante von Auswahl …")
                    enabled: vm && vm.selectedWorkflow.length > 0
                    onClicked: vm.startEdgeFromSelectedNode()
                }
                RowLayout {
                    Button {
                        text: qsTr("Kante (Daten)")
                        enabled: vm && vm.pendingEdgeSource.length > 0
                        onClicked: vm.completeEdgeToSelectedNode("data")
                    }
                    Button {
                        text: qsTr("Kante (Kontroll)")
                        enabled: vm && vm.pendingEdgeSource.length > 0
                        onClicked: vm.completeEdgeToSelectedNode("control")
                    }
                }
                Button {
                    text: qsTr("Kante abbrechen")
                    flat: true
                    enabled: vm && vm.pendingEdgeSource.length > 0
                    onClicked: vm.cancelPendingEdge()
                }
            }

            ColumnLayout {
                Layout.fillWidth: true
                spacing: Theme.spacing.xs
                Label {
                    text: qsTr("Knoten hinzufügen")
                    font.pixelSize: Theme.typography.caption.pixelSize
                    color: Theme.colors.textSecondary
                }
                Flow {
                    Layout.fillWidth: true
                    spacing: Theme.spacing.xs
                    Repeater {
                        model: ["agent", "prompt", "tool", "model", "condition", "memory"]
                        delegate: Button {
                            required property string modelData
                            text: modelData
                            onClicked: vm.addNode(modelData)
                            enabled: vm && vm.selectedWorkflow.length > 0
                        }
                    }
                }
            }

            WorkflowJsonObjectInputBlock {
                id: testRunJsonBlock
                caption: qsTr("Test-Run — initial_input (JSON-Objekt, leer = {})")
                boxHeight: 120
                areaObjectName: "workflowTestRunInputJson"
                placeholderText: qsTr('{\n  "key": "value"\n}')
                Component.onCompleted: {
                    if (root.vm)
                        testRunJsonBlock.text = root.vm.testRunInputJson
                }
                Connections {
                    target: root.vm
                    ignoreUnknownSignals: true
                    function onSelectedWorkflowChanged() {
                        if (root.vm)
                            testRunJsonBlock.text = root.vm.testRunInputJson
                    }
                }
            }
            RowLayout {
                Layout.fillWidth: true
                Button {
                    text: qsTr("Test-Run starten")
                    highlighted: true
                    enabled: vm && vm.selectedWorkflow.length > 0 && !vm.runBusy
                    onClicked: {
                        vm.setTestRunInputJson(testRunJsonBlock.text)
                        vm.startTestRun()
                    }
                }
                Button {
                    text: qsTr("Leer ({})")
                    enabled: vm && vm.selectedWorkflow.length > 0
                    onClicked: {
                        testRunJsonBlock.text = "{}"
                        vm.setTestRunInputJson("{}")
                    }
                }
            }
            RowLayout {
                Layout.fillWidth: true
                Button {
                    text: qsTr("Graph speichern")
                    enabled: vm && vm.selectedWorkflow.length > 0
                    onClicked: vm.saveGraph()
                }
            }

            Label {
                visible: vm && vm.lastError.length > 0
                text: vm ? vm.lastError : ""
                wrapMode: Text.Wrap
                Layout.fillWidth: true
                color: Theme.states.error
                font.pixelSize: Theme.typography.caption.pixelSize
            }

            Item {
                Layout.fillHeight: true
                Layout.minimumHeight: Theme.spacing.md
            }
        }
    }
}
