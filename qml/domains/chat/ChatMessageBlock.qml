import QtQuick
import QtQuick.Controls
import themes 1.0

Item {
    id: root
    width: ListView.view ? ListView.view.width : parent.width
    height: blockRoot.height

    property string msgRole: model.role
    property string msgContent: model.content
    property string msgModelLabel: model.modelLabel
    property bool msgStreaming: model.isStreaming

    readonly property bool isUser: msgRole === "user"
    readonly property bool isAssistant: msgRole === "assistant"
    readonly property bool isSystem: msgRole === "system" || msgRole === "tool"

    Item {
        id: blockRoot
        width: root.width
        height: col.height

        Column {
            id: col
            width: isUser ? Math.min(parent.width, Theme.readingUserMaxWidth) : parent.width
            spacing: Theme.readingBlockGap

            Item {
                width: 1
                height: isAssistant ? Theme.spaceSm : Theme.readingRoleToBodyGap
                visible: isAssistant || isUser
            }

            Row {
                id: userRow
                visible: isUser
                width: parent.width
                spacing: Theme.spaceSm

                Rectangle {
                    width: 2
                    height: userStack.height
                    radius: 1
                    color: Theme.borderSubtle
                    opacity: 0.75
                }

                Column {
                    id: userStack
                    width: userRow.width - userRow.spacing - 2
                    spacing: Theme.readingRoleToBodyGap

                    Label {
                        width: parent.width
                        text: qsTr("Anfrage")
                        font.pixelSize: Theme.fontSizeSmall
                        font.weight: Font.Medium
                        font.letterSpacing: 0.3
                        color: Theme.textSecondary
                    }
                    Label {
                        width: parent.width
                        text: msgContent
                        wrapMode: Text.Wrap
                        font.pixelSize: Theme.fontSizeUi
                        lineHeight: Theme.readingUserLineHeight
                        lineHeightMode: Text.ProportionalHeight
                        color: Theme.textPrimary
                    }
                }
            }

            Column {
                visible: isAssistant
                width: parent.width
                spacing: Theme.readingRoleToBodyGap

                Label {
                    width: parent.width
                    text: qsTr("Antwort")
                    font.pixelSize: Theme.fontSizeSmall
                    font.weight: Font.Medium
                    font.letterSpacing: 0.3
                    color: Theme.textSecondary
                }
                Label {
                    visible: msgModelLabel.length > 0
                    width: parent.width
                    text: msgModelLabel
                    font.pixelSize: Theme.fontSizeSmall
                    color: Theme.textSecondary
                    opacity: 0.88
                }

                Row {
                    width: parent.width
                    spacing: Theme.spaceSm

                    Rectangle {
                        width: 3
                        height: Math.max(assistantBody.height, 1)
                        radius: 1
                        color: Theme.accentPrimary
                        opacity: msgStreaming ? 0.3 : 0
                    }

                    Label {
                        id: assistantBody
                        width: parent.width - parent.spacing - 3
                        text: msgContent
                        wrapMode: Text.Wrap
                        font.pixelSize: Theme.fontSizeUi + 1
                        lineHeight: Theme.readingAssistantLineHeight
                        lineHeightMode: Text.ProportionalHeight
                        color: Theme.textPrimary
                    }
                }

                Label {
                    visible: msgStreaming
                    width: parent.width
                    text: qsTr("Antwort wird erstellt …")
                    font.pixelSize: Theme.fontSizeSmall
                    font.italic: true
                    color: Theme.textSecondary
                    opacity: 0.92
                }
            }

            Column {
                visible: isSystem
                width: parent.width
                spacing: Theme.spaceXs

                Rectangle {
                    width: parent.width
                    height: 1
                    color: Theme.borderSubtle
                    opacity: 0.3
                }
                Label {
                    width: parent.width
                    text: qsTr("System")
                    font.pixelSize: Theme.fontSizeSmall - 1
                    color: Theme.textSecondary
                    opacity: 0.8
                }
                Label {
                    width: parent.width
                    text: msgContent
                    wrapMode: Text.Wrap
                    font.pixelSize: Theme.fontSizeSmall
                    lineHeight: 1.22
                    lineHeightMode: Text.ProportionalHeight
                    color: Theme.textSecondary
                    opacity: 0.88
                }
            }
        }
    }
}
