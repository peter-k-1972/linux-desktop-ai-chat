import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import themes 1.0
import "../_placeholder"
import "../../foundation"

ColumnLayout {
    anchors.fill: parent
    spacing: Theme.spacing.md

    DomainPlaceholder {
        Layout.fillWidth: true
        Layout.preferredHeight: 200
        domainTitle: qsTr("Einstellungen")
        domainRoleDescription: qsTr("Archivverwaltung und Haustechnik — Konfiguration der Anwendung.")
    }

    Rectangle {
        Layout.fillWidth: true
        Layout.preferredHeight: 1
        color: Theme.divider.line
        opacity: Theme.divider.lineOpacity
    }

    Label {
        Layout.fillWidth: true
        text: qsTr("Design-Fundament (Smoke)")
        font.pixelSize: Theme.typography.label.pixelSize
        font.weight: Theme.typography.label.weight
        color: Theme.colors.textMuted
    }

    ScrollView {
        id: tokenScroll
        Layout.fillWidth: true
        Layout.fillHeight: true
        clip: true

        FoundationPreview {
            width: Math.max(tokenScroll.availableWidth, 200)
        }
    }
}
