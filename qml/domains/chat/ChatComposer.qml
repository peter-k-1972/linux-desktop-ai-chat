import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import themes 1.0

Rectangle {
    id: root
    color: Theme.canvasElevated
    radius: Theme.radiusMd
    border.width: 1
    border.color: Theme.borderSubtle

    property var chatVm

    RowLayout {
        anchors.fill: parent
        anchors.margins: Theme.spaceMd
        spacing: Theme.spaceMd

        TextArea {
            id: input
            Layout.fillWidth: true
            Layout.preferredHeight: Math.min(160, Math.max(56, implicitHeight))
            placeholderText: qsTr("Nachricht … (Enter senden, Umschalt+Enter Zeile)")
            wrapMode: TextEdit.Wrap
            selectByMouse: true
            enabled: chatVm && chatVm.canSend && !chatVm.busy
            color: Theme.textPrimary
            background: Rectangle {
                color: Theme.surfaceWork
                radius: Theme.radiusSm
                border.width: 1
                border.color: Theme.borderSubtle
            }

            Keys.onPressed: function (ev) {
                if (ev.key === Qt.Key_Return || ev.key === Qt.Key_Enter) {
                    if (ev.modifiers & Qt.ShiftModifier) {
                        return
                    }
                    ev.accepted = true
                    root.submit()
                }
            }
        }

        Button {
            text: qsTr("Senden")
            enabled: chatVm && chatVm.canSend && input.text.trim().length > 0
            onClicked: root.submit()
        }
    }

    function submit() {
        if (!chatVm || !chatVm.canSend) {
            return
        }
        var t = input.text.trim()
        if (t.length === 0) {
            return
        }
        chatVm.sendMessage(t)
        input.text = ""
    }
}
