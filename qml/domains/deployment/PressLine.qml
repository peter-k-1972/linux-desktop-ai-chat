import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import themes 1.0

/**
 * MITTE: Pressestraße — Build, Validate, Package, Publish.
 */
Rectangle {
    id: root
    color: Theme.surfaces.work
    radius: Theme.radiusMd
    border.width: 1
    border.color: Theme.divider.borderSoft

    property var vm

    function stepColor(state) {
        if (state === "running")
            return Theme.accentSecondary;
        if (state === "done")
            return Theme.states.success;
        if (state === "error")
            return Theme.states.error;
        return Theme.colors.textSecondary;
    }

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: Theme.spacing.md
        spacing: Theme.spacing.md

        Label {
            text: qsTr("Pressestraße")
            font.pixelSize: Theme.fontSizeTitle
            font.bold: true
            color: Theme.colors.textPrimary
            Layout.fillWidth: true
        }

        RowLayout {
            Layout.fillWidth: true
            spacing: Theme.spacing.sm
            Button {
                text: qsTr("Pipeline starten (draft → ready)")
                enabled: vm && !vm.buildBusy && vm.selectedReleaseId.length > 0
                onClicked: {
                    if (vm) {
                        vm.buildRelease();
                    }
                }
            }
            Button {
                text: qsTr("Veröffentlichen (Rollout)")
                flat: true
                enabled: vm && !vm.buildBusy && vm.selectedReleaseId.length > 0
                onClicked: {
                    if (vm) {
                        vm.publishRelease();
                    }
                }
            }
        }

        ListView {
            id: stepList
            Layout.fillWidth: true
            Layout.fillHeight: true
            spacing: Theme.spacing.md
            model: vm ? vm.builds : null

            delegate: RowLayout {
                required property string stepId
                required property string label
                required property string state

                width: stepList.width
                spacing: Theme.spacing.md

                Rectangle {
                    Layout.preferredWidth: 36
                    Layout.preferredHeight: 36
                    radius: width / 2
                    color: Theme.surfaceMuted
                    border.width: 2
                    border.color: root.stepColor(state)

                    Label {
                        anchors.centerIn: parent
                        text: state === "done" ? "✓" : (state === "running" ? "…" : "")
                        font.bold: true
                        color: root.stepColor(state)
                    }
                }

                ColumnLayout {
                    Layout.fillWidth: true
                    spacing: Theme.spacing.xs

                    Label {
                        text: label
                        font.pixelSize: Theme.typography.body.pixelSize
                        font.bold: true
                        color: Theme.colors.textPrimary
                        Layout.fillWidth: true
                    }
                    Label {
                        text: state === "idle" ? qsTr("Wartet") : (state === "running" ? qsTr("Läuft …") : (state === "done" ? qsTr("Fertig") : state))
                        font.pixelSize: Theme.fontSizeSmall
                        color: Theme.colors.textSecondary
                        Layout.fillWidth: true
                    }
                }
            }
        }
    }
}
