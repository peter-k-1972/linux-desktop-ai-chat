pragma Singleton
import QtQuick

/**
 * Globales Theme: Registry + LibraryTheme + strukturierte API + Legacy-Aliase (Slice 0–2).
 */
QtObject {
    id: root

    readonly property ThemeRegistry registry: ThemeRegistry {}
    readonly property LibraryTheme themeLibrary: LibraryTheme {}

    // —— Strukturierte API (Foundation Design System) ——
    // Typen als ``var``: Foundation-Typen sind nur über LibraryTheme importiert, nicht im themes-Modul.
    readonly property var colors: themeLibrary.colors
    readonly property var surfaces: themeLibrary.surfaces
    readonly property var spacing: themeLibrary.spacing
    readonly property var sizing: themeLibrary.sizing
    readonly property var typography: themeLibrary.typography
    readonly property var radius: themeLibrary.radius
    readonly property var divider: themeLibrary.divider
    readonly property var elevation: themeLibrary.elevation
    readonly property var motion: themeLibrary.motion
    readonly property var states: themeLibrary.states

    readonly property string variant: registry.activeVariantId

    // —— Legacy / Kompatibilität ——
    readonly property var library: themeLibrary

    readonly property color canvasBase: themeLibrary.colors.appBackground
    readonly property color canvasElevated: themeLibrary.colors.sideSurface
    readonly property color surfaceWork: themeLibrary.colors.workSurface
    readonly property color surfaceMuted: themeLibrary.colors.surfaceMutedTray
    readonly property color borderSubtle: themeLibrary.divider.borderSoft
    readonly property color borderFocus: themeLibrary.states.focusRing
    readonly property color textOnDark: themeLibrary.colors.textOnDarkPrimary
    readonly property color textPrimary: themeLibrary.colors.textPrimary
    readonly property color textSecondary: themeLibrary.colors.textSecondary
    readonly property color accentPrimary: themeLibrary.colors.accentPrimary
    readonly property color accentSecondary: themeLibrary.colors.accentSecondary
    readonly property color stateError: themeLibrary.states.error

    readonly property int fontSizeSmall: themeLibrary.typography.caption.pixelSize
    readonly property int fontSizeUi: themeLibrary.typography.body.pixelSize
    readonly property int fontSizeTitle: themeLibrary.typography.domainTitle.pixelSize

    readonly property int spaceXs: themeLibrary.spacing.xs
    readonly property int spaceSm: themeLibrary.spacing.sm
    readonly property int spaceMd: themeLibrary.spacing.md
    readonly property int spaceLg: themeLibrary.spacing.lg

    readonly property int radiusSm: themeLibrary.radius.sm
    readonly property int radiusMd: themeLibrary.radius.md

    readonly property int durationFast: themeLibrary.motion.durationShort
    readonly property int durationNormal: themeLibrary.motion.durationMedium

    readonly property int readingColumnMaxWidth: themeLibrary.sizing.reading.columnMaxWidth
    readonly property int readingUserMaxWidth: themeLibrary.sizing.reading.userBubbleMaxWidth
    readonly property real readingAssistantLineHeight: themeLibrary.sizing.reading.assistantLineHeight
    readonly property real readingUserLineHeight: themeLibrary.sizing.reading.userLineHeight
    readonly property int readingBlockGap: themeLibrary.sizing.reading.blockGap
    readonly property int readingSectionGap: themeLibrary.sizing.reading.sectionGap
    readonly property int readingRoleToBodyGap: themeLibrary.sizing.reading.roleToBodyGap
    readonly property int readingManuscriptPadH: themeLibrary.sizing.reading.manuscriptPadH
    readonly property int readingManuscriptPadV: themeLibrary.sizing.reading.manuscriptPadV
}
