import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import themes 1.0

Rectangle {
    id: root
    color: Theme.surfaces.architectural
    border.width: 0

    property var shellBridge

    ScrollView {
        anchors.fill: parent
        anchors.topMargin: Theme.spacing.lg
        anchors.bottomMargin: Theme.spacing.md
        clip: true

        ColumnLayout {
            width: root.width - Theme.spacing.sm * 2
            spacing: Theme.spacing.sm

            Label {
                text: qsTr("Bereiche")
                font.pixelSize: Theme.typography.caption.pixelSize
                color: Theme.colors.textOnDarkSecondary
                Layout.leftMargin: Theme.spacing.sm
            }

            ListView {
                id: navList
                Layout.fillWidth: true
                Layout.preferredHeight: contentHeight
                interactive: false
                model: shellBridge ? shellBridge.domainNavModel : null
                spacing: Theme.spacing.xs

                delegate: Rectangle {
                    width: navList.width
                    height: navLabel.implicitHeight + Theme.spacing.md
                    radius: Theme.radius.sm
                    color: shellBridge && shellBridge.activeTopArea === model.areaId
                        ? Theme.surfaces.panelSide
                        : Theme.colors.transparent
                    border.width: shellBridge && shellBridge.activeTopArea === model.areaId ? 1 : 0
                    border.color: Theme.states.focusRing

                    Label {
                        id: navLabel
                        anchors.left: parent.left
                        anchors.right: parent.right
                        anchors.verticalCenter: parent.verticalCenter
                        anchors.leftMargin: Theme.spacing.sm
                        anchors.rightMargin: Theme.spacing.sm
                        text: model.label
                        font.pixelSize: Theme.typography.body.pixelSize
                        color: Theme.colors.textOnDarkPrimary
                        elide: Text.ElideRight
                        wrapMode: Text.NoWrap
                    }

                    MouseArea {
                        anchors.fill: parent
                        cursorShape: Qt.PointingHandCursor
                        onClicked: {
                            if (shellBridge)
                                shellBridge.requestTopAreaChange(model.areaId)
                        }
                    }
                }
            }

            Rectangle {
                Layout.fillWidth: true
                Layout.preferredHeight: 1
                visible: workspaceList.count > 0
                color: Theme.divider.line
                opacity: Theme.divider.lineOpacity
            }

            Label {
                visible: workspaceList.count > 0
                text: qsTr("Operations — Workspaces")
                font.pixelSize: Theme.typography.caption.pixelSize
                color: Theme.colors.textOnDarkSecondary
                Layout.leftMargin: Theme.spacing.sm
            }

            ListView {
                id: workspaceList
                Layout.fillWidth: true
                Layout.preferredHeight: contentHeight
                visible: count > 0
                interactive: false
                model: shellBridge ? shellBridge.workspaceNavModel : null
                spacing: Theme.spacing.xs

                delegate: Rectangle {
                    width: workspaceList.width
                    height: wsLabel.implicitHeight + Theme.spacing.md
                    radius: Theme.radius.sm
                    color: shellBridge && shellBridge.activeWorkspaceId === model.workspaceId
                        ? Theme.surfaces.panelSide
                        : Theme.colors.transparent
                    border.width: shellBridge && shellBridge.activeWorkspaceId === model.workspaceId ? 1 : 0
                    border.color: Theme.states.focusRing

                    Label {
                        id: wsLabel
                        anchors.left: parent.left
                        anchors.right: parent.right
                        anchors.verticalCenter: parent.verticalCenter
                        anchors.leftMargin: Theme.spacing.sm
                        anchors.rightMargin: Theme.spacing.sm
                        text: model.label
                        font.pixelSize: Theme.typography.caption.pixelSize
                        color: Theme.colors.textOnDarkPrimary
                        elide: Text.ElideRight
                        wrapMode: Text.NoWrap
                    }

                    MouseArea {
                        anchors.fill: parent
                        cursorShape: Qt.PointingHandCursor
                        onClicked: {
                            if (shellBridge)
                                shellBridge.requestOperationsWorkspaceChange(model.workspaceId)
                        }
                    }
                }
            }
        }
    }
}
