import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import themes 1.0

/**
 * Vertikaler Katalog: Suche, Sammlungen (Kategorien), Tags.
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
        anchors.margins: Theme.spaceSm
        spacing: Theme.spaceSm

        Label {
            text: qsTr("Katalog")
            font.pixelSize: Theme.fontSizeSmall
            font.bold: true
            color: Theme.textOnDark
            Layout.fillWidth: true
        }

        TextField {
            id: searchField
            Layout.fillWidth: true
            placeholderText: qsTr("Suche …")
            text: vm ? vm.searchText : ""
            onTextChanged: {
                if (vm && text !== vm.searchText) {
                    vm.searchText = text;
                }
            }
            Component.onCompleted: {
                if (vm) {
                    searchField.text = vm.searchText;
                }
            }
            Connections {
                target: vm
                function onSearchTextChanged() {
                    if (vm && searchField.text !== vm.searchText) {
                        searchField.text = vm.searchText;
                    }
                }
            }
        }

        Label {
            text: qsTr("Sammlungen")
            font.pixelSize: Theme.typography.caption.pixelSize
            color: Theme.colors.textSecondary
            Layout.fillWidth: true
        }

        ListView {
            id: colList
            Layout.fillWidth: true
            Layout.preferredHeight: Math.min(160, contentHeight)
            clip: true
            spacing: Theme.spaceXs
            model: vm ? vm.collections : null

            delegate: Rectangle {
                required property string display

                width: colList.width
                height: Math.max(Theme.spaceLg + Theme.spaceSm, rowLbl.implicitHeight + Theme.spaceSm)
                radius: Theme.radiusSm
                color: vm && display === vm.activeCollection
                    ? Qt.rgba(Theme.accentPrimary.r, Theme.accentPrimary.g, Theme.accentPrimary.b, 0.2)
                    : "transparent"

                Label {
                    id: rowLbl
                    anchors.left: parent.left
                    anchors.right: parent.right
                    anchors.verticalCenter: parent.verticalCenter
                    anchors.leftMargin: Theme.spaceSm
                    anchors.rightMargin: Theme.spaceSm
                    text: display.length > 0 ? display : qsTr("Alle Sammlungen")
                    font.pixelSize: Theme.fontSizeSmall
                    color: Theme.textOnDark
                    elide: Text.ElideRight
                }

                MouseArea {
                    anchors.fill: parent
                    cursorShape: Qt.PointingHandCursor
                    onClicked: {
                        if (vm) {
                            vm.setActiveCollection(display);
                        }
                    }
                }
            }
        }

        Label {
            text: qsTr("Tags")
            font.pixelSize: Theme.typography.caption.pixelSize
            color: Theme.colors.textSecondary
            Layout.fillWidth: true
        }

        ListView {
            id: tagList
            Layout.fillWidth: true
            Layout.fillHeight: true
            clip: true
            spacing: Theme.spaceXs
            model: vm ? vm.tags : null

            delegate: Rectangle {
                required property string display

                width: tagList.width
                height: Math.max(Theme.spaceLg, tagLbl.implicitHeight + Theme.spaceXs)
                radius: Theme.radiusSm
                color: vm && display === vm.activeTag
                    ? Qt.rgba(Theme.accentSecondary.r, Theme.accentSecondary.g, Theme.accentSecondary.b, 0.18)
                    : "transparent"

                Label {
                    id: tagLbl
                    anchors.left: parent.left
                    anchors.right: parent.right
                    anchors.verticalCenter: parent.verticalCenter
                    anchors.leftMargin: Theme.spaceSm
                    text: display.length > 0 ? ("# " + display) : qsTr("Alle Tags")
                    font.pixelSize: Theme.fontSizeSmall
                    color: Theme.textOnDark
                    elide: Text.ElideRight
                }

                MouseArea {
                    anchors.fill: parent
                    cursorShape: Qt.PointingHandCursor
                    onClicked: {
                        if (vm) {
                            vm.setActiveTag(display);
                        }
                    }
                }
            }
        }
    }
}
