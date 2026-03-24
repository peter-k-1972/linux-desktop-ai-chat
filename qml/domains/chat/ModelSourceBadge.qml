import QtQuick
import QtQuick.Controls
import themes 1.0

Column {
    id: root
    width: parent.width
    spacing: Theme.spaceXs

    property string modelText: ""
    property string providerText: ""

    Rectangle {
        width: parent.width
        implicitHeight: innerCol.implicitHeight + 2 * Theme.spaceSm
        radius: Theme.radiusSm
        color: Theme.canvasBase
        opacity: 0.55
        border.width: 0

        Column {
            id: innerCol
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.verticalCenter: parent.verticalCenter
            anchors.margins: Theme.spaceSm
            spacing: Theme.spaceXs
            width: parent.width - 2 * Theme.spaceSm

            Label {
                width: parent.width
                text: qsTr("Modell")
                font.pixelSize: Theme.fontSizeSmall
                color: Theme.textSecondary
            }
            Label {
                width: parent.width
                text: root.modelText.length > 0 ? root.modelText : "—"
                font.pixelSize: Theme.fontSizeUi
                font.weight: Font.Medium
                color: Theme.textOnDark
                wrapMode: Text.Wrap
            }
            Label {
                visible: root.providerText.length > 0
                width: parent.width
                text: qsTr("Quelle · %1").arg(root.providerText)
                font.pixelSize: Theme.fontSizeSmall
                color: Theme.textSecondary
                wrapMode: Text.Wrap
            }
        }
    }
}
