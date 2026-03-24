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

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: Theme.spaceSm
        spacing: Theme.spaceSm

        Label {
            text: qsTr("Sitzungen")
            font.pixelSize: Theme.fontSizeSmall
            font.bold: true
            color: Theme.textOnDark
            Layout.fillWidth: true
        }

        Button {
            text: qsTr("Neue Sitzung")
            Layout.fillWidth: true
            enabled: chatVm && !chatVm.busy
            onClicked: {
                if (chatVm) {
                    chatVm.createSession()
                }
            }
        }

        ListView {
            id: sessionList
            Layout.fillWidth: true
            Layout.fillHeight: true
            clip: true
            spacing: Theme.spaceXs
            model: chatVm ? chatVm.sessionModel : null

            delegate: Rectangle {
                width: sessionList.width
                height: Math.max(Theme.spaceLg * 2, rowTitle.implicitHeight + Theme.spaceMd)
                radius: Theme.radiusSm
                color: model.isActive ? Theme.accentPrimary : "transparent"
                opacity: model.isActive ? 0.25 : 1

                Label {
                    id: rowTitle
                    anchors.left: parent.left
                    anchors.right: parent.right
                    anchors.verticalCenter: parent.verticalCenter
                    anchors.leftMargin: Theme.spaceSm
                    anchors.rightMargin: Theme.spaceSm
                    text: model.title
                    elide: Text.ElideRight
                    font.pixelSize: Theme.fontSizeSmall
                    color: Theme.textOnDark
                    wrapMode: Text.NoWrap
                }

                MouseArea {
                    anchors.fill: parent
                    cursorShape: Qt.PointingHandCursor
                    onClicked: {
                        if (chatVm) {
                            chatVm.selectSession(model.chatId)
                        }
                    }
                }
            }
        }
    }
}
