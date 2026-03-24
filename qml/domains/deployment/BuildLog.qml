import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import themes 1.0

/**
 * UNTEN: Setzerei-Log.
 */
Rectangle {
    id: root
    color: Theme.surfaceMuted
    radius: Theme.radiusSm
    border.width: 1
    border.color: Theme.borderSubtle

    property var vm

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: Theme.spacing.sm
        spacing: Theme.spacing.xs

        Label {
            text: qsTr("Setzerei-Log")
            font.pixelSize: Theme.fontSizeSmall
            font.bold: true
            color: Theme.colors.textPrimary
            Layout.fillWidth: true
        }

        ListView {
            id: logList
            Layout.fillWidth: true
            Layout.fillHeight: true
            clip: true
            spacing: 2
            model: vm ? vm.buildLog : null

            delegate: RowLayout {
                required property string message
                required property string timeLabel

                width: logList.width
                spacing: Theme.spacing.sm

                Label {
                    text: timeLabel
                    font.pixelSize: Theme.typography.caption.pixelSize
                    color: Theme.colors.textSecondary
                    Layout.preferredWidth: 64
                }
                Label {
                    text: message
                    font.pixelSize: Theme.fontSizeSmall
                    color: Theme.colors.textPrimary
                    wrapMode: Text.Wrap
                    Layout.fillWidth: true
                }
            }
        }
    }
}
