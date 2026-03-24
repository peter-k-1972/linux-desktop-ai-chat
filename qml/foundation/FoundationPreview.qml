import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import themes 1.0

/**
 * Minimale Smoke-Ansicht für Foundation-Tokens (kein Demo-Screen).
 */
Item {
    id: root
    implicitHeight: col.implicitHeight
    width: parent ? parent.width : implicitWidth

    ColumnLayout {
        id: col
        anchors.left: parent.left
        anchors.right: parent.right
        width: parent.width
        spacing: Theme.spacing.md

        Label {
            Layout.fillWidth: true
            text: qsTr("Foundation · %1").arg(Theme.registry.displayLabel)
            font.pixelSize: Theme.typography.sectionTitle.pixelSize
            font.weight: Theme.typography.sectionTitle.weight
            color: Theme.colors.textPrimary
            wrapMode: Text.Wrap
        }
        Label {
            Layout.fillWidth: true
            text: qsTr("Variante: %1").arg(Theme.variant)
            font.pixelSize: Theme.typography.caption.pixelSize
            color: Theme.colors.textSecondary
        }

        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: 48
            radius: Theme.radius.sm
            color: Theme.surfaces.readingPaper
            border.width: 1
            border.color: Theme.divider.borderSoft
        }
        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: 36
            radius: Theme.radius.sm
            color: Theme.surfaces.panelSide
            border.width: 1
            border.color: Theme.states.focusRing
        }
        RowLayout {
            Layout.fillWidth: true
            spacing: Theme.spacing.sm
            Rectangle {
                Layout.preferredWidth: 28
                Layout.preferredHeight: 28
                radius: Theme.radius.none
                color: Theme.colors.accentPrimary
            }
            Rectangle {
                Layout.preferredWidth: 28
                Layout.preferredHeight: 28
                radius: Theme.radius.none
                color: Theme.colors.accentSecondary
            }
            Rectangle {
                Layout.preferredWidth: 28
                Layout.preferredHeight: 28
                radius: Theme.radius.none
                color: Theme.states.success
            }
            Rectangle {
                Layout.preferredWidth: 28
                Layout.preferredHeight: 28
                radius: Theme.radius.none
                color: Theme.states.warning
            }
            Rectangle {
                Layout.preferredWidth: 28
                Layout.preferredHeight: 28
                radius: Theme.radius.none
                color: Theme.states.error
            }
            Item {
                Layout.fillWidth: true
            }
        }
        Label {
            Layout.fillWidth: true
            text: qsTr("Motion: kurz %1 ms · mittel %2 ms · easing %3")
                .arg(Theme.motion.durationShort)
                .arg(Theme.motion.durationMedium)
                .arg(Theme.motion.easingStandard)
            font.pixelSize: Theme.typography.technicalMono.pixelSize
            font.family: Theme.typography.technicalMono.family
            color: Theme.colors.textMuted
            wrapMode: Text.Wrap
        }
    }
}
