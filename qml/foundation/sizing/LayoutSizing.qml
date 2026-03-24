import QtQuick

/** Layout- und Komponentenmaße (Desktop, kontrollierte Proportionen). */
QtObject {
    readonly property int navWidthPreferred: 168
    readonly property int navWidthMin: 144
    readonly property int navWidthMax: 200

    readonly property int contextSurfaceWidthPreferred: 200
    readonly property int contextSurfaceWidthMax: 240

    readonly property int sessionShelfWidthPreferred: 232

    readonly property int contentMaxWidthReading: 680
    readonly property int contentMaxWidthUserBubble: 480

    readonly property int inputComposerMinHeight: 120
    readonly property int inputComposerPreferredMaxHeight: 160
    readonly property int listRowHeightDefault: 40
    readonly property int listRowHeightComfortable: 44

    readonly property QtObject reading: QtObject {
        readonly property int columnMaxWidth: 680
        readonly property int userBubbleMaxWidth: 480
        readonly property real assistantLineHeight: 1.5
        readonly property real userLineHeight: 1.35
        readonly property int blockGap: 8
        readonly property int sectionGap: 32
        readonly property int roleToBodyGap: 6
        readonly property int manuscriptPadH: 20
        readonly property int manuscriptPadV: 24
    }
}
