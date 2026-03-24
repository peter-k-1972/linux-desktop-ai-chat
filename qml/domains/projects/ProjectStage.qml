import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import themes 1.0

/**
 * Projekte — War-Room: Liste · Übersicht · Inspector.
 */
Item {
    id: root
    anchors.fill: parent

    readonly property bool studioOk: typeof projectStudio !== "undefined" && projectStudio !== null

    Rectangle {
        anchors.fill: parent
        visible: !root.studioOk
        color: Theme.colors.surfaceMutedTray
        Label {
            anchors.centerIn: parent
            text: qsTr("Projekte sind nicht angebunden (kein „projectStudio“).")
            color: Theme.colors.textPrimary
            wrapMode: Text.Wrap
            width: parent.width - Theme.spacing.lg * 2
            horizontalAlignment: Text.AlignHCenter
        }
    }

    RowLayout {
        anchors.fill: parent
        spacing: Theme.spacing.md
        visible: root.studioOk

        Loader {
            id: listLoader
            Layout.preferredWidth: 288
            Layout.maximumWidth: 340
            Layout.fillHeight: true
            asynchronous: false
            source: "ProjectList.qml"
            onLoaded: {
                if (item)
                    item.vm = projectStudio
            }
            onStatusChanged: {
                if (status === Loader.Ready && item)
                    item.vm = projectStudio
            }
        }

        Rectangle {
            Layout.preferredWidth: 1
            Layout.fillHeight: true
            color: Theme.divider.line
            opacity: Theme.divider.lineOpacity
        }

        Loader {
            id: workspaceLoader
            Layout.fillWidth: true
            Layout.fillHeight: true
            asynchronous: false
            source: "ProjectWorkspace.qml"
            onLoaded: {
                if (item) {
                    item.vm = projectStudio
                    item.shellBridge = typeof shell !== "undefined" ? shell : null
                }
            }
            onStatusChanged: {
                if (status === Loader.Ready && item) {
                    item.vm = projectStudio
                    item.shellBridge = typeof shell !== "undefined" ? shell : null
                }
            }
        }

        Rectangle {
            Layout.preferredWidth: 1
            Layout.fillHeight: true
            color: Theme.divider.line
            opacity: Theme.divider.lineOpacity
        }

        Loader {
            id: inspectorLoader
            Layout.preferredWidth: 272
            Layout.maximumWidth: 360
            Layout.fillHeight: true
            asynchronous: false
            source: "ProjectInspector.qml"
            onLoaded: {
                if (item)
                    item.vm = projectStudio
            }
            onStatusChanged: {
                if (status === Loader.Ready && item)
                    item.vm = projectStudio
            }
        }
    }
}
