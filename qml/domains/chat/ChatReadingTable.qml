import QtQuick
import QtQuick.Controls
import themes 1.0

Rectangle {
    id: root
    color: Theme.surfaceWork
    radius: Theme.radiusMd
    border.width: 1
    border.color: Theme.borderSubtle

    property var chatVm

    property bool stickToBottom: true

    Item {
        id: manuscript
        anchors.fill: parent
        anchors.margins: Theme.spaceMd

        Rectangle {
            id: columnGuide
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.top: parent.top
            anchors.bottom: parent.bottom
            width: Math.min(
                parent.width - 2 * Theme.readingManuscriptPadH,
                Theme.readingColumnMaxWidth
            )
            color: Theme.surfaceWork
            border.width: 0

            ListView {
                id: msgList
                anchors.fill: parent
                anchors.leftMargin: Theme.readingManuscriptPadH
                anchors.rightMargin: Theme.readingManuscriptPadH
                anchors.topMargin: Theme.readingManuscriptPadV
                anchors.bottomMargin: Theme.readingManuscriptPadV
                clip: true
                spacing: Theme.readingSectionGap
                model: chatVm ? chatVm.messageModel : null
                boundsBehavior: Flickable.StopAtBounds

                delegate: ChatMessageBlock {
                    width: msgList.width
                }

                ScrollBar.vertical: ScrollBar {}

                onMovementEnded: root.stickToBottom = atYEnd
                onFlickEnded: root.stickToBottom = atYEnd
            }
        }
    }

    Connections {
        target: chatVm
        enabled: chatVm !== null
        function onReadingTableScrollToEnd() {
            Qt.callLater(function () {
                if (!root.stickToBottom || msgList.count === 0) {
                    return
                }
                msgList.positionViewAtEnd()
            })
        }
        function onActiveChatIdChanged() {
            root.stickToBottom = true
        }
    }

    Label {
        z: 2
        anchors.centerIn: parent
        visible: chatVm && msgList.count === 0
        width: Math.min(parent.width - Theme.spaceLg * 2, Theme.readingColumnMaxWidth)
        horizontalAlignment: Text.AlignHCenter
        wrapMode: Text.Wrap
        text: qsTr("Keine Nachrichten in dieser Sitzung.")
        font.pixelSize: Theme.fontSizeUi
        color: Theme.textSecondary
    }
}
