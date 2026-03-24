import QtQuick

QtObject {
    readonly property int durationShort: 160
    readonly property int durationMedium: 240
    readonly property int durationLong: 360

    /** Qt Quick Easing-Typen (Animation.easing.type). */
    readonly property int easingStandard: Easing.OutCubic
    readonly property int easingEmphasized: Easing.OutQuint
    readonly property int easingEnter: Easing.OutCubic
    readonly property int easingExit: Easing.InCubic

    readonly property int durationStageTransition: durationMedium
    readonly property int durationPanelReveal: durationMedium
    readonly property int durationFocusShift: durationShort
    readonly property int durationHoverResponse: durationShort
}
