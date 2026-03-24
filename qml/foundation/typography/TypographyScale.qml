import QtQuick

/**
 * Typografische Rollen — Pixelgrößen und Gewichte.
 * Farben über Theme.colors.* an Komponenten binden (keine harte Kopplung hier).
 */
QtObject {
    readonly property QtObject appTitle: QtObject {
        readonly property int pixelSize: 22
        readonly property int weight: 600
        readonly property real lineHeight: 1.25
    }
    readonly property QtObject domainTitle: QtObject {
        readonly property int pixelSize: 20
        readonly property int weight: 600
        readonly property real lineHeight: 1.3
    }
    readonly property QtObject sectionTitle: QtObject {
        readonly property int pixelSize: 16
        readonly property int weight: 600
        readonly property real lineHeight: 1.35
    }
    readonly property QtObject panelTitle: QtObject {
        readonly property int pixelSize: 15
        readonly property int weight: 500
        readonly property real lineHeight: 1.35
    }
    readonly property QtObject body: QtObject {
        readonly property int pixelSize: 14
        readonly property int weight: 400
        readonly property real lineHeight: 1.45
    }
    readonly property QtObject bodyEmphasis: QtObject {
        readonly property int pixelSize: 14
        readonly property int weight: 500
        readonly property real lineHeight: 1.45
    }
    readonly property QtObject metadata: QtObject {
        readonly property int pixelSize: 13
        readonly property int weight: 400
        readonly property real lineHeight: 1.4
    }
    readonly property QtObject label: QtObject {
        readonly property int pixelSize: 13
        readonly property int weight: 500
        readonly property real lineHeight: 1.35
    }
    readonly property QtObject caption: QtObject {
        readonly property int pixelSize: 12
        readonly property int weight: 400
        readonly property real lineHeight: 1.35
    }
    readonly property QtObject technicalMono: QtObject {
        readonly property int pixelSize: 12
        readonly property int weight: 400
        readonly property real lineHeight: 1.35
        readonly property string family: "monospace"
    }
}
