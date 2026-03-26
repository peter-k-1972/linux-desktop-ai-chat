import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import themes 1.0

/**
 * Operations Read: Audit-Ereignisse (DB), Runtime-Incidents, QA-Datei-Index, Platform Health.
 * Daten nur über operationsRead (Bridge → Port → Adapter → Services).
 */
Item {
    id: root
    anchors.fill: parent
    objectName: "operationsReadStage"

    readonly property bool opsOk: typeof operationsRead !== "undefined" && operationsRead !== null

    function refreshForTab(ix) {
        if (!root.opsOk)
            return
        if (ix === 0)
            operationsRead.refreshAuditEvents()
        else if (ix === 1)
            operationsRead.refreshRuntimeIncidents()
        else if (ix === 2)
            operationsRead.refreshQaFileSnapshots()
        else if (ix === 3)
            operationsRead.refreshPlatformHealth()
    }

    function applyShellOpsTabHint() {
        var sh = typeof shell !== "undefined" ? shell : null
        if (!sh || !sh.pendingContextJson || sh.pendingContextJson.length === 0)
            return
        try {
            var o = JSON.parse(sh.pendingContextJson)
            var t = (o.audit_incidents_tab || "").toString().toLowerCase()
            if (t === "platform")
                tabBar.currentIndex = 3
            else if (t === "incidents")
                tabBar.currentIndex = 1
            else if (t === "activity")
                tabBar.currentIndex = 0
            root.refreshForTab(tabBar.currentIndex)
            if (sh.clearPendingContext)
                sh.clearPendingContext()
        } catch (e) {
        }
    }

    Component.onCompleted: {
        if (root.opsOk) {
            operationsRead.refreshAll()
            root.applyShellOpsTabHint()
        }
    }

    Rectangle {
        anchors.fill: parent
        visible: !root.opsOk
        color: Theme.surfaces.architectural
        Label {
            anchors.centerIn: parent
            text: qsTr("Operations Read ist nicht angebunden (kein „operationsRead“).")
            color: Theme.colors.textPrimary
            wrapMode: Text.Wrap
            width: parent.width - Theme.spacing.lg * 2
            horizontalAlignment: Text.AlignHCenter
        }
    }

    ColumnLayout {
        anchors.fill: parent
        spacing: Theme.spacing.sm
        visible: root.opsOk

        Label {
            text: qsTr("Betrieb / Audit (Lesen)")
            font.bold: true
            font.pixelSize: Theme.typography.domainTitle.pixelSize
            color: Theme.colors.textPrimary
            Layout.fillWidth: true
        }

        TabBar {
            id: tabBar
            Layout.fillWidth: true
            onCurrentIndexChanged: root.refreshForTab(currentIndex)

            TabButton {
                text: qsTr("Ereignisse")
            }
            TabButton {
                text: qsTr("Incidents")
            }
            TabButton {
                text: qsTr("QA-Berichte")
            }
            TabButton {
                text: qsTr("Plattform")
            }
        }

        StackLayout {
            id: stack
            Layout.fillWidth: true
            Layout.fillHeight: true
            currentIndex: tabBar.currentIndex

            // 0 — Audit events
            Rectangle {
                color: Theme.colors.transparent
                border.width: 1
                border.color: Theme.divider.borderSoft
                radius: Theme.radius.sm
                ListView {
                    id: auditList
                    anchors.fill: parent
                    anchors.margins: 4
                    clip: true
                    model: operationsRead.auditEvents
                    spacing: 0
                    delegate: Rectangle {
                        required property int index
                        required property string occurredAt
                        required property string eventType
                        required property string summary
                        required property int projectId
                        required property string workflowId
                        required property string runId

                        width: auditList.width
                        height: rowA.implicitHeight + Theme.spacing.xs
                        color: auditList.currentIndex === index ? Theme.surfaces.architectural : Theme.colors.transparent
                        border.width: auditList.currentIndex === index ? 1 : 0
                        border.color: Theme.states.focusRing

                        ColumnLayout {
                            id: rowA
                            anchors.left: parent.left
                            anchors.right: parent.right
                            anchors.verticalCenter: parent.verticalCenter
                            anchors.leftMargin: Theme.spacing.xs
                            anchors.rightMargin: Theme.spacing.xs
                            spacing: 2
                            Label {
                                text: occurredAt + " · " + eventType
                                font.pixelSize: Theme.typography.caption.pixelSize
                                color: Theme.colors.textSecondary
                                Layout.fillWidth: true
                                elide: Text.ElideRight
                            }
                            Label {
                                text: summary
                                wrapMode: Text.Wrap
                                Layout.fillWidth: true
                                color: Theme.colors.textPrimary
                                font.pixelSize: Theme.typography.caption.pixelSize
                            }
                            Label {
                                text: "P" + projectId + " · " + workflowId + " · " + runId
                                font.pixelSize: Theme.typography.caption.pixelSize
                                color: Theme.colors.textSecondary
                                Layout.fillWidth: true
                                elide: Text.ElideRight
                            }
                        }
                        MouseArea {
                            anchors.fill: parent
                            onClicked: {
                                auditList.currentIndex = index
                                operationsRead.selectAuditEventRow(index)
                            }
                        }
                    }
                }
            }

            // 1 — Runtime incidents
            Rectangle {
                color: Theme.colors.transparent
                border.width: 1
                border.color: Theme.divider.borderSoft
                radius: Theme.radius.sm
                ListView {
                    id: incList
                    anchors.fill: parent
                    anchors.margins: 4
                    clip: true
                    model: operationsRead.runtimeIncidents
                    spacing: 0
                    delegate: Rectangle {
                        required property int index
                        required property int incidentId
                        required property string lastSeenAt
                        required property string status
                        required property string severity
                        required property string title
                        required property string workflowId
                        required property string runId
                        required property int occurrenceCount

                        width: incList.width
                        height: rowI.implicitHeight + Theme.spacing.xs
                        color: incList.currentIndex === index ? Theme.surfaces.architectural : Theme.colors.transparent
                        border.width: incList.currentIndex === index ? 1 : 0
                        border.color: Theme.states.focusRing

                        ColumnLayout {
                            id: rowI
                            anchors.left: parent.left
                            anchors.right: parent.right
                            anchors.verticalCenter: parent.verticalCenter
                            anchors.leftMargin: Theme.spacing.xs
                            anchors.rightMargin: Theme.spacing.xs
                            spacing: 2
                            Label {
                                text: "#" + incidentId + " · " + lastSeenAt + " · " + status + " · " + severity
                                font.pixelSize: Theme.typography.caption.pixelSize
                                color: Theme.colors.textSecondary
                                Layout.fillWidth: true
                                elide: Text.ElideRight
                            }
                            Label {
                                text: title
                                wrapMode: Text.Wrap
                                Layout.fillWidth: true
                                color: Theme.colors.textPrimary
                                font.pixelSize: Theme.typography.body.pixelSize
                            }
                            Label {
                                text: workflowId + " · " + runId + " · n=" + occurrenceCount
                                font.pixelSize: Theme.typography.caption.pixelSize
                                color: Theme.colors.textSecondary
                                Layout.fillWidth: true
                                elide: Text.ElideRight
                            }
                        }
                        MouseArea {
                            anchors.fill: parent
                            onClicked: {
                                incList.currentIndex = index
                                operationsRead.selectRuntimeIncidentRow(index)
                            }
                        }
                    }
                }
            }

            // 2 — QA index + audit follow-ups (stacked lists)
            ScrollView {
                id: qaScroll
                clip: true
                ColumnLayout {
                    width: qaScroll.availableWidth
                    spacing: Theme.spacing.sm

                    Label {
                        text: operationsRead.qaSummaryLine
                        wrapMode: Text.Wrap
                        Layout.fillWidth: true
                        font.pixelSize: Theme.typography.caption.pixelSize
                        color: Theme.colors.textSecondary
                    }

                    Label {
                        text: qsTr("QA incidents/index.json")
                        font.bold: true
                        font.pixelSize: Theme.typography.caption.pixelSize
                        color: Theme.colors.textPrimary
                    }

                    Rectangle {
                        Layout.fillWidth: true
                        Layout.preferredHeight: 160
                        color: Theme.colors.transparent
                        border.width: 1
                        border.color: Theme.divider.borderSoft
                        radius: Theme.radius.sm
                        ListView {
                            id: qaIdxList
                            anchors.fill: parent
                            anchors.margins: 4
                            clip: true
                            model: operationsRead.qaIndexIncidents
                            delegate: Rectangle {
                                required property int index
                                required property string incidentId
                                required property string title
                                required property string status
                                required property string severity
                                required property string subsystem
                                required property string bindingText

                                width: qaIdxList.width
                                height: qRow.implicitHeight + Theme.spacing.xs
                                color: qaIdxList.currentIndex === index ? Theme.surfaces.architectural : Theme.colors.transparent

                                ColumnLayout {
                                    id: qRow
                                    anchors.left: parent.left
                                    anchors.right: parent.right
                                    anchors.verticalCenter: parent.verticalCenter
                                    anchors.leftMargin: Theme.spacing.xs
                                    spacing: 2
                                    Label {
                                        text: incidentId + " · " + status + " · " + severity
                                        font.pixelSize: Theme.typography.caption.pixelSize
                                        color: Theme.colors.textSecondary
                                        Layout.fillWidth: true
                                    }
                                    Label {
                                        text: title
                                        wrapMode: Text.Wrap
                                        Layout.fillWidth: true
                                        font.pixelSize: Theme.typography.caption.pixelSize
                                    }
                                    Label {
                                        text: subsystem + " · " + bindingText
                                        font.pixelSize: Theme.typography.caption.pixelSize
                                        color: Theme.colors.textSecondary
                                        Layout.fillWidth: true
                                        elide: Text.ElideRight
                                    }
                                }
                                MouseArea {
                                    anchors.fill: parent
                                    onClicked: {
                                        qaIdxList.currentIndex = index
                                        operationsRead.selectQaIndexRow(index)
                                    }
                                }
                            }
                        }
                    }

                    Label {
                        text: operationsRead.auditFollowupSummary
                        wrapMode: Text.Wrap
                        Layout.fillWidth: true
                        font.pixelSize: Theme.typography.caption.pixelSize
                        color: Theme.colors.textSecondary
                    }

                    Label {
                        text: qsTr("AUDIT_REPORT Follow-ups")
                        font.bold: true
                        font.pixelSize: Theme.typography.caption.pixelSize
                        color: Theme.colors.textPrimary
                    }

                    Rectangle {
                        Layout.fillWidth: true
                        Layout.preferredHeight: 140
                        color: Theme.colors.transparent
                        border.width: 1
                        border.color: Theme.divider.borderSoft
                        radius: Theme.radius.sm
                        ListView {
                            id: folList
                            anchors.fill: parent
                            anchors.margins: 4
                            clip: true
                            model: operationsRead.auditFollowups
                            delegate: Rectangle {
                                required property int index
                                required property string category
                                required property string source
                                required property string description

                                width: folList.width
                                height: fRow.implicitHeight + Theme.spacing.xs
                                color: folList.currentIndex === index ? Theme.surfaces.architectural : Theme.colors.transparent

                                ColumnLayout {
                                    id: fRow
                                    anchors.left: parent.left
                                    anchors.right: parent.right
                                    anchors.verticalCenter: parent.verticalCenter
                                    anchors.leftMargin: Theme.spacing.xs
                                    spacing: 2
                                    Label {
                                        text: category + " · " + source
                                        font.pixelSize: Theme.typography.caption.pixelSize
                                        color: Theme.colors.textSecondary
                                        Layout.fillWidth: true
                                        elide: Text.ElideRight
                                    }
                                    Label {
                                        text: description
                                        wrapMode: Text.Wrap
                                        Layout.fillWidth: true
                                        font.pixelSize: Theme.typography.caption.pixelSize
                                    }
                                }
                                MouseArea {
                                    anchors.fill: parent
                                    onClicked: {
                                        folList.currentIndex = index
                                        operationsRead.selectAuditFollowupRow(index)
                                    }
                                }
                            }
                        }
                    }
                }
            }

            // 3 — Platform
            Rectangle {
                color: Theme.colors.transparent
                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: Theme.spacing.xs
                    spacing: Theme.spacing.xs

                    Label {
                        text: operationsRead.platformHeadline
                        Layout.fillWidth: true
                        font.pixelSize: Theme.typography.caption.pixelSize
                        color: Theme.colors.textPrimary
                    }

                    Rectangle {
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        color: Theme.colors.transparent
                        border.width: 1
                        border.color: Theme.divider.borderSoft
                        radius: Theme.radius.sm
                        ListView {
                            id: platList
                            anchors.fill: parent
                            anchors.margins: 4
                            clip: true
                            model: operationsRead.platformChecks
                            delegate: Rectangle {
                                required property int index
                                required property string severity
                                required property string title
                                required property string detail

                                width: platList.width
                                height: pRow.implicitHeight + Theme.spacing.xs
                                color: platList.currentIndex === index ? Theme.surfaces.architectural : Theme.colors.transparent

                                ColumnLayout {
                                    id: pRow
                                    anchors.left: parent.left
                                    anchors.right: parent.right
                                    anchors.verticalCenter: parent.verticalCenter
                                    anchors.leftMargin: Theme.spacing.xs
                                    spacing: 2
                                    Label {
                                        text: "[" + severity + "] " + title
                                        font.pixelSize: Theme.typography.caption.pixelSize
                                        color: Theme.colors.textPrimary
                                        Layout.fillWidth: true
                                        wrapMode: Text.Wrap
                                    }
                                    Label {
                                        text: detail
                                        font.pixelSize: Theme.typography.caption.pixelSize
                                        color: Theme.colors.textSecondary
                                        Layout.fillWidth: true
                                        wrapMode: Text.Wrap
                                        maximumLineCount: 3
                                        elide: Text.ElideRight
                                    }
                                }
                                MouseArea {
                                    anchors.fill: parent
                                    onClicked: {
                                        platList.currentIndex = index
                                        operationsRead.selectPlatformCheckRow(index)
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }

        RowLayout {
            Layout.fillWidth: true
            spacing: Theme.spacing.sm
            Button {
                text: qsTr("Diesen Tab aktualisieren")
                onClicked: root.refreshForTab(tabBar.currentIndex)
            }
            Button {
                text: qsTr("Alles aktualisieren")
                onClicked: operationsRead.refreshAll()
            }
            Button {
                text: qsTr("Zum Workflow-Run …")
                visible: operationsRead.canNavigateIncidentRun
                enabled: operationsRead && !operationsRead.busy
                onClicked: operationsRead.navigateSelectedIncidentToWorkflow(shell)
            }
            Item {
                Layout.fillWidth: true
            }
            Label {
                visible: operationsRead.busy
                text: qsTr("Lade …")
                font.pixelSize: Theme.typography.caption.pixelSize
                color: Theme.colors.textSecondary
            }
        }

        Label {
            visible: operationsRead && operationsRead.lastError.length > 0
            text: operationsRead ? operationsRead.lastError : ""
            wrapMode: Text.Wrap
            Layout.fillWidth: true
            color: Theme.states.error
            font.pixelSize: Theme.typography.caption.pixelSize
        }

        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: detailCol.implicitHeight + Theme.spacing.md
            color: Theme.surfaces.panelSide
            border.width: 1
            border.color: Theme.divider.borderSoft
            radius: Theme.radius.sm

            ColumnLayout {
                id: detailCol
                anchors.fill: parent
                anchors.margins: Theme.spacing.sm
                spacing: Theme.spacing.xs

                Label {
                    text: operationsRead ? operationsRead.detailCaption : "—"
                    font.bold: true
                    font.pixelSize: Theme.typography.body.pixelSize
                    color: Theme.colors.textPrimary
                    Layout.fillWidth: true
                    wrapMode: Text.Wrap
                }
                Label {
                    text: operationsRead ? operationsRead.detailBody : ""
                    wrapMode: Text.Wrap
                    Layout.fillWidth: true
                    color: Theme.colors.textSecondary
                    font.pixelSize: Theme.typography.caption.pixelSize
                }
            }
        }
    }
}
