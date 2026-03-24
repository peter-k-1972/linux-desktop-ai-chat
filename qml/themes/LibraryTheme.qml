import QtQuick
import "../foundation/color"
import "../foundation/surfaces"
import "../foundation/spacing"
import "../foundation/sizing"
import "../foundation/typography"
import "../foundation/radius"
import "../foundation/divider"
import "../foundation/elevation"
import "../foundation/motion"
import "../foundation/states"

/**
 * Zusammenführung aller Foundation-Token-Objekte.
 * Keine Fachlogik — nur semantische Werte.
 */
QtObject {
    id: root

    readonly property SemanticColors colors: SemanticColors {}
    readonly property SemanticSurfaces surfaces: SemanticSurfaces {
        palette: root.colors
    }
    readonly property SpacingScale spacing: SpacingScale {}
    readonly property LayoutSizing sizing: LayoutSizing {}
    readonly property TypographyScale typography: TypographyScale {}
    readonly property RadiusScale radius: RadiusScale {}
    readonly property DividerTokens divider: DividerTokens {
        palette: root.colors
    }
    readonly property ElevationTokens elevation: ElevationTokens {
        palette: root.colors
    }
    readonly property MotionTokens motion: MotionTokens {}
    readonly property InteractionStates states: InteractionStates {
        palette: root.colors
    }
}
