import QtQuick
import QtQuick.Controls
import themes 1.0

Column {
    id: root
    width: parent.width
    spacing: 2

    property string keyText: ""
    property string valueText: ""
    property bool valueBold: false
    property int valueSize: Theme.fontSizeUi

    Label {
        visible: root.keyText.length > 0
        width: parent.width
        text: root.keyText
        font.pixelSize: Theme.fontSizeSmall
        font.weight: Font.Normal
        color: Theme.textSecondary
        wrapMode: Text.Wrap
    }
    Label {
        width: parent.width
        text: root.valueText.length > 0 ? root.valueText : "—"
        font.pixelSize: root.valueSize
        font.weight: root.valueBold ? Font.Medium : Font.Normal
        color: Theme.textOnDark
        wrapMode: Text.Wrap
    }
}
