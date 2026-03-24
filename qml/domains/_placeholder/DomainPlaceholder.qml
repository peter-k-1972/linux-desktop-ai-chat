import QtQuick
import QtQuick.Controls
import themes 1.0

Item {
    id: root
    property string domainTitle: ""
    property string domainRoleDescription: ""

    Column {
        spacing: Theme.spacing.md
        anchors.fill: parent

        Label {
            text: root.domainTitle
            font.pixelSize: Theme.typography.domainTitle.pixelSize
            font.weight: Theme.typography.domainTitle.weight
            color: Theme.colors.textPrimary
            wrapMode: Text.Wrap
            width: parent.width
        }
        Label {
            text: root.domainRoleDescription
            font.pixelSize: Theme.typography.body.pixelSize
            color: Theme.colors.textSecondary
            wrapMode: Text.Wrap
            width: parent.width
        }
        Label {
            text: qsTr("Platzhalter — hier wird später die echte Domäne geladen.")
            font.pixelSize: Theme.typography.caption.pixelSize
            color: Theme.colors.textSecondary
            wrapMode: Text.Wrap
            width: parent.width
        }
    }
}
