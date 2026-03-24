import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import themes 1.0

/**
 * RECHTS: Vorschau / Kurzfassung (Archiv-Karteikarte).
 */
Rectangle {
    id: root
    color: Theme.canvasElevated
    radius: Theme.radiusMd
    border.width: 1
    border.color: Theme.borderSubtle

    property var vm

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: Theme.spacing.md
        spacing: Theme.spacing.md

        Label {
            text: qsTr("Vorschau")
            font.pixelSize: Theme.fontSizeSmall
            font.bold: true
            color: Theme.textOnDark
            Layout.fillWidth: true
        }

        Rectangle {
            Layout.fillWidth: true
            Layout.fillHeight: true
            radius: Theme.radiusSm
            color: Theme.surfaceMuted
            border.width: 1
            border.color: Theme.borderSubtle

            ColumnLayout {
                anchors.fill: parent
                anchors.margins: Theme.spacing.md
                spacing: Theme.spacing.sm

                Label {
                    text: qsTr("Aktives Erscheinungsbild")
                    font.pixelSize: Theme.typography.caption.pixelSize
                    color: Theme.colors.textSecondary
                    Layout.fillWidth: true
                }

                Label {
                    text: vm ? vm.previewText : ""
                    font.pixelSize: Theme.fontSizeSmall
                    color: Theme.colors.textPrimary
                    wrapMode: Text.Wrap
                    Layout.fillWidth: true
                }

                Rectangle {
                    Layout.fillWidth: true
                    Layout.preferredHeight: 72
                    radius: Theme.radiusSm
                    color: Theme.surfaces.work
                    border.width: 1
                    border.color: Theme.divider.borderSoft

                    Label {
                        anchors.centerIn: parent
                        anchors.leftMargin: Theme.spacing.sm
                        anchors.rightMargin: Theme.spacing.sm
                        width: parent.width - Theme.spacing.md * 2
                        text: qsTr("Beispieltext — so wirkt Kontrast und Typografie im Arbeitsbereich.")
                        horizontalAlignment: Text.AlignHCenter
                        wrapMode: Text.Wrap
                        font.pixelSize: Theme.typography.body.pixelSize
                        color: Theme.colors.textPrimary
                    }
                }
            }
        }
    }
}
