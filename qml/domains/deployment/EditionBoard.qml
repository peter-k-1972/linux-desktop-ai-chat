import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import themes 1.0

/**
 * OBEN: Releases und Versionen (Auflagen).
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
        spacing: Theme.spacing.sm

        RowLayout {
            Layout.fillWidth: true
            spacing: Theme.spacing.sm

            Label {
                text: qsTr("Auflagen")
                font.pixelSize: Theme.fontSizeTitle
                font.bold: true
                color: Theme.colors.textPrimary
                Layout.fillWidth: true
            }

            Button {
                text: qsTr("Aktualisieren")
                flat: true
                onClicked: {
                    if (vm) {
                        vm.reloadDeployments();
                    }
                }
            }
        }

        Label {
            text: vm && vm.selectedReleaseId.length > 0
                ? qsTr("Gewählt: %1").arg(vm.selectedReleaseId)
                : qsTr("Release auswählen — Version siehe Spalte „Version“")
            font.pixelSize: Theme.fontSizeSmall
            color: Theme.colors.textSecondary
            elide: Text.ElideRight
            Layout.fillWidth: true
        }

        ListView {
            id: relList
            Layout.fillWidth: true
            Layout.fillHeight: true
            clip: true
            spacing: Theme.spacing.xs
            model: vm ? vm.releases : null

            delegate: Rectangle {
                required property string releaseId
                required property string displayName
                required property string versionLabel
                required property string lifecycle
                required property string artifactKind
                required property string artifactRef
                required property bool isSelected

                width: relList.width
                height: rowCol.implicitHeight + Theme.spacing.sm * 2
                radius: Theme.radiusSm
                color: isSelected
                    ? Qt.rgba(Theme.accentPrimary.r, Theme.accentPrimary.g, Theme.accentPrimary.b, 0.18)
                    : Theme.surfaceWork
                border.width: 1
                border.color: isSelected ? Theme.states.focusRing : Theme.borderSubtle

                ColumnLayout {
                    id: rowCol
                    anchors.left: parent.left
                    anchors.right: parent.right
                    anchors.verticalCenter: parent.verticalCenter
                    anchors.leftMargin: Theme.spacing.sm
                    anchors.rightMargin: Theme.spacing.sm
                    spacing: Theme.spacing.xs

                    Label {
                        text: displayName + " · " + versionLabel
                        font.pixelSize: Theme.typography.body.pixelSize
                        font.bold: true
                        color: Theme.colors.textPrimary
                        elide: Text.ElideRight
                        Layout.fillWidth: true
                    }
                    Label {
                        text: qsTr("Status: %1").arg(lifecycle)
                        font.pixelSize: Theme.fontSizeSmall
                        color: Theme.colors.textSecondary
                        Layout.fillWidth: true
                    }
                    Label {
                        text: qsTr("Artefakt: %1 — %2").arg(artifactKind).arg(artifactRef)
                        font.pixelSize: Theme.typography.caption.pixelSize
                        color: Theme.colors.textSecondary
                        elide: Text.ElideRight
                        Layout.fillWidth: true
                    }
                }

                MouseArea {
                    anchors.fill: parent
                    cursorShape: Qt.PointingHandCursor
                    onClicked: {
                        if (vm) {
                            vm.selectRelease(releaseId);
                        }
                    }
                }
            }
        }
    }
}
