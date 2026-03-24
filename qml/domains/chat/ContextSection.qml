import QtQuick
import QtQuick.Controls
import themes 1.0

Item {
    id: root
    implicitHeight: headingLabel.implicitHeight
    property string heading: ""

    Label {
        id: headingLabel
        anchors.left: parent.left
        anchors.right: parent.right
        visible: root.heading.length > 0
        text: root.heading
        font.pixelSize: Theme.fontSizeSmall
        font.weight: Font.Normal
        font.letterSpacing: 0.3
        color: Theme.textSecondary
        wrapMode: Text.Wrap
    }
}
