import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import themes 1.0

/**
 * MITTE: strukturiertes Ledger (Abschnitte über Katalog), kein Formularwüstling.
 */
Rectangle {
    id: root
    color: Theme.surfaces.work
    radius: Theme.radiusMd
    border.width: 1
    border.color: Theme.divider.borderSoft

    property var vm

    // 0 = Provider, 1 = Erscheinung, 2 = Kontext + Richtlinien (ein Modell ``policies``)
    property int sectionIndex: {
        if (!vm) {
            return 0;
        }
        if (vm.activeSection === "appearance") {
            return 1;
        }
        if (vm.activeSection === "context" || vm.activeSection === "policies") {
            return 2;
        }
        return 0;
    }

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: Theme.spacing.md
        spacing: Theme.spacing.sm

        RowLayout {
            Layout.fillWidth: true
            spacing: Theme.spacing.sm

            Label {
                text: qsTr("Hauptbuch")
                font.pixelSize: Theme.fontSizeTitle
                font.bold: true
                color: Theme.colors.textPrimary
                Layout.fillWidth: true
            }

            Button {
                text: qsTr("Zurücksetzen")
                flat: true
                enabled: vm && vm.dirty
                onClicked: {
                    if (vm) {
                        vm.reloadSettings();
                    }
                }
            }

            Button {
                text: qsTr("Speichern")
                enabled: vm && vm.dirty
                onClicked: {
                    if (vm) {
                        vm.saveSettings();
                    }
                }
            }
        }

        Label {
            text: qsTr("Werte anpassen; Speichern schreibt in die persistenten Einstellungen.")
            font.pixelSize: Theme.typography.caption.pixelSize
            color: Theme.colors.textSecondary
            wrapMode: Text.Wrap
            Layout.fillWidth: true
        }

        StackLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            currentIndex: root.sectionIndex

            ListView {
                id: provList
                clip: true
                spacing: Theme.spacing.md
                model: vm ? vm.providers : null
                delegate: ledgerRowDelegate
            }

            ListView {
                clip: true
                spacing: Theme.spacing.md
                model: vm ? vm.appearance : null
                delegate: ledgerRowDelegate
            }

            ListView {
                id: policiesList
                clip: true
                spacing: Theme.spacing.md
                model: vm ? vm.policies : null
                delegate: ledgerRowDelegate
            }
        }
    }

    Component {
        id: ledgerRowDelegate

        ColumnLayout {
            required property string settingKey
            required property string label
            required property string value
            required property string kind
            required property string options
            required property string description

            width: ListView.view ? ListView.view.width : implicitWidth
            spacing: Theme.spacing.xs

            property string _valueMirror: value
            on_ValueMirrorChanged: {
                if (kind === "enum" && enumBox) {
                    Qt.callLater(function () {
                        enumBox.syncIndex();
                    });
                }
            }

            Label {
                visible: kind === "section"
                text: label
                font.pixelSize: Theme.fontSizeTitle
                font.bold: true
                color: Theme.colors.accentSecondary
                topPadding: Theme.spacing.md
                Layout.fillWidth: true
            }

            Label {
                visible: kind !== "section"
                text: label
                font.pixelSize: Theme.typography.body.pixelSize
                font.bold: true
                color: Theme.colors.textPrimary
                Layout.fillWidth: true
            }

            Label {
                visible: kind !== "section" && description.length > 0
                text: description
                font.pixelSize: Theme.fontSizeSmall
                color: Theme.colors.textSecondary
                wrapMode: Text.Wrap
                Layout.fillWidth: true
            }

            Switch {
                visible: kind === "bool"
                text: value === "true" ? qsTr("An") : qsTr("Aus")
                checked: value === "true"
                onToggled: {
                    if (vm) {
                        vm.updateSetting(settingKey, checked ? "true" : "false");
                    }
                }
            }

            TextField {
                id: strField
                visible: kind === "string" || kind === "number"
                Layout.fillWidth: true
                text: value
                echoMode: settingKey === "ollama_api_key" ? TextInput.Password : TextInput.Normal
                onEditingFinished: {
                    if (vm && strField.text !== value) {
                        vm.updateSetting(settingKey, strField.text);
                    }
                }
            }

            ComboBox {
                id: enumBox
                visible: kind === "enum"
                Layout.fillWidth: true
                model: options.length > 0 ? options.split("|") : []

                function syncIndex() {
                    let parts = options.length > 0 ? options.split("|") : [];
                    let i = parts.indexOf(value);
                    enumBox.currentIndex = i >= 0 ? i : 0;
                }

                Component.onCompleted: syncIndex()

                onActivated: function (ix) {
                    if (vm) {
                        vm.updateSetting(settingKey, enumBox.textAt(ix));
                    }
                }
            }
        }
    }
}
