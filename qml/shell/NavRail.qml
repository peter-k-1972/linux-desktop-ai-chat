import QtQuick
import QtQuick.Controls
import themes 1.0

Rectangle {
    id: root
    color: Theme.surfaces.architectural
    border.width: 0

    property var shellBridge

    ListView {
        id: navList
        anchors.fill: parent
        anchors.topMargin: Theme.spacing.lg
        anchors.bottomMargin: Theme.spacing.md
        spacing: Theme.spacing.xs
        model: shellBridge ? shellBridge.domainNavModel : null
        clip: true

        delegate: Rectangle {
            width: navList.width
            height: navLabel.implicitHeight + Theme.spacing.md
            radius: Theme.radius.sm
            color: shellBridge && shellBridge.activeDomain === model.domainId
                ? Theme.surfaces.panelSide
                : Theme.colors.transparent
            border.width: shellBridge && shellBridge.activeDomain === model.domainId ? 1 : 0
            border.color: Theme.states.focusRing

            Label {
                id: navLabel
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.verticalCenter: parent.verticalCenter
                anchors.leftMargin: Theme.spacing.sm
                anchors.rightMargin: Theme.spacing.sm
                text: model.label
                font.pixelSize: Theme.typography.body.pixelSize
                color: Theme.colors.textOnDarkPrimary
                elide: Text.ElideRight
                wrapMode: Text.NoWrap
            }

            MouseArea {
                anchors.fill: parent
                cursorShape: Qt.PointingHandCursor
                onClicked: {
                    if (shellBridge) {
                        shellBridge.requestDomainChange(model.domainId)
                    }
                }
            }
        }
    }
}
