import QtQuick
import QtQuick.Controls
import themes 1.0
import "../foundation/layout"

Item {
    id: root
    clip: true

    property var shellBridge

    WorkSurface {
        id: ws
        anchors.fill: parent
        anchors.margins: Theme.spacing.stageMargin

        Loader {
            id: stageLoader
            anchors.fill: parent
            anchors.margins: Theme.spacing.stageMargin
            asynchronous: false
            source: shellBridge && shellBridge.stageUrl ? shellBridge.stageUrl : ""
        }
    }
}
