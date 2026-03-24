import QtQuick
import QtQuick.Controls
import themes 1.0

/**
 * Ein „Buchrücken“ / Band auf dem Regal.
 */
Rectangle {
    id: root
    height: spine.implicitHeight + Theme.spaceMd * 2
    radius: Theme.radiusSm
    color: root.selected
        ? Qt.rgba(Theme.accentPrimary.r, Theme.accentPrimary.g, Theme.accentPrimary.b, 0.22)
        : Theme.surfaceWork
    border.width: 1
    border.color: root.selected ? Theme.states.focusRing : Theme.borderSubtle

    property bool selected: false
    property string titleText: ""
    property string categoryText: ""
    property string tagsLine: ""

    Column {
        id: spine
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.verticalCenter: parent.verticalCenter
        anchors.leftMargin: Theme.spaceMd
        anchors.rightMargin: Theme.spaceMd
        spacing: Theme.spaceXs

        Label {
            width: parent.width
            text: root.titleText
            font.pixelSize: Theme.typography.body.pixelSize
            font.bold: true
            color: Theme.colors.textPrimary
            elide: Text.ElideRight
        }
        Label {
            width: parent.width
            visible: root.categoryText.length > 0
            text: root.categoryText
            font.pixelSize: Theme.fontSizeSmall
            color: Theme.colors.textSecondary
            elide: Text.ElideRight
        }
        Label {
            width: parent.width
            visible: root.tagsLine.length > 0
            text: root.tagsLine
            font.pixelSize: Theme.typography.caption.pixelSize
            color: Theme.colors.textSecondary
            elide: Text.ElideRight
            wrapMode: Text.WordWrap
            maximumLineCount: 2
        }
    }
}
