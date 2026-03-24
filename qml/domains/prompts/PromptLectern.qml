import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import themes 1.0

/**
 * Lesepult — ruhiger Editor ohne IDE-Überladung.
 */
Rectangle {
    id: root
    color: Theme.canvasElevated
    radius: Theme.radiusMd
    border.width: 1
    border.color: Theme.borderSubtle

    property var vm

    ScrollView {
        anchors.fill: parent
        anchors.margins: Theme.spacing.md
        clip: true

        ColumnLayout {
            width: parent.width
            spacing: Theme.spacing.md

            Label {
                text: qsTr("Lesepult")
                font.pixelSize: Theme.fontSizeSmall
                font.bold: true
                color: Theme.textOnDark
                Layout.fillWidth: true
            }

            Label {
                visible: !vm || !vm.selectedPrompt || vm.selectedPrompt.promptId < 0
                text: qsTr("Wählen Sie links ein Prompt aus dem Regal.")
                font.pixelSize: Theme.fontSizeSmall
                color: Theme.colors.textSecondary
                wrapMode: Text.Wrap
                Layout.fillWidth: true
            }

            ColumnLayout {
                visible: vm && vm.selectedPrompt && vm.selectedPrompt.promptId >= 0
                Layout.fillWidth: true
                spacing: Theme.spacing.sm

                TextField {
                    id: titleField
                    Layout.fillWidth: true
                    placeholderText: qsTr("Titel")
                    text: vm && vm.selectedPrompt ? vm.selectedPrompt.title : ""
                    onTextChanged: {
                        if (vm && vm.selectedPrompt && text !== vm.selectedPrompt.title) {
                            vm.selectedPrompt.title = text;
                        }
                    }
                    Connections {
                        target: vm && vm.selectedPrompt ? vm.selectedPrompt : null
                        function onTitleChanged() {
                            if (vm && vm.selectedPrompt && titleField.text !== vm.selectedPrompt.title) {
                                titleField.text = vm.selectedPrompt.title;
                            }
                        }
                    }
                }

                Label {
                    text: qsTr("Beschreibung")
                    font.pixelSize: Theme.typography.caption.pixelSize
                    color: Theme.colors.textSecondary
                    Layout.fillWidth: true
                }

                TextArea {
                    id: descArea
                    Layout.fillWidth: true
                    Layout.preferredHeight: 72
                    wrapMode: TextArea.Wrap
                    placeholderText: qsTr("Kurzbeschreibung …")
                    text: vm && vm.selectedPrompt ? vm.selectedPrompt.description : ""
                    onTextChanged: {
                        if (vm && vm.selectedPrompt && text !== vm.selectedPrompt.description) {
                            vm.selectedPrompt.description = text;
                        }
                    }
                    Connections {
                        target: vm && vm.selectedPrompt ? vm.selectedPrompt : null
                        function onDescriptionChanged() {
                            if (vm && vm.selectedPrompt && descArea.text !== vm.selectedPrompt.description) {
                                descArea.text = vm.selectedPrompt.description;
                            }
                        }
                    }
                }

                RowLayout {
                    Layout.fillWidth: true
                    spacing: Theme.spacing.sm

                    Label {
                        text: qsTr("Variablen")
                        font.pixelSize: Theme.typography.caption.pixelSize
                        color: Theme.colors.textSecondary
                    }
                    Label {
                        Layout.fillWidth: true
                        text: vm && vm.selectedPrompt ? vm.selectedPrompt.variables : ""
                        font.pixelSize: Theme.fontSizeSmall
                        color: Theme.colors.textPrimary
                        wrapMode: Text.Wrap
                    }
                }

                Label {
                    text: qsTr("Prompt-Text")
                    font.pixelSize: Theme.typography.caption.pixelSize
                    color: Theme.colors.textSecondary
                    Layout.fillWidth: true
                }

                TextArea {
                    id: bodyArea
                    Layout.fillWidth: true
                    Layout.preferredHeight: 220
                    wrapMode: TextArea.Wrap
                    placeholderText: qsTr("Hier den Prompt schreiben … Platzhalter: {name}")
                    text: vm && vm.selectedPrompt ? vm.selectedPrompt.content : ""
                    selectByMouse: true
                    onTextChanged: {
                        if (vm && vm.selectedPrompt && text !== vm.selectedPrompt.content) {
                            vm.selectedPrompt.content = text;
                        }
                    }
                    Connections {
                        target: vm && vm.selectedPrompt ? vm.selectedPrompt : null
                        function onContentChanged() {
                            if (vm && vm.selectedPrompt && bodyArea.text !== vm.selectedPrompt.content) {
                                bodyArea.text = vm.selectedPrompt.content;
                            }
                        }
                    }
                }

                Button {
                    text: qsTr("Speichern")
                    Layout.alignment: Qt.AlignRight
                    enabled: vm && vm.selectedPrompt && vm.selectedPrompt.promptId >= 0
                    onClicked: {
                        if (vm) {
                            vm.savePrompt();
                        }
                    }
                }
            }
        }
    }
}
