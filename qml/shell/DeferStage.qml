import QtQuick
import QtQuick.Controls
import themes 1.0

/**
 * Shown when no product QML surface is bound for the current route (Welle 1).
 * Displays routing token only — no product copy.
 */
Item {
    id: root
    anchors.fill: parent

    /** Engine context property ``shell`` (``ShellBridgeFacade``). */
    readonly property var shellRef: typeof shell !== "undefined" ? shell : null

    ScrollView {
        anchors.fill: parent
        clip: true

        Label {
            width: root.width
            text: root.shellRef && root.shellRef.routeDeferReason.length > 0
                ? root.shellRef.routeDeferReason
                : qsTr("route_not_bound")
            font.pixelSize: Theme.typography.body.pixelSize
            color: Theme.colors.textSecondary
            wrapMode: Text.Wrap
        }
    }
}
