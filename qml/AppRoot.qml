import QtQuick
import QtQuick.Controls
import themes 1.0
import "shell"

ApplicationWindow {
    id: root
    visible: true
    width: 1280
    height: 800
    title: qsTr("Linux Desktop Chat — QML Shell")
    color: Theme.surfaces.architectural

    AppChrome {
        anchors.fill: parent
        anchors.margins: Theme.spacing.sm
        shellBridge: shell
    }
}
