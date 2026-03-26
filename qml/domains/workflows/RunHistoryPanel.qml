import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import themes 1.0

/**
 * Run-Liste mit Scopes/Filtern, Diagnose und NodeRuns — Daten nur aus workflowStudio (Port/Presenter).
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

        Label {
            visible: vm && vm.runScopeCaption.length > 0
            text: vm ? vm.runScopeCaption : ""
            wrapMode: Text.Wrap
            Layout.fillWidth: true
            font.pixelSize: Theme.typography.caption.pixelSize
            color: Theme.colors.textSecondary
        }

        Label {
            visible: vm && vm.runEmptyHint.length > 0
            text: vm ? vm.runEmptyHint : ""
            wrapMode: Text.Wrap
            Layout.fillWidth: true
            font.pixelSize: Theme.typography.caption.pixelSize
            color: Theme.states.warning
        }

        RowLayout {
            Layout.fillWidth: true
            spacing: Theme.spacing.sm
            Label {
                text: qsTr("Runs:")
                font.pixelSize: Theme.typography.caption.pixelSize
                color: Theme.colors.textSecondary
            }
            ComboBox {
                id: scopeCombo
                Layout.preferredWidth: 200
                model: [qsTr("Dieser Workflow"), qsTr("Aktives Projekt"), qsTr("Alle Runs")]
                property var scopeValues: ["workflow", "project", "all"]
                Component.onCompleted: syncScopeFromVm()
                Connections {
                    target: root.vm
                    function onRunListScopeChanged() {
                        scopeCombo.syncScopeFromVm()
                    }
                    ignoreUnknownSignals: true
                }
                function syncScopeFromVm() {
                    if (!root.vm)
                        return
                    var v = root.vm.runListScope
                    for (var i = 0; i < scopeValues.length; i++) {
                        if (scopeValues[i] === v) {
                            currentIndex = i
                            return
                        }
                    }
                }
                onActivated: function (ix) {
                    if (root.vm && ix >= 0 && ix < scopeValues.length)
                        root.vm.setRunListScope(scopeValues[ix])
                }
            }
            Label {
                text: qsTr("Status:")
                font.pixelSize: Theme.typography.caption.pixelSize
                color: Theme.colors.textSecondary
            }
            ComboBox {
                id: statusCombo
                Layout.preferredWidth: 160
                model: ["", "pending", "running", "completed", "failed", "cancelled"]
                displayText: currentIndex <= 0 ? qsTr("Alle") : model[currentIndex]
                Component.onCompleted: syncStatusFromVm()
                Connections {
                    target: root.vm
                    function onRunStatusFilterChanged() {
                        statusCombo.syncStatusFromVm()
                    }
                    ignoreUnknownSignals: true
                }
                function syncStatusFromVm() {
                    if (!root.vm)
                        return
                    var v = root.vm.runStatusFilter
                    if (!v || v.length === 0) {
                        currentIndex = 0
                        return
                    }
                    for (var i = 1; i < model.length; i++) {
                        if (model[i] === v) {
                            currentIndex = i
                            return
                        }
                    }
                }
                onActivated: function (ix) {
                    if (!root.vm)
                        return
                    root.vm.setRunStatusFilter(ix <= 0 ? "" : model[ix])
                }
            }
            Button {
                text: qsTr("Runs aktualisieren")
                onClicked: root.vm.refreshRuns()
            }
            Button {
                text: qsTr("Re-Run (gleiche Eingaben)")
                enabled: root.vm && root.vm.selectedRunId.length > 0 && !root.vm.runBusy
                onClicked: root.vm.rerunSelectedRunSameInputs()
            }
            Item {
                Layout.fillWidth: true
            }
        }

        Label {
            visible: vm && vm.graphDirty
            text: qsTr("Hinweis: Graph geändert — Speichern vor kontextabhängigem Workflow-Wechsel empfohlen.")
            wrapMode: Text.Wrap
            Layout.fillWidth: true
            font.pixelSize: Theme.typography.caption.pixelSize
            color: Theme.states.warning
        }

        ColumnLayout {
            Layout.fillWidth: true
            spacing: Theme.spacing.xs
            WorkflowJsonObjectInputBlock {
                id: rerunOverrideBlock
                caption: qsTr("Re-Run — Eingaben überschreiben (JSON-Objekt; gleiche Semantik wie Test-Run)")
                boxHeight: 72
                areaObjectName: "workflowRerunOverrideJson"
                placeholderText: qsTr("Leer lassen und „Re-Run (gleiche Eingaben)“ nutzen, oder JSON-Objekt.")
            }
            Connections {
                target: root.vm
                ignoreUnknownSignals: true
                function onRerunOverrideInputJsonChanged() {
                    if (root.vm)
                        rerunOverrideBlock.text = root.vm.rerunOverrideInputJson
                }
            }
            RowLayout {
                Layout.fillWidth: true
                spacing: Theme.spacing.sm
                Button {
                    text: qsTr("Aus Run übernehmen")
                    enabled: root.vm && root.vm.selectedRunId.length > 0
                    onClicked: root.vm.syncRerunOverrideFromSelectedRun()
                }
                Button {
                    text: qsTr("Re-Run (Override)")
                    enabled: root.vm && root.vm.selectedRunId.length > 0 && !root.vm.runBusy
                    onClicked: {
                        root.vm.setRerunOverrideInputJson(rerunOverrideBlock.text)
                        root.vm.startRerunWithCommittedOverride()
                    }
                }
            }
        }

        RowLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            spacing: Theme.spacing.sm

            // Run list
            Rectangle {
                Layout.preferredWidth: 420
                Layout.fillHeight: true
                color: Theme.colors.transparent
                border.width: 1
                border.color: Theme.divider.borderSoft
                radius: Theme.radius.sm
                ListView {
                    id: runList
                    anchors.fill: parent
                    anchors.margins: 2
                    clip: true
                    model: vm ? vm.runs : null
                    spacing: 0
                    delegate: Rectangle {
                        required property string runId
                        required property string status
                        required property string duration
                        required property string started
                        required property string workflowId
                        required property string workflowName
                        required property string projectLabel
                        required property string errorPreview
                        required property bool isSelected
                        width: runList.width
                        height: row.implicitHeight + Theme.spacing.xs
                        color: isSelected ? Theme.surfaces.architectural : Theme.colors.transparent
                        border.width: isSelected ? 1 : 0
                        border.color: Theme.states.focusRing
                        radius: Theme.radius.sm
                        ColumnLayout {
                            id: row
                            anchors.left: parent.left
                            anchors.right: parent.right
                            anchors.verticalCenter: parent.verticalCenter
                            anchors.leftMargin: Theme.spacing.xs
                            anchors.rightMargin: Theme.spacing.xs
                            Label {
                                text: runId
                                font.bold: true
                                font.pixelSize: Theme.typography.caption.pixelSize
                                color: Theme.colors.textPrimary
                                elide: Text.ElideMiddle
                                Layout.fillWidth: true
                            }
                            Label {
                                text: workflowName.length ? (workflowName + " · " + workflowId) : workflowId
                                font.pixelSize: Theme.typography.caption.pixelSize
                                color: Theme.colors.textSecondary
                                elide: Text.ElideRight
                                Layout.fillWidth: true
                            }
                            RowLayout {
                                Layout.fillWidth: true
                                Label {
                                    text: status
                                    font.pixelSize: Theme.typography.caption.pixelSize
                                    color: Theme.colors.textPrimary
                                    Layout.preferredWidth: 88
                                }
                                Label {
                                    text: duration
                                    font.pixelSize: Theme.typography.caption.pixelSize
                                    color: Theme.colors.textSecondary
                                    Layout.preferredWidth: 56
                                }
                                Label {
                                    text: projectLabel
                                    font.pixelSize: Theme.typography.caption.pixelSize
                                    color: Theme.colors.textSecondary
                                    Layout.preferredWidth: 72
                                }
                            }
                            Label {
                                visible: errorPreview.length > 0 && errorPreview !== "—"
                                text: errorPreview
                                font.pixelSize: Theme.typography.caption.pixelSize
                                color: Theme.states.error
                                wrapMode: Text.Wrap
                                Layout.fillWidth: true
                            }
                        }
                        MouseArea {
                            anchors.fill: parent
                            onClicked: root.vm.selectRun(runId)
                        }
                    }
                }
            }

            // Diagnostics + node runs
            ColumnLayout {
                Layout.fillWidth: true
                Layout.fillHeight: true
                spacing: Theme.spacing.xs

                Rectangle {
                    Layout.fillWidth: true
                    Layout.preferredHeight: diagCol.implicitHeight + Theme.spacing.sm
                    color: Theme.surfaces.architectural
                    radius: Theme.radius.sm
                    border.width: 1
                    border.color: Theme.divider.borderSoft
                    ColumnLayout {
                        id: diagCol
                        anchors.left: parent.left
                        anchors.right: parent.right
                        anchors.top: parent.top
                        anchors.margins: Theme.spacing.sm
                        spacing: Theme.spacing.xs
                        Label {
                            text: qsTr("Diagnose (Run)")
                            font.bold: true
                            font.pixelSize: Theme.typography.caption.pixelSize
                            color: Theme.colors.textSecondary
                            Layout.fillWidth: true
                        }
                        Label {
                            text: vm ? vm.runDiagnosticsHeadline : "—"
                            font.bold: true
                            wrapMode: Text.Wrap
                            Layout.fillWidth: true
                            color: Theme.colors.textPrimary
                            font.pixelSize: Theme.typography.body.pixelSize
                        }
                        Label {
                            text: vm ? vm.runDiagnosticsSummary : ""
                            wrapMode: Text.Wrap
                            Layout.fillWidth: true
                            color: Theme.colors.textSecondary
                            font.pixelSize: Theme.typography.caption.pixelSize
                        }
                        Label {
                            text: vm ? vm.runDiagnosticsDetail : ""
                            wrapMode: Text.Wrap
                            Layout.fillWidth: true
                            color: Theme.colors.textSecondary
                            font.pixelSize: Theme.typography.caption.pixelSize
                        }
                        Label {
                            visible: vm && vm.runErrorFull.length > 0
                            text: vm ? vm.runErrorFull : ""
                            wrapMode: Text.Wrap
                            Layout.fillWidth: true
                            color: Theme.states.error
                            font.pixelSize: Theme.typography.caption.pixelSize
                        }
                    }
                }

                Label {
                    text: qsTr("Initial-Input (JSON)")
                    font.pixelSize: Theme.typography.caption.pixelSize
                    color: Theme.colors.textSecondary
                    Layout.fillWidth: true
                }
                ScrollView {
                    Layout.fillWidth: true
                    Layout.preferredHeight: 72
                    ScrollBar.horizontal.policy: ScrollBar.AlwaysOff
                    TextArea {
                        readOnly: true
                        wrapMode: Text.Wrap
                        text: vm ? vm.runInitialInputJson : ""
                        font.family: "monospace"
                        font.pixelSize: Theme.typography.caption.pixelSize
                        color: Theme.colors.textPrimary
                        background: Rectangle {
                            color: Theme.surfaces.architectural
                            radius: Theme.radius.sm
                        }
                    }
                }

                Label {
                    text: qsTr("Knotenläufe")
                    font.bold: true
                    font.pixelSize: Theme.typography.caption.pixelSize
                    color: Theme.colors.textSecondary
                    Layout.fillWidth: true
                }
                Rectangle {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    Layout.minimumHeight: 100
                    color: Theme.colors.transparent
                    border.width: 1
                    border.color: Theme.divider.borderSoft
                    radius: Theme.radius.sm
                    ListView {
                        id: nodeRunList
                        anchors.fill: parent
                        anchors.margins: 2
                        clip: true
                        model: vm ? vm.nodeRuns : null
                        delegate: Rectangle {
                            required property string nodeRunId
                            required property string nodeId
                            required property string nodeType
                            required property string status
                            required property string errorPreview
                            required property bool isSelected
                            width: nodeRunList.width
                            height: nrRow.implicitHeight + 4
                            color: isSelected ? Theme.surfaces.architectural : Theme.colors.transparent
                            ColumnLayout {
                                id: nrRow
                                anchors.fill: parent
                                anchors.margins: Theme.spacing.xs
                                Label {
                                    text: nodeId + " · " + nodeType + " · " + status
                                    font.pixelSize: Theme.typography.caption.pixelSize
                                    color: Theme.colors.textPrimary
                                    Layout.fillWidth: true
                                }
                                Label {
                                    visible: errorPreview.length > 0 && errorPreview !== "—"
                                    text: errorPreview
                                    font.pixelSize: Theme.typography.caption.pixelSize
                                    color: Theme.states.error
                                    wrapMode: Text.Wrap
                                    Layout.fillWidth: true
                                }
                            }
                            MouseArea {
                                anchors.fill: parent
                                onClicked: root.vm.selectNodeRun(nodeRunId)
                            }
                        }
                    }
                }

                Label {
                    text: qsTr("Knoten-Detail (Input / Output / Fehler)")
                    font.pixelSize: Theme.typography.caption.pixelSize
                    color: Theme.colors.textSecondary
                    Layout.fillWidth: true
                }
                RowLayout {
                    Layout.fillWidth: true
                    Layout.preferredHeight: 100
                    ScrollView {
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        TextArea {
                            readOnly: true
                            wrapMode: Text.Wrap
                            text: vm ? vm.selectedNodeRunInputJson : ""
                            font.family: "monospace"
                            font.pixelSize: Theme.typography.caption.pixelSize
                        }
                    }
                    ScrollView {
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        TextArea {
                            readOnly: true
                            wrapMode: Text.Wrap
                            text: vm ? vm.selectedNodeRunOutputJson : ""
                            font.family: "monospace"
                            font.pixelSize: Theme.typography.caption.pixelSize
                        }
                    }
                }
                TextArea {
                    Layout.fillWidth: true
                    Layout.preferredHeight: 56
                    readOnly: true
                    wrapMode: Text.Wrap
                    text: vm ? vm.selectedNodeRunErrorText : ""
                    font.family: "monospace"
                    font.pixelSize: Theme.typography.caption.pixelSize
                    color: Theme.states.error
                }
            }
        }
    }
}
