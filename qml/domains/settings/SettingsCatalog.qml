import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import themes 1.0

/**
 * LINKS: Archivnavigation — Provider, Kontext, Erscheinung, Richtlinien.
 */
Rectangle {
    id: root
    color: Theme.canvasElevated
    radius: Theme.radiusMd
    border.width: 1
    border.color: Theme.borderSubtle

    property var vm

    ListModel {
        id: catModel
        ListElement {
            sid: "providers"
            title: "Providers"
        }
        ListElement {
            sid: "context"
            title: "Context"
        }
        ListElement {
            sid: "appearance"
            title: "Appearance"
        }
        ListElement {
            sid: "policies"
            title: "Policies"
        }
    }

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: Theme.spacing.sm
        spacing: Theme.spacing.sm

        Label {
            text: qsTr("Katalog")
            font.pixelSize: Theme.fontSizeSmall
            font.bold: true
            color: Theme.textOnDark
            Layout.fillWidth: true
        }

        ListView {
            id: catList
            Layout.fillWidth: true
            Layout.fillHeight: true
            clip: true
            spacing: Theme.spacing.xs
            model: catModel

            delegate: Rectangle {
                width: catList.width
                height: Math.max(Theme.sizing.listRowHeightComfortable, catLbl.implicitHeight + Theme.spacing.md)
                radius: Theme.radiusSm
                color: vm && vm.activeSection === model.sid ? Theme.surfaces.panelSide : "transparent"
                border.width: vm && vm.activeSection === model.sid ? 1 : 0
                border.color: Theme.states.focusRing

                Label {
                    id: catLbl
                    anchors.left: parent.left
                    anchors.right: parent.right
                    anchors.verticalCenter: parent.verticalCenter
                    anchors.leftMargin: Theme.spacing.sm
                    text: model.title
                    font.pixelSize: Theme.typography.body.pixelSize
                    color: Theme.colors.textOnDarkPrimary
                    elide: Text.ElideRight
                }

                MouseArea {
                    anchors.fill: parent
                    cursorShape: Qt.PointingHandCursor
                    onClicked: {
                        if (vm) {
                            vm.selectSection(model.sid);
                        }
                    }
                }
            }
        }
    }
}
