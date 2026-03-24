import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import themes 1.0

/**
 * Untere Leiste: gespeicherte Editionen (Versionen) des gewählten Prompts.
 */
Rectangle {
    id: root
    implicitHeight: drawerCol.implicitHeight + Theme.spacing.md * 2
    color: Theme.surfaceMuted
    radius: Theme.radiusSm
    border.width: 1
    border.color: Theme.borderSubtle

    property var vm

    ColumnLayout {
        id: drawerCol
        anchors.fill: parent
        anchors.margins: Theme.spacing.md
        spacing: Theme.spacing.xs

        Label {
            text: qsTr("Editionen (Versionen)")
            font.pixelSize: Theme.fontSizeSmall
            font.bold: true
            color: Theme.colors.textPrimary
            Layout.fillWidth: true
        }

        ListView {
            id: vlist
            Layout.fillWidth: true
            Layout.preferredHeight: Math.min(140, Math.max(48, contentHeight))
            orientation: ListView.Horizontal
            clip: true
            spacing: Theme.spacing.sm
            model: vm ? vm.variants : null

            delegate: Rectangle {
                required property string version
                required property string title
                required property string subtitle
                required property string content

                width: 200
                height: vlist.height
                radius: Theme.radiusSm
                color: Theme.surfaceWork
                border.width: 1
                border.color: Theme.borderSubtle

                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: Theme.spacing.sm
                    spacing: Theme.spaceXs

                    Label {
                        text: qsTr("v%1").arg(version)
                        font.pixelSize: Theme.fontSizeSmall
                        font.bold: true
                        color: Theme.colors.textPrimary
                        Layout.fillWidth: true
                        elide: Text.ElideRight
                    }
                    Label {
                        text: title
                        font.pixelSize: Theme.typography.caption.pixelSize
                        color: Theme.colors.textSecondary
                        Layout.fillWidth: true
                        elide: Text.ElideRight
                    }
                    Label {
                        text: subtitle
                        font.pixelSize: Theme.typography.caption.pixelSize
                        color: Theme.colors.textSecondary
                        Layout.fillWidth: true
                    }
                    Button {
                        text: qsTr("Inhalt übernehmen")
                        flat: true
                        Layout.fillWidth: true
                        onClicked: {
                            if (vm) {
                                vm.applyVersionContent(version, content);
                            }
                        }
                    }
                }
            }
        }
    }
}
