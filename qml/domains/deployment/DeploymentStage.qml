import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import themes 1.0

/**
 * Deployment — Druckerei: Auflagen, Presse, Artefakte, Log.
 */
Item {
    id: root
    anchors.fill: parent

    readonly property bool studioOk: typeof deploymentStudio !== "undefined" && deploymentStudio !== null

    Rectangle {
        anchors.fill: parent
        visible: !root.studioOk
        color: Theme.colors.surfaceMutedTray
        Label {
            anchors.centerIn: parent
            text: qsTr("Deployment ist nicht angebunden (kein „deploymentStudio“).")
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

        EditionBoard {
            Layout.fillWidth: true
            Layout.preferredHeight: 200
            vm: deploymentStudio
        }

        RowLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            spacing: Theme.spacing.md

            PressLine {
                Layout.fillWidth: true
                Layout.fillHeight: true
                vm: deploymentStudio
            }

            ArtifactRack {
                Layout.preferredWidth: Math.max(Theme.sizing.contextSurfaceWidthPreferred, 260)
                Layout.maximumWidth: 340
                Layout.fillHeight: true
                vm: deploymentStudio
            }
        }

        BuildLog {
            Layout.fillWidth: true
            Layout.preferredHeight: 140
            vm: deploymentStudio
        }
    }
}
