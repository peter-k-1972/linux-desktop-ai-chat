import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import themes 1.0

/**
 * Abschnittskopf für den Projekt-Überblick (War-Room).
 */
ColumnLayout {
    id: root
    property string titleText: ""

    spacing: Theme.spacing.xs
    Layout.fillWidth: true

    Rectangle {
        Layout.fillWidth: true
        height: 1
        color: Theme.divider.line
        opacity: Theme.divider.lineOpacity
    }

    Label {
        text: root.titleText
        font.bold: true
        font.pixelSize: Theme.typography.body.pixelSize
        color: Theme.colors.textPrimary
        Layout.fillWidth: true
        Layout.topMargin: Theme.spacing.xs
    }
}
