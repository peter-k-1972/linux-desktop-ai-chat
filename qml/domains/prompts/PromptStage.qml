import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import themes 1.0

/**
 * Prompt Studio — Regal (Mitte), Katalog (links), Lesepult (rechts), Varianten (unten, optional).
 */
Item {
    id: root
    anchors.fill: parent

    readonly property bool studioOk: typeof promptStudio !== "undefined" && promptStudio !== null

    Rectangle {
        anchors.fill: parent
        visible: !root.studioOk
        color: Theme.colors.surfaceMutedTray
        Label {
            anchors.centerIn: parent
            text: qsTr("Prompt Studio ist nicht angebunden (kein „promptStudio“).")
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

        RowLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            spacing: Theme.spacing.md

            PromptCatalogRail {
                Layout.preferredWidth: Theme.sizing.sessionShelfWidthPreferred
                Layout.fillHeight: true
                vm: promptStudio
            }

            PromptShelf {
                Layout.fillWidth: true
                Layout.fillHeight: true
                vm: promptStudio
            }

            PromptLectern {
                Layout.preferredWidth: Math.max(Theme.sizing.contextSurfaceWidthPreferred, 280)
                Layout.maximumWidth: 400
                Layout.fillHeight: true
                vm: promptStudio
            }
        }

        VariantDrawer {
            Layout.fillWidth: true
            Layout.preferredHeight: promptStudio && promptStudio.variantDrawerOpen ? implicitHeight : 0
            visible: promptStudio && promptStudio.variantDrawerOpen
            vm: promptStudio
        }
    }
}
