import QtQuick
import QtQuick.Controls
import themes 1.0

Item {
    id: root
    property var chatVm

    function _providerDisplay(code) {
        if (code === "local")
            return qsTr("lokal")
        if (code === "cloud")
            return qsTr("Cloud")
        return ""
    }

    function _contextModeDisplay(raw) {
        var t = raw || ""
        if (t === "—" || t.length === 0)
            return "—"
        return t
    }

    Rectangle {
        anchors.fill: parent
        color: Theme.canvasBase
        opacity: 0.35
        radius: Theme.radiusSm
        border.width: 0
    }
    Rectangle {
        anchors.top: parent.top
        anchors.bottom: parent.bottom
        anchors.left: parent.left
        width: 1
        color: Theme.borderSubtle
        opacity: 0.45
    }

    Flickable {
        id: flick
        anchors.fill: parent
        anchors.margins: Theme.spaceMd
        clip: true
        contentWidth: width
        contentHeight: body.implicitHeight
        boundsBehavior: Flickable.StopAtBounds
        ScrollBar.vertical: ScrollBar {
            policy: flick.contentHeight > flick.height ? ScrollBar.AsNeeded : ScrollBar.AlwaysOff
        }

        Column {
            id: body
            width: flick.width
            spacing: Theme.spaceLg

            Label {
                width: parent.width
                text: qsTr("Kontextfläche")
                font.pixelSize: Theme.fontSizeSmall
                font.letterSpacing: 0.4
                color: Theme.textSecondary
            }

            Column {
                width: parent.width
                spacing: Theme.spaceXs

                Label {
                    width: parent.width
                    text: chatVm && chatVm.sessionTitle.length > 0 ? chatVm.sessionTitle : qsTr("Keine Sitzung gewählt")
                    font.pixelSize: Theme.fontSizeUi
                    font.weight: Font.Medium
                    color: Theme.textOnDark
                    wrapMode: Text.Wrap
                }
                Label {
                    width: parent.width
                    visible: chatVm && chatVm.sessionIdCaption.length > 0
                    text: chatVm ? chatVm.sessionIdCaption : ""
                    font.pixelSize: Theme.fontSizeSmall
                    color: Theme.textSecondary
                }
                Label {
                    width: parent.width
                    visible: chatVm && chatVm.sessionActivityLine.length > 0
                    text: chatVm ? chatVm.sessionActivityLine : ""
                    font.pixelSize: Theme.fontSizeSmall
                    color: Theme.textSecondary
                    wrapMode: Text.Wrap
                }
            }

            ContextDivider {
                width: parent.width
            }

            ModelSourceBadge {
                width: parent.width
                modelText: chatVm ? chatVm.activeModel : ""
                providerText: chatVm ? _providerDisplay(chatVm.provider) : ""
            }

            ContextDivider {
                width: parent.width
            }

            ContextKeyValue {
                width: parent.width
                keyText: qsTr("Kontextmodus")
                valueText: chatVm ? _contextModeDisplay(chatVm.contextMode) : "—"
            }

            ContextDivider {
                width: parent.width
            }

            ContextSection {
                width: parent.width
                heading: qsTr("Projekt")
            }
            Label {
                width: parent.width
                text: (chatVm && chatVm.projectName.length > 0) ? chatVm.projectName : qsTr("Globaler Chat")
                font.pixelSize: Theme.fontSizeUi
                color: Theme.textOnDark
                wrapMode: Text.Wrap
            }
            Item {
                width: parent.width
                height: Theme.spaceSm
            }
            ContextSection {
                width: parent.width
                heading: qsTr("Thema")
            }
            Label {
                width: parent.width
                text: (chatVm && chatVm.topicName.length > 0) ? chatVm.topicName : qsTr("Kein Thema")
                font.pixelSize: Theme.fontSizeUi
                color: Theme.textOnDark
                wrapMode: Text.Wrap
            }

            ContextDivider {
                width: parent.width
            }

            ContextSection {
                width: parent.width
                heading: qsTr("Sitzung")
            }
            Label {
                width: parent.width
                text: chatVm ? qsTr("Nachrichten · %1").arg(chatVm.messageCount) : qsTr("Nachrichten · 0")
                font.pixelSize: Theme.fontSizeSmall
                color: Theme.textSecondary
            }
            Label {
                width: parent.width
                visible: chatVm && chatVm.tokenUsageLine.length > 0
                text: chatVm ? chatVm.tokenUsageLine : ""
                font.pixelSize: Theme.fontSizeSmall
                color: Theme.textSecondary
                wrapMode: Text.Wrap
            }
            Label {
                width: parent.width
                visible: chatVm && chatVm.sessionDurationLine.length > 0
                text: chatVm ? chatVm.sessionDurationLine : ""
                font.pixelSize: Theme.fontSizeSmall
                color: Theme.textSecondary
                wrapMode: Text.Wrap
            }
        }
    }
}
