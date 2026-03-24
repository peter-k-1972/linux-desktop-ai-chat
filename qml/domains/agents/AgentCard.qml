import QtQuick
import QtQuick.Controls
import themes 1.0

/**
 * Ein Agent auf der Dienstliste (Bibliothekar-Karte).
 */
Rectangle {
    id: root
    height: col.implicitHeight + Theme.spaceMd * 2
    radius: Theme.radiusSm
    color: root.selected
        ? Qt.rgba(Theme.accentPrimary.r, Theme.accentPrimary.g, Theme.accentPrimary.b, 0.2)
        : Theme.surfaceWork
    border.width: 1
    border.color: root.selected ? Theme.states.focusRing : Theme.borderSubtle

    property bool selected: false
    property string nameText: ""
    property string roleText: ""
    property string modelText: ""
    property string statusText: ""

    Column {
        id: col
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.verticalCenter: parent.verticalCenter
        anchors.leftMargin: Theme.spaceMd
        anchors.rightMargin: Theme.spaceMd
        spacing: Theme.spaceXs

        Label {
            width: parent.width
            text: root.nameText
            font.pixelSize: Theme.typography.body.pixelSize
            font.bold: true
            color: Theme.colors.textPrimary
            elide: Text.ElideRight
        }
        Label {
            width: parent.width
            text: qsTr("Rolle: %1").arg(root.roleText)
            font.pixelSize: Theme.fontSizeSmall
            color: Theme.colors.textSecondary
            elide: Text.ElideRight
        }
        Label {
            width: parent.width
            text: qsTr("Modell: %1").arg(root.modelText)
            font.pixelSize: Theme.typography.caption.pixelSize
            color: Theme.colors.textSecondary
            elide: Text.ElideRight
        }
        Label {
            width: parent.width
            text: qsTr("Status: %1").arg(root.statusText)
            font.pixelSize: Theme.typography.caption.pixelSize
            color: Theme.accentSecondary
            elide: Text.ElideRight
        }
    }
}
