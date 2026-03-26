import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import themes 1.0

/**
 * Agents — Bibliothekare: Dienstliste, Schreibtisch, Inspektor.
 */
Item {
    id: root
    anchors.fill: parent

    readonly property bool studioOk: typeof agentStudio !== "undefined" && agentStudio !== null

    function consumeShellPendingContext() {
        if (!root.studioOk)
            return
        var sh = typeof shell !== "undefined" ? shell : null
        if (!sh || !sh.pendingContextJson || sh.pendingContextJson.length === 0)
            return
        agentStudio.applyShellPendingContextJson(sh.pendingContextJson)
        sh.clearPendingContext()
    }

    Component.onCompleted: root.consumeShellPendingContext()

    Rectangle {
        anchors.fill: parent
        visible: !root.studioOk
        color: Theme.colors.surfaceMutedTray
        Label {
            anchors.centerIn: parent
            text: qsTr("Agents ist nicht angebunden (kein „agentStudio“).")
            color: Theme.colors.textPrimary
            wrapMode: Text.Wrap
            width: parent.width - Theme.spacing.lg * 2
            horizontalAlignment: Text.AlignHCenter
        }
    }

    RowLayout {
        anchors.fill: parent
        spacing: Theme.spacing.md
        visible: root.studioOk

        AgentRoster {
            Layout.preferredWidth: Theme.sizing.sessionShelfWidthPreferred
            Layout.fillHeight: true
            vm: agentStudio
        }

        TaskDesk {
            Layout.fillWidth: true
            Layout.fillHeight: true
            vm: agentStudio
        }

        AgentInspector {
            Layout.preferredWidth: Math.max(Theme.sizing.contextSurfaceWidthPreferred, 260)
            Layout.maximumWidth: 360
            Layout.fillHeight: true
            vm: agentStudio
        }
    }
}
