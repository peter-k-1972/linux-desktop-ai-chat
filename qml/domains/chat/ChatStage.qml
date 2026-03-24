import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import themes 1.0

Item {
    id: root
    anchors.fill: parent

    readonly property bool chatOk: typeof chat !== "undefined" && chat !== null

    Rectangle {
        anchors.fill: parent
        visible: !root.chatOk
        color: Theme.colors.surfaceMutedTray
        Label {
            anchors.centerIn: parent
            text: qsTr("Chat ist nicht angebunden (kein Kontextobjekt „chat“).")
            color: Theme.colors.textPrimary
        }
    }

    ColumnLayout {
        anchors.fill: parent
        spacing: Theme.spacing.sm
        visible: root.chatOk

        Label {
            visible: chat && chat.statusHint.length > 0
            text: chat ? chat.statusHint : ""
            font.pixelSize: Theme.fontSizeSmall
            color: Theme.colors.accentSecondary
            Layout.fillWidth: true
        }
        Label {
            visible: chat && chat.errorText.length > 0
            text: chat ? chat.errorText : ""
            font.pixelSize: Theme.fontSizeSmall
            color: Theme.states.error
            wrapMode: Text.Wrap
            Layout.fillWidth: true
        }

        RowLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            spacing: Theme.spacing.md

            ChatSessionShelf {
                Layout.preferredWidth: Theme.sizing.sessionShelfWidthPreferred
                Layout.fillHeight: true
                chatVm: chat
            }

            ColumnLayout {
                Layout.fillWidth: true
                Layout.fillHeight: true
                spacing: Theme.spacing.sm

                ChatReadingTable {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    chatVm: chat
                }
                ChatComposer {
                    Layout.fillWidth: true
                    Layout.preferredHeight: Theme.sizing.inputComposerMinHeight
                    chatVm: chat
                }
            }

            ContextSurface {
                Layout.preferredWidth: Theme.sizing.contextSurfaceWidthPreferred
                Layout.maximumWidth: Theme.sizing.contextSurfaceWidthMax
                Layout.fillHeight: true
                chatVm: chat
            }
        }
    }
}
