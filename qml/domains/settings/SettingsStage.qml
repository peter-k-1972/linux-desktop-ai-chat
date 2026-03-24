import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import themes 1.0

/**
 * Settings — Archivraum: Katalog, Ledger, Vorschau.
 */
Item {
    id: root
    anchors.fill: parent

    readonly property bool studioOk: typeof settingsStudio !== "undefined" && settingsStudio !== null

    Rectangle {
        anchors.fill: parent
        visible: !root.studioOk
        color: Theme.colors.surfaceMutedTray
        Label {
            anchors.centerIn: parent
            text: qsTr("Einstellungen sind nicht angebunden (kein „settingsStudio“).")
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

        SettingsCatalog {
            Layout.preferredWidth: Theme.sizing.sessionShelfWidthPreferred
            Layout.fillHeight: true
            vm: settingsStudio
        }

        SettingsLedger {
            Layout.fillWidth: true
            Layout.fillHeight: true
            vm: settingsStudio
        }

        PreviewSurface {
            Layout.preferredWidth: Math.max(Theme.sizing.contextSurfaceWidthPreferred, 240)
            Layout.maximumWidth: 320
            Layout.fillHeight: true
            vm: settingsStudio
        }
    }
}
