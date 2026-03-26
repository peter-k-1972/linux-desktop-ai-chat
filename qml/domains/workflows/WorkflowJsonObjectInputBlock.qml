import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import themes 1.0

/**
 * Nur Darstellung: monospace JSON-Feld + Beschriftung.
 * Kein ViewModel — Eltern binden ``text`` und eigene Connections (Test-Run vs. Re-Run strikt getrennt).
 */
ColumnLayout {
    id: root
    property string caption: ""
    property string placeholderText: ""
    property int boxHeight: 120
    /// Für Tests (QQmlApplicationEngine / findChild)
    property string areaObjectName: ""
    property alias text: jsonTextArea.text

    spacing: Theme.spacing.xs
    Layout.fillWidth: true

    Label {
        visible: root.caption.length > 0
        text: root.caption
        font.pixelSize: Theme.typography.caption.pixelSize
        color: Theme.colors.textSecondary
        Layout.fillWidth: true
    }

    ScrollView {
        Layout.fillWidth: true
        Layout.preferredHeight: root.boxHeight
        TextArea {
            id: jsonTextArea
            objectName: root.areaObjectName.length > 0 ? root.areaObjectName : ""
            wrapMode: Text.Wrap
            font.family: "monospace"
            font.pixelSize: Theme.typography.caption.pixelSize
            placeholderText: root.placeholderText
        }
    }
}
