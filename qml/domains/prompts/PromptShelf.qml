import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import themes 1.0

/**
 * Geordnete Regalansicht — vertikale Liste von PromptCards (kein Kartenchaos).
 */
Rectangle {
    id: root
    color: Theme.surfaces.work
    radius: Theme.radiusMd
    border.width: 1
    border.color: Theme.divider.borderSoft

    property var vm

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: Theme.spacing.md
        spacing: Theme.spacing.sm

        RowLayout {
            Layout.fillWidth: true
            spacing: Theme.spacing.sm

            Label {
                text: qsTr("Regal")
                font.pixelSize: Theme.fontSizeTitle
                font.bold: true
                color: Theme.colors.textPrimary
                Layout.fillWidth: true
            }

            Button {
                text: qsTr("Neuer Prompt")
                flat: true
                enabled: vm
                onClicked: {
                    if (vm) {
                        vm.createPrompt();
                    }
                }
            }

            Button {
                text: vm && vm.variantDrawerOpen ? qsTr("Versionen ▾") : qsTr("Versionen ▸")
                flat: true
                enabled: vm && vm.selectedPrompt && vm.selectedPrompt.promptId >= 0
                onClicked: {
                    if (vm) {
                        vm.toggleVariantDrawer();
                    }
                }
            }
        }

        Label {
            visible: vm && vm.activeCollection.length > 0
            text: qsTr("Sammlung: %1").arg(vm ? vm.activeCollection : "")
            font.pixelSize: Theme.fontSizeSmall
            color: Theme.colors.textSecondary
            Layout.fillWidth: true
        }
        Label {
            visible: vm && vm.activeTag.length > 0
            text: qsTr("Tag: %1").arg(vm ? vm.activeTag : "")
            font.pixelSize: Theme.fontSizeSmall
            color: Theme.colors.textSecondary
            Layout.fillWidth: true
        }

        ListView {
            id: shelfList
            Layout.fillWidth: true
            Layout.fillHeight: true
            clip: true
            spacing: Theme.spacing.xs
            model: vm ? vm.prompts : null

            delegate: PromptCard {
                width: shelfList.width
                selected: model.isSelected
                titleText: model.title
                categoryText: model.category
                tagsLine: model.tagsLine

                MouseArea {
                    anchors.fill: parent
                    cursorShape: Qt.PointingHandCursor
                    onClicked: {
                        if (vm) {
                            vm.selectPrompt(model.promptId);
                        }
                    }
                }
            }
        }
    }
}
