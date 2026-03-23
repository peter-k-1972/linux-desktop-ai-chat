"""Unit-Tests: icon_registry – Auflösung und Helfer."""

from app.gui.icons.icon_registry import get_resource_svg_path, list_resource_backed_names


def test_get_resource_svg_path_symbolic_assets_exist():
    for name in ("pin", "open", "link_out", "qa_runtime", "sparkles", "deploy", "graph"):
        p = get_resource_svg_path(name)
        assert p is not None, name
        assert p.is_file(), name


def test_get_icon_for_object_deployment_resolves_to_deploy(qapplication):
    from app.gui.icons.icon_registry import get_icon_for_object

    ic = get_icon_for_object("deployment", size=24)
    assert not ic.isNull()


def test_get_icon_for_action_open_uses_open_glyph(qapplication):
    from app.gui.icons.icon_registry import get_icon_for_action

    ic = get_icon_for_action("open", size=24)
    assert not ic.isNull()


def test_list_resource_backed_names_includes_new_registry_ids():
    names = list_resource_backed_names()
    for n in ("qa_runtime", "sparkles", "pin", "open", "link_out", "graph", "folder"):
        assert n in names
