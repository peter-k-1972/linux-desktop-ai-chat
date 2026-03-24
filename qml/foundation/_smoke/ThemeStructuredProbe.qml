import QtQuick
import themes 1.0

/**
 * Interner Smoke-Check für pytest — nicht in Screens verwenden.
 */
Item {
    property bool ok: Theme.registry !== null
        && Theme.library !== null
        && Theme.colors.appBackground !== undefined
        && Theme.surfaces.architectural !== undefined
        && Theme.typography.body.pixelSize > 0
        && Theme.spacing.md === 16
        && Theme.motion.durationMedium >= Theme.motion.durationShort
}
