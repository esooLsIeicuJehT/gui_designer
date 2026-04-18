"""Comprehensive tests for gui_designer.py (PR additions)."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# All tests in this module require PyQt6.  Skip the whole module if it is not
# installed so the test session remains healthy in environments without a GUI
# toolkit.
PyQt6 = pytest.importorskip("PyQt6", reason="PyQt6 is required to test gui_designer")

import gui_designer  # noqa: E402  (import after PyQt6 check)
from gui_designer import (  # noqa: E402
    AUTHOR_EMAIL,
    AUTHOR_NAME,
    STARTER_PRESETS,
    STYLE_PRESETS,
    WATERMARK_TEXT,
    build_layout,
    build_stylesheet,
    default_widget,
    make_widget,
    yaml_available,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _minimal_design(**overrides):
    """Return a minimal design dict suitable for most helpers."""
    base = {
        "window_title": "Test Window",
        "bg_color": "#ffffff",
        "accent_color": "#3498db",
        "theme": "Light",
        "button_style": "Default",
        "layout_type": "Vertical",
        "tab_position": "North",
        "grid_columns": 2,
        "margin": 10,
        "spacing": 8,
        "widgets": [],
    }
    base.update(overrides)
    return base


def _make_widget_descriptor(widget_type: str, **extra) -> dict:
    w = default_widget(widget_type, 1)
    w.update(extra)
    return w


# ===========================================================================
# 1. Module-level constants
# ===========================================================================

class TestConstants:
    def test_author_name(self):
        assert AUTHOR_NAME == "Justin Lorenc"

    def test_author_email(self):
        assert AUTHOR_EMAIL == "midnight-repo@engineer.com"

    def test_watermark_contains_author(self):
        assert AUTHOR_NAME in WATERMARK_TEXT
        assert AUTHOR_EMAIL in WATERMARK_TEXT

    def test_style_presets_keys(self):
        expected = {"Default", "Flat", "Modern", "Rounded", "Neon"}
        assert set(STYLE_PRESETS.keys()) == expected

    def test_default_style_preset_is_empty(self):
        assert STYLE_PRESETS["Default"] == ""

    def test_neon_preset_contains_color(self):
        assert "#00ff9f" in STYLE_PRESETS["Neon"]

    def test_starter_presets_keys(self):
        expected = {"Data Dashboard", "Neon Game Launcher", "Glass CRM Panel"}
        assert set(STARTER_PRESETS.keys()) == expected

    def test_data_dashboard_preset(self):
        preset = STARTER_PRESETS["Data Dashboard"]
        assert preset["theme"] == "Dark"
        assert preset["layout_type"] == "Grid"
        assert len(preset["widgets"]) == 4

    def test_neon_game_launcher_preset(self):
        preset = STARTER_PRESETS["Neon Game Launcher"]
        assert preset["theme"] == "Gradient"
        assert preset["button_style"] == "Neon"

    def test_glass_crm_panel_preset(self):
        preset = STARTER_PRESETS["Glass CRM Panel"]
        assert preset["theme"] == "Glass"
        assert preset["layout_type"] == "Horizontal"


# ===========================================================================
# 2. default_widget()
# ===========================================================================

class TestDefaultWidget:
    def test_returns_dict(self):
        w = default_widget("Label", 1)
        assert isinstance(w, dict)

    def test_type_stored(self):
        w = default_widget("Button", 3)
        assert w["type"] == "Button"

    def test_name_derived_from_type_and_index(self):
        w = default_widget("Line Edit", 5)
        assert w["name"] == "line_edit_5"

    def test_label_derived_from_type_and_index(self):
        w = default_widget("Spin Box", 2)
        assert w["label"] == "Spin Box 2"

    def test_defaults_for_optional_fields(self):
        w = default_widget("Check Box", 1)
        assert w["placeholder"] == ""
        assert w["min"] == 0
        assert w["max"] == 100
        assert w["required"] is False

    def test_spaces_replaced_in_name(self):
        w = default_widget("Text Edit", 7)
        assert " " not in w["name"]
        assert w["name"] == "text_edit_7"

    def test_index_zero_still_works(self):
        w = default_widget("Label", 0)
        assert w["name"] == "label_0"

    def test_large_index(self):
        w = default_widget("Group Box", 999)
        assert w["name"] == "group_box_999"

    def test_name_is_lowercase(self):
        w = default_widget("Combo Box", 1)
        assert w["name"] == w["name"].lower()


# ===========================================================================
# 3. yaml_available()
# ===========================================================================

class TestYamlAvailable:
    def test_returns_bool(self):
        result = yaml_available()
        assert isinstance(result, bool)

    def test_true_when_yaml_importable(self):
        # yaml is installed in the test environment
        import importlib
        try:
            importlib.import_module("yaml")
            yaml_installed = True
        except ImportError:
            yaml_installed = False
        assert yaml_available() == yaml_installed

    def test_false_when_yaml_missing(self):
        original = sys.modules.get("yaml")
        sys.modules["yaml"] = None  # simulate broken import
        try:
            result = yaml_available()
            assert result is False
        finally:
            if original is None:
                del sys.modules["yaml"]
            else:
                sys.modules["yaml"] = original


# ===========================================================================
# 4. build_stylesheet()
# ===========================================================================

class TestBuildStylesheet:
    def test_light_theme_includes_bg_color(self):
        d = _minimal_design(theme="Light", bg_color="#abcdef")
        css = build_stylesheet(d)
        assert "#abcdef" in css

    def test_dark_theme_includes_bg_color(self):
        d = _minimal_design(theme="Dark", bg_color="#111111")
        css = build_stylesheet(d)
        assert "#111111" in css

    def test_gradient_theme_includes_both_colors(self):
        d = _minimal_design(theme="Gradient", bg_color="#000000", accent_color="#ff0000")
        css = build_stylesheet(d)
        assert "#000000" in css
        assert "#ff0000" in css

    def test_glass_theme_uses_rgba(self):
        d = _minimal_design(theme="Glass", bg_color="#222222")
        css = build_stylesheet(d)
        assert "rgba" in css

    def test_unknown_theme_falls_back_to_light(self):
        d = _minimal_design(theme="Alien", bg_color="#ffffff")
        css = build_stylesheet(d)
        # Should not raise; falls back to Light (first key or get default)
        assert isinstance(css, str)

    def test_watermark_style_present(self):
        d = _minimal_design()
        css = build_stylesheet(d)
        assert "#watermark" in css

    def test_neon_button_style_included(self):
        d = _minimal_design(button_style="Neon")
        css = build_stylesheet(d)
        assert "#00ff9f" in css

    def test_default_button_style_adds_no_extra(self):
        d = _minimal_design(button_style="Default")
        css = build_stylesheet(d)
        # STYLE_PRESETS["Default"] is "", so only theme + watermark lines
        assert "QPushButton" not in css

    def test_returns_string(self):
        d = _minimal_design()
        assert isinstance(build_stylesheet(d), str)


# ===========================================================================
# 5. make_widget()  (requires QApplication)
# ===========================================================================

class TestMakeWidget:
    @pytest.fixture(autouse=True)
    def _ensure_app(self, qapp):
        pass

    def test_label_widget(self):
        from PyQt6.QtWidgets import QLabel
        w = make_widget({"type": "Label", "label": "Hello"})
        assert isinstance(w, QLabel)
        assert w.text() == "Hello"

    def test_button_widget(self):
        from PyQt6.QtWidgets import QPushButton
        w = make_widget({"type": "Button", "label": "Click me"})
        assert isinstance(w, QPushButton)
        assert w.text() == "Click me"

    def test_line_edit_widget(self):
        from PyQt6.QtWidgets import QLineEdit
        w = make_widget({"type": "Line Edit", "label": "Name", "placeholder": "Enter name"})
        assert isinstance(w, QLineEdit)
        assert w.placeholderText() == "Enter name"

    def test_line_edit_falls_back_to_label_for_placeholder(self):
        from PyQt6.QtWidgets import QLineEdit
        w = make_widget({"type": "Line Edit", "label": "Email"})
        assert isinstance(w, QLineEdit)
        assert w.placeholderText() == "Email"

    def test_text_edit_widget(self):
        from PyQt6.QtWidgets import QTextEdit
        w = make_widget({"type": "Text Edit", "label": "Notes", "placeholder": "Type here"})
        assert isinstance(w, QTextEdit)
        assert w.placeholderText() == "Type here"

    def test_text_edit_minimum_height(self):
        from PyQt6.QtWidgets import QTextEdit
        w = make_widget({"type": "Text Edit", "label": "Bio"})
        assert isinstance(w, QTextEdit)
        assert w.minimumHeight() >= 90

    def test_checkbox_widget(self):
        from PyQt6.QtWidgets import QCheckBox
        w = make_widget({"type": "Check Box", "label": "Enable feature"})
        assert isinstance(w, QCheckBox)
        assert w.text() == "Enable feature"

    def test_combobox_widget(self):
        from PyQt6.QtWidgets import QComboBox
        w = make_widget({"type": "Combo Box", "label": "Mode"})
        assert isinstance(w, QComboBox)
        assert w.count() == 3

    def test_spinbox_widget_range(self):
        from PyQt6.QtWidgets import QSpinBox
        w = make_widget({"type": "Spin Box", "label": "Count", "min": 5, "max": 50})
        assert isinstance(w, QSpinBox)
        assert w.minimum() == 5
        assert w.maximum() == 50

    def test_spinbox_default_range(self):
        from PyQt6.QtWidgets import QSpinBox
        w = make_widget({"type": "Spin Box", "label": "Count"})
        assert isinstance(w, QSpinBox)
        assert w.minimum() == 0
        assert w.maximum() == 100

    def test_groupbox_widget(self):
        from PyQt6.QtWidgets import QGroupBox
        w = make_widget({"type": "Group Box", "label": "Settings"})
        assert isinstance(w, QGroupBox)
        assert w.title() == "Settings"

    def test_unsupported_type_returns_label(self):
        from PyQt6.QtWidgets import QLabel
        w = make_widget({"type": "NonExistent", "label": "Oops"})
        assert isinstance(w, QLabel)
        assert "Unsupported" in w.text()
        assert "NonExistent" in w.text()

    def test_missing_label_falls_back_to_type(self):
        from PyQt6.QtWidgets import QLabel
        w = make_widget({"type": "Label"})
        assert isinstance(w, QLabel)
        assert w.text() == "Label"


# ===========================================================================
# 6. build_layout()  (requires QApplication)
# ===========================================================================

class TestBuildLayout:
    @pytest.fixture(autouse=True)
    def _ensure_app(self, qapp):
        pass

    def test_vertical_layout(self):
        from PyQt6.QtWidgets import QVBoxLayout, QWidget
        parent = QWidget()
        lay = build_layout(_minimal_design(layout_type="Vertical"), parent)
        assert isinstance(lay, QVBoxLayout)

    def test_horizontal_layout(self):
        from PyQt6.QtWidgets import QHBoxLayout, QWidget
        parent = QWidget()
        lay = build_layout(_minimal_design(layout_type="Horizontal"), parent)
        assert isinstance(lay, QHBoxLayout)

    def test_grid_layout(self):
        from PyQt6.QtWidgets import QGridLayout, QWidget
        parent = QWidget()
        lay = build_layout(_minimal_design(layout_type="Grid"), parent)
        assert isinstance(lay, QGridLayout)

    def test_tabbed_falls_back_to_vertical(self):
        # "Tabbed" is not handled specifically by build_layout, defaults to VBox
        from PyQt6.QtWidgets import QVBoxLayout, QWidget
        parent = QWidget()
        lay = build_layout(_minimal_design(layout_type="Tabbed"), parent)
        assert isinstance(lay, QVBoxLayout)

    def test_margin_applied(self):
        from PyQt6.QtWidgets import QWidget
        parent = QWidget()
        lay = build_layout(_minimal_design(margin=15, layout_type="Vertical"), parent)
        left, top, right, bottom = lay.contentsMargins().left(), lay.contentsMargins().top(), lay.contentsMargins().right(), lay.contentsMargins().bottom()
        assert left == 15 and top == 15 and right == 15 and bottom == 15

    def test_spacing_applied(self):
        from PyQt6.QtWidgets import QWidget
        parent = QWidget()
        lay = build_layout(_minimal_design(spacing=20, layout_type="Horizontal"), parent)
        assert lay.spacing() == 20


# ===========================================================================
# 7. PropertyEditor  (requires QApplication)
# ===========================================================================

class TestPropertyEditor:
    @pytest.fixture(autouse=True)
    def _ensure_app(self, qapp):
        pass

    @pytest.fixture
    def main_win(self):
        from gui_designer import MainWindow
        win = MainWindow()
        yield win
        win.close()

    @pytest.fixture
    def editor(self, main_win):
        return main_win.editor

    # --- design() ---

    def test_design_returns_dict(self, editor):
        d = editor.design()
        assert isinstance(d, dict)

    def test_design_has_required_keys(self, editor):
        keys = {
            "window_title", "bg_color", "accent_color", "theme",
            "button_style", "layout_type", "tab_position", "grid_columns",
            "margin", "spacing", "widgets",
        }
        assert keys.issubset(editor.design().keys())

    def test_design_default_title(self, editor):
        assert editor.design()["window_title"] == "My Custom GUI"

    def test_design_default_theme(self, editor):
        assert editor.design()["theme"] == "Light"

    def test_design_widgets_initially_empty(self, editor):
        assert editor.design()["widgets"] == []

    def test_design_returns_copy_of_widgets(self, editor):
        from PyQt6.QtWidgets import QListWidgetItem
        item = QListWidgetItem("Label")
        editor.add_widget(item)
        d1 = editor.design()
        d1["widgets"].clear()
        # Original widgets list should be unaffected
        assert len(editor.widgets) == 1

    # --- load_design() ---

    def test_load_design_updates_title(self, editor):
        editor.load_design({"window_title": "Loaded Title"})
        assert editor.window_title.text() == "Loaded Title"

    def test_load_design_updates_theme(self, editor):
        editor.load_design({"theme": "Dark"})
        assert editor.theme.currentText() == "Dark"

    def test_load_design_updates_layout_type(self, editor):
        editor.load_design({"layout_type": "Horizontal"})
        assert editor.layout_type.currentText() == "Horizontal"

    def test_load_design_updates_margin(self, editor):
        editor.load_design({"margin": 25})
        assert editor.margin.value() == 25

    def test_load_design_updates_spacing(self, editor):
        editor.load_design({"spacing": 15})
        assert editor.spacing.value() == 15

    def test_load_design_repopulates_widgets_list(self, editor):
        data = {
            "widgets": [
                {"type": "Label", "name": "lbl_1", "label": "Hi", "placeholder": "", "min": 0, "max": 100, "required": False}
            ]
        }
        editor.load_design(data)
        assert len(editor.widgets) == 1
        assert editor.widgets_list.count() == 1

    def test_load_design_clears_previous_widgets(self, editor):
        from PyQt6.QtWidgets import QListWidgetItem
        editor.add_widget(QListWidgetItem("Button"))
        editor.load_design({"widgets": []})
        assert len(editor.widgets) == 0

    def test_load_design_empty_dict_uses_defaults(self, editor):
        editor.load_design({})
        # Should not raise; uses fallback defaults
        assert editor.window_title.text() == "Custom GUI"

    # --- add_widget() / remove_widget() / clear_widgets() ---

    def test_add_widget_increases_count(self, editor):
        from PyQt6.QtWidgets import QListWidgetItem
        editor.add_widget(QListWidgetItem("Label"))
        assert len(editor.widgets) == 1
        assert editor.widgets_list.count() == 1

    def test_add_widget_sets_correct_type(self, editor):
        from PyQt6.QtWidgets import QListWidgetItem
        editor.add_widget(QListWidgetItem("Button"))
        assert editor.widgets[0]["type"] == "Button"

    def test_add_widget_list_item_text_format(self, editor):
        from PyQt6.QtWidgets import QListWidgetItem
        editor.add_widget(QListWidgetItem("Check Box"))
        text = editor.widgets_list.item(0).text()
        assert "Check Box" in text
        assert "check_box_1" in text

    def test_add_multiple_widgets(self, editor):
        from PyQt6.QtWidgets import QListWidgetItem
        for name in ["Label", "Button", "Spin Box"]:
            editor.add_widget(QListWidgetItem(name))
        assert len(editor.widgets) == 3
        assert editor.widgets_list.count() == 3

    def test_remove_widget_decreases_count(self, editor):
        from PyQt6.QtWidgets import QListWidgetItem
        editor.add_widget(QListWidgetItem("Label"))
        editor.widgets_list.setCurrentRow(0)
        editor.remove_widget()
        assert len(editor.widgets) == 0
        assert editor.widgets_list.count() == 0

    def test_remove_widget_no_selection_is_noop(self, editor):
        from PyQt6.QtWidgets import QListWidgetItem
        editor.add_widget(QListWidgetItem("Label"))
        editor.widgets_list.setCurrentRow(-1)
        editor.remove_widget()
        assert len(editor.widgets) == 1

    def test_remove_widget_correct_item_removed(self, editor):
        from PyQt6.QtWidgets import QListWidgetItem
        editor.add_widget(QListWidgetItem("Label"))
        editor.add_widget(QListWidgetItem("Button"))
        editor.widgets_list.setCurrentRow(0)
        editor.remove_widget()
        assert editor.widgets[0]["type"] == "Button"

    def test_clear_widgets_removes_all(self, editor):
        from PyQt6.QtWidgets import QListWidgetItem
        for name in ["Label", "Button", "Combo Box"]:
            editor.add_widget(QListWidgetItem(name))
        editor.clear_widgets()
        assert len(editor.widgets) == 0
        assert editor.widgets_list.count() == 0

    def test_clear_widgets_when_empty_is_safe(self, editor):
        editor.clear_widgets()
        assert len(editor.widgets) == 0

    # --- _load_widget_properties() ---

    def test_load_widget_properties_sets_fields(self, editor):
        from PyQt6.QtWidgets import QListWidgetItem
        editor.add_widget(QListWidgetItem("Spin Box"))
        editor.widgets[0].update({"placeholder": "ph", "min": 5, "max": 50, "required": True})
        editor._load_widget_properties(0)
        assert editor.prop_min.value() == 5
        assert editor.prop_max.value() == 50
        assert editor.prop_required.isChecked() is True
        assert editor.prop_placeholder.text() == "ph"

    def test_load_widget_properties_negative_row_is_noop(self, editor):
        # Should not raise
        editor._load_widget_properties(-1)

    def test_load_widget_properties_out_of_range_is_noop(self, editor):
        editor._load_widget_properties(99)

    # --- apply_widget_properties() ---

    def test_apply_widget_properties_updates_widget(self, editor):
        from PyQt6.QtWidgets import QListWidgetItem
        editor.add_widget(QListWidgetItem("Label"))
        editor.widgets_list.setCurrentRow(0)
        editor.prop_name.setText("my_label")
        editor.prop_label.setText("Updated Label")
        editor.prop_placeholder.setText("ph")
        editor.prop_min.setValue(1)
        editor.prop_max.setValue(99)
        editor.prop_required.setChecked(True)
        editor.apply_widget_properties()
        w = editor.widgets[0]
        assert w["name"] == "my_label"
        assert w["label"] == "Updated Label"
        assert w["placeholder"] == "ph"
        assert w["min"] == 1
        assert w["max"] == 99
        assert w["required"] is True

    def test_apply_widget_properties_keeps_original_name_if_empty(self, editor):
        from PyQt6.QtWidgets import QListWidgetItem
        editor.add_widget(QListWidgetItem("Button"))
        original_name = editor.widgets[0]["name"]
        editor.widgets_list.setCurrentRow(0)
        editor.prop_name.setText("")  # empty -> keep original
        editor.apply_widget_properties()
        assert editor.widgets[0]["name"] == original_name

    def test_apply_widget_properties_no_selection_is_safe(self, editor):
        editor.widgets_list.setCurrentRow(-1)
        editor.apply_widget_properties()  # Should not raise

    # --- apply_starter() ---

    def test_apply_starter_data_dashboard(self, editor):
        editor.starter_combo.setCurrentText("Data Dashboard")
        editor.apply_starter()
        assert editor.window_title.text() == "Telemetry Dashboard"
        assert editor.theme.currentText() == "Dark"
        assert editor.layout_type.currentText() == "Grid"
        assert len(editor.widgets) == 4

    def test_apply_starter_neon_game_launcher(self, editor):
        editor.starter_combo.setCurrentText("Neon Game Launcher")
        editor.apply_starter()
        assert editor.window_title.text() == "Arcade Launcher"
        assert editor.button_style.currentText() == "Neon"

    def test_apply_starter_glass_crm_panel(self, editor):
        editor.starter_combo.setCurrentText("Glass CRM Panel")
        editor.apply_starter()
        assert editor.window_title.text() == "Client Command Center"
        assert editor.layout_type.currentText() == "Horizontal"

    def test_apply_starter_replaces_widgets(self, editor):
        from PyQt6.QtWidgets import QListWidgetItem
        editor.add_widget(QListWidgetItem("Label"))
        editor.starter_combo.setCurrentText("Data Dashboard")
        editor.apply_starter()
        # Should have exactly the preset widgets, not the manual one
        assert len(editor.widgets) == 4

    def test_apply_starter_populates_widgets_list_ui(self, editor):
        editor.starter_combo.setCurrentText("Neon Game Launcher")
        editor.apply_starter()
        assert editor.widgets_list.count() == len(STARTER_PRESETS["Neon Game Launcher"]["widgets"])

    # --- _layout_mode_sync() ---

    def test_tabbed_enables_tab_pos(self, editor):
        editor._layout_mode_sync("Tabbed")
        assert editor.tab_pos.isEnabled() is True
        assert editor.grid_cols.isEnabled() is False

    def test_grid_enables_grid_cols(self, editor):
        editor._layout_mode_sync("Grid")
        assert editor.grid_cols.isEnabled() is True
        assert editor.tab_pos.isEnabled() is False

    def test_vertical_disables_both(self, editor):
        editor._layout_mode_sync("Vertical")
        assert editor.tab_pos.isEnabled() is False
        assert editor.grid_cols.isEnabled() is False

    def test_horizontal_disables_both(self, editor):
        editor._layout_mode_sync("Horizontal")
        assert editor.tab_pos.isEnabled() is False
        assert editor.grid_cols.isEnabled() is False


# ===========================================================================
# 8. MainWindow – undo / redo / history  (requires QApplication)
# ===========================================================================

class TestMainWindowHistory:
    @pytest.fixture(autouse=True)
    def _ensure_app(self, qapp):
        pass

    @pytest.fixture
    def win(self):
        from gui_designer import MainWindow
        w = MainWindow()
        yield w
        w.close()

    def test_initial_history_has_one_entry(self, win):
        assert len(win.history) >= 1

    def test_record_history_adds_entry(self, win):
        initial = len(win.history)
        win.editor.window_title.setText("New Title")
        win.record_history()
        assert len(win.history) > initial

    def test_record_history_does_not_duplicate_identical_state(self, win):
        win.record_history()
        count_before = len(win.history)
        win.record_history()  # same state
        assert len(win.history) == count_before

    def test_undo_restores_previous_state(self, win):
        win.editor.window_title.setText("Before")
        win.record_history()

        win.editor.window_title.setText("After")
        win.record_history()

        win.undo()
        assert win.editor.window_title.text() == "Before"

    def test_undo_at_oldest_state_is_noop(self, win):
        # Move to beginning
        while win.history_index > 0:
            win.undo()
        index_before = win.history_index
        win.undo()
        assert win.history_index == index_before

    def test_redo_reapplies_undone_state(self, win):
        win.editor.window_title.setText("State A")
        win.record_history()

        win.editor.window_title.setText("State B")
        win.record_history()

        win.undo()
        assert win.editor.window_title.text() == "State A"

        win.redo()
        assert win.editor.window_title.text() == "State B"

    def test_redo_at_latest_state_is_noop(self, win):
        index_before = win.history_index
        win.redo()
        assert win.history_index == index_before

    def test_new_action_after_undo_truncates_future(self, win):
        win.editor.window_title.setText("A")
        win.record_history()
        win.editor.window_title.setText("B")
        win.record_history()

        win.undo()
        # Now record a new state – B should be gone
        win.editor.window_title.setText("C")
        win.record_history()
        assert len(win.history) == win.history_index + 1
        # Redo should be a noop now
        idx = win.history_index
        win.redo()
        assert win.history_index == idx


# ===========================================================================
# 9. MainWindow – current_project() / apply_project()  (requires QApplication)
# ===========================================================================

class TestMainWindowProject:
    @pytest.fixture(autouse=True)
    def _ensure_app(self, qapp):
        pass

    @pytest.fixture
    def win(self):
        from gui_designer import MainWindow
        w = MainWindow()
        yield w
        w.close()

    def test_current_project_has_expected_keys(self, win):
        p = win.current_project()
        assert "original_script_path" in p
        assert "original_code" in p
        assert "design" in p

    def test_current_project_initial_path_is_none(self, win):
        assert win.current_project()["original_script_path"] is None

    def test_apply_project_restores_title(self, win):
        project = win.current_project()
        project["design"]["window_title"] = "Restored Title"
        win.apply_project(project)
        assert win.editor.window_title.text() == "Restored Title"

    def test_apply_project_restores_script_path(self, win, tmp_path):
        fake_path = str(tmp_path / "script.py")
        project = {"original_script_path": fake_path, "original_code": "x = 1", "design": {}}
        win.apply_project(project)
        assert win.original_script_path == fake_path

    def test_apply_project_restores_original_code(self, win):
        project = {"original_script_path": None, "original_code": "print('hello')", "design": {}}
        win.apply_project(project)
        assert win.original_code == "print('hello')"

    def test_load_script_reads_file(self, win, tmp_path):
        script = tmp_path / "sample.py"
        script.write_text("x = 42\n", encoding="utf-8")
        win.load_script(str(script))
        assert win.original_code == "x = 42\n"
        assert win.original_script_path == str(script)


# ===========================================================================
# 10. MainWindow – generate_gui_code()  (requires QApplication)
# ===========================================================================

class TestGenerateGuiCode:
    @pytest.fixture(autouse=True)
    def _ensure_app(self, qapp):
        pass

    @pytest.fixture
    def win(self):
        from gui_designer import MainWindow
        w = MainWindow()
        yield w
        w.close()

    def _design_with_widget(self, widget_type: str, **overrides):
        d = _minimal_design()
        d["widgets"] = [_make_widget_descriptor(widget_type, **overrides)]
        return d

    def test_returns_string(self, win):
        code = win.generate_gui_code(_minimal_design(), "")
        assert isinstance(code, str)

    def test_contains_original_script(self, win):
        code = win.generate_gui_code(_minimal_design(), "# hello world")
        assert "# hello world" in code

    def test_contains_window_title(self, win):
        d = _minimal_design(window_title="MyCoolApp")
        code = win.generate_gui_code(d, "")
        assert "MyCoolApp" in code

    def test_contains_watermark(self, win):
        code = win.generate_gui_code(_minimal_design(), "")
        assert WATERMARK_TEXT in code

    def test_contains_author_name(self, win):
        code = win.generate_gui_code(_minimal_design(), "")
        assert AUTHOR_NAME in code

    def test_label_widget_generates_qlabel(self, win):
        d = self._design_with_widget("Label")
        code = win.generate_gui_code(d, "")
        assert "QLabel" in code

    def test_button_widget_generates_qpushbutton(self, win):
        d = self._design_with_widget("Button")
        code = win.generate_gui_code(d, "")
        assert "QPushButton" in code

    def test_button_generates_clicked_connect(self, win):
        d = self._design_with_widget("Button")
        code = win.generate_gui_code(d, "")
        assert "clicked.connect" in code

    def test_label_does_not_generate_connect(self, win):
        d = self._design_with_widget("Label")
        code = win.generate_gui_code(d, "")
        assert "clicked.connect" not in code

    def test_spin_box_uses_min_max(self, win):
        d = self._design_with_widget("Spin Box", min=10, max=200)
        code = win.generate_gui_code(d, "")
        assert "10" in code
        assert "200" in code

    def test_grid_layout_uses_row_col(self, win):
        d = _minimal_design(layout_type="Grid", grid_columns=2)
        d["widgets"] = [
            _make_widget_descriptor("Label"),
            _make_widget_descriptor("Button"),
        ]
        d["widgets"][1]["name"] = "button_2"
        code = win.generate_gui_code(d, "")
        # Grid layout should produce addWidget calls with row/column args
        assert "layout.addWidget" in code

    def test_empty_widgets_list_adds_default_label(self, win):
        d = _minimal_design(widgets=[])
        code = win.generate_gui_code(d, "")
        assert "QLabel" in code

    def test_quotes_in_label_escaped(self, win):
        d = self._design_with_widget("Label")
        d["widgets"][0]["label"] = 'Say "hello"'
        code = win.generate_gui_code(d, "")
        assert 'Say \\"hello\\"' in code

    def test_generated_code_has_main_function(self, win):
        code = win.generate_gui_code(_minimal_design(), "")
        assert "def main()" in code

    def test_generated_code_has_original_main(self, win):
        code = win.generate_gui_code(_minimal_design(), "")
        assert "def original_main()" in code

    def test_generated_code_is_valid_python(self, win):
        import py_compile, tempfile
        code = win.generate_gui_code(_minimal_design(), "")
        with tempfile.NamedTemporaryFile(suffix=".py", mode="w", delete=False) as f:
            f.write(code)
            fname = f.name
        try:
            py_compile.compile(fname, doraise=True)
        finally:
            Path(fname).unlink(missing_ok=True)

    def test_line_edit_placeholder_in_generated_code(self, win):
        d = self._design_with_widget("Line Edit", placeholder="Search here")
        code = win.generate_gui_code(d, "")
        assert "Search here" in code

    def test_combo_box_adds_options(self, win):
        d = self._design_with_widget("Combo Box")
        code = win.generate_gui_code(d, "")
        assert "Option A" in code

    def test_group_box_generated(self, win):
        d = self._design_with_widget("Group Box")
        code = win.generate_gui_code(d, "")
        assert "QGroupBox" in code

    def test_unsupported_widget_type_generates_qlabel_fallback(self, win):
        d = _minimal_design()
        d["widgets"] = [{"type": "Alien", "name": "alien_1", "label": "Alien widget", "placeholder": "", "min": 0, "max": 100, "required": False}]
        code = win.generate_gui_code(d, "")
        assert "Unsupported" in code


# ===========================================================================
# 11. MainWindow – generate_prompt_result()  (requires QApplication)
# ===========================================================================

class TestGeneratePromptResult:
    @pytest.fixture(autouse=True)
    def _ensure_app(self, qapp):
        pass

    @pytest.fixture
    def win(self):
        from gui_designer import MainWindow
        w = MainWindow()
        yield w
        w.close()

    def test_imgui_framework_returns_draw_ui_function(self, win):
        result = win.generate_prompt_result("Draw a login form", "ImGui")
        assert "def draw_ui()" in result

    def test_imgui_contains_prompt_text(self, win):
        result = win.generate_prompt_result("Draw a login form", "ImGui")
        assert "Draw a login form" in result

    def test_imgui_contains_skeleton_comment(self, win):
        result = win.generate_prompt_result("something", "ImGui")
        assert "ImGui" in result
        assert "imgui" in result

    def test_imgui_prompt_with_single_quotes_escaped(self, win):
        result = win.generate_prompt_result("It's a test", "ImGui")
        # Should not cause a SyntaxError in the generated string
        assert "It" in result

    def test_generic_gui_returns_concept_text(self, win):
        result = win.generate_prompt_result("Login screen", "Generic GUI")
        assert "Generic GUI" in result
        assert "Login screen" in result

    def test_generic_gui_mentions_sections(self, win):
        result = win.generate_prompt_result("anything", "Generic GUI")
        assert "Sections" in result

    def test_pyqt6_framework_returns_generated_code(self, win):
        result = win.generate_prompt_result("any prompt", "PyQt6")
        # Should return gui code (has CustomGUI class)
        assert "CustomGUI" in result

    def test_empty_prompt_handled_by_caller(self, win):
        # generate_prompt_result itself doesn't guard for empty prompt;
        # but it should not raise
        result = win.generate_prompt_result("", "Generic GUI")
        assert isinstance(result, str)


# ===========================================================================
# 12. MainWindow – on_design_change() summary  (requires QApplication)
# ===========================================================================

class TestOnDesignChange:
    @pytest.fixture(autouse=True)
    def _ensure_app(self, qapp):
        pass

    @pytest.fixture
    def win(self):
        from gui_designer import MainWindow
        w = MainWindow()
        yield w
        w.close()

    def test_summary_includes_window_title(self, win):
        win.editor.window_title.setText("SummaryTest")
        win.on_design_change()
        assert "SummaryTest" in win.summary.text()

    def test_summary_includes_theme(self, win):
        win.editor.theme.setCurrentText("Dark")
        win.on_design_change()
        assert "Dark" in win.summary.text()

    def test_summary_includes_layout(self, win):
        win.editor.layout_type.setCurrentText("Grid")
        win.on_design_change()
        assert "Grid" in win.summary.text()

    def test_summary_widget_count(self, win):
        from PyQt6.QtWidgets import QListWidgetItem
        win.editor.add_widget(QListWidgetItem("Button"))
        win.on_design_change()
        assert "1" in win.summary.text()

    def test_preview_text_is_valid_json(self, win):
        win.on_design_change()
        text = win.editor.preview_text.toPlainText()
        parsed = json.loads(text)
        assert isinstance(parsed, dict)

    def test_script_not_loaded_indicated(self, win):
        win.on_design_change()
        assert "no" in win.summary.text().lower()

    def test_script_loaded_indicated(self, win, tmp_path):
        script = tmp_path / "s.py"
        script.write_text("pass\n", encoding="utf-8")
        win.load_script(str(script))
        assert "yes" in win.summary.text().lower()


# ===========================================================================
# 13. MainWindow – export_ui_file() content  (requires QApplication)
# ===========================================================================

class TestExportUiFile:
    @pytest.fixture(autouse=True)
    def _ensure_app(self, qapp):
        pass

    @pytest.fixture
    def win(self):
        from gui_designer import MainWindow
        w = MainWindow()
        yield w
        w.close()

    def _ui_content_for(self, win, design, tmp_path):
        """Patch file dialog and capture the written .ui content."""
        out = tmp_path / "test.ui"
        with patch("PyQt6.QtWidgets.QFileDialog.getSaveFileName", return_value=(str(out), "")), \
             patch("PyQt6.QtWidgets.QMessageBox.information"):
            win.editor.load_design(design)
            win.export_ui_file()
        return out.read_text(encoding="utf-8") if out.exists() else ""

    def test_valid_xml_header(self, win, tmp_path):
        content = self._ui_content_for(win, _minimal_design(), tmp_path)
        assert content.startswith("<?xml")

    def test_window_title_in_ui(self, win, tmp_path):
        d = _minimal_design(window_title="ExportedUI")
        content = self._ui_content_for(win, d, tmp_path)
        assert "ExportedUI" in content

    def test_label_widget_mapped_to_qlabel(self, win, tmp_path):
        d = _minimal_design()
        d["widgets"] = [_make_widget_descriptor("Label")]
        content = self._ui_content_for(win, d, tmp_path)
        assert "QLabel" in content

    def test_button_widget_mapped_to_qpushbutton(self, win, tmp_path):
        d = _minimal_design()
        d["widgets"] = [_make_widget_descriptor("Button")]
        content = self._ui_content_for(win, d, tmp_path)
        assert "QPushButton" in content

    def test_unknown_widget_type_defaults_to_qlabel(self, win, tmp_path):
        d = _minimal_design()
        d["widgets"] = [{"type": "FancyUnknown", "name": "x_1", "label": "X", "placeholder": "", "min": 0, "max": 100, "required": False}]
        content = self._ui_content_for(win, d, tmp_path)
        assert "QLabel" in content

    def test_no_path_selected_does_nothing(self, win):
        with patch("PyQt6.QtWidgets.QFileDialog.getSaveFileName", return_value=("", "")):
            win.export_ui_file()  # Should not raise


# ===========================================================================
# 14. MainWindow – export_template / import_template JSON  (requires QApplication)
# ===========================================================================

class TestTemplateJsonRoundtrip:
    @pytest.fixture(autouse=True)
    def _ensure_app(self, qapp):
        pass

    @pytest.fixture
    def win(self):
        from gui_designer import MainWindow
        w = MainWindow()
        yield w
        w.close()

    def test_export_import_json_roundtrip(self, win, tmp_path):
        json_file = tmp_path / "template.json"

        # Customise design
        win.editor.window_title.setText("RoundtripTest")
        win.editor.theme.setCurrentText("Dark")

        with patch("PyQt6.QtWidgets.QFileDialog.getSaveFileName", return_value=(str(json_file), "")):
            win.export_template("json")

        assert json_file.exists()
        data = json.loads(json_file.read_text(encoding="utf-8"))
        assert data["window_title"] == "RoundtripTest"
        assert data["theme"] == "Dark"

        # Reset and import
        win.editor.window_title.setText("Reset")
        with patch("PyQt6.QtWidgets.QFileDialog.getOpenFileName", return_value=(str(json_file), "")):
            win.import_template("json")

        assert win.editor.window_title.text() == "RoundtripTest"

    def test_export_json_no_path_does_nothing(self, win, tmp_path):
        with patch("PyQt6.QtWidgets.QFileDialog.getSaveFileName", return_value=("", "")):
            win.export_template("json")  # Should not raise

    def test_import_json_no_path_does_nothing(self, win):
        with patch("PyQt6.QtWidgets.QFileDialog.getOpenFileName", return_value=("", "")):
            win.import_template("json")  # Should not raise


# ===========================================================================
# 15. MainWindow – run_smoke_test()  (requires QApplication)
# ===========================================================================

class TestRunSmokeTest:
    @pytest.fixture(autouse=True)
    def _ensure_app(self, qapp):
        pass

    @pytest.fixture
    def win(self):
        from gui_designer import MainWindow
        w = MainWindow()
        yield w
        w.close()

    def test_smoke_test_passes_for_valid_generated_code(self, win):
        with patch("PyQt6.QtWidgets.QMessageBox.information") as info_mock:
            win.run_smoke_test()
        info_mock.assert_called_once()
        call_args = info_mock.call_args[0]
        assert "passed" in call_args[2].lower() or "smoke" in call_args[1].lower()

    def test_smoke_test_fails_for_invalid_code(self, win):
        broken = "this is not valid python @@@@"
        with patch.object(win, "generate_gui_code", return_value=broken), \
             patch("PyQt6.QtWidgets.QMessageBox.critical") as crit_mock:
            win.run_smoke_test()
        crit_mock.assert_called_once()


# ===========================================================================
# 16. Regression / boundary tests
# ===========================================================================

class TestRegressionAndBoundary:
    @pytest.fixture(autouse=True)
    def _ensure_app(self, qapp):
        pass

    @pytest.fixture
    def win(self):
        from gui_designer import MainWindow
        w = MainWindow()
        yield w
        w.close()

    def test_design_window_title_empty_string_defaults_to_custom_gui(self, win):
        win.editor.window_title.setText("")
        d = win.editor.design()
        assert d["window_title"] == "Custom GUI"

    def test_grid_layout_one_column_no_division_error(self, win):
        d = _minimal_design(layout_type="Grid", grid_columns=1)
        d["widgets"] = [_make_widget_descriptor("Label"), _make_widget_descriptor("Button")]
        d["widgets"][1]["name"] = "button_2"
        code = win.generate_gui_code(d, "")
        assert "QLabel" in code

    def test_history_index_never_negative_after_multiple_undos(self, win):
        for _ in range(20):
            win.undo()
        assert win.history_index >= 0

    def test_generate_gui_code_large_original_code(self, win):
        large_code = "x = 1\n" * 5000
        code = win.generate_gui_code(_minimal_design(), large_code)
        assert isinstance(code, str)
        assert len(code) > 0

    def test_make_widget_label_with_special_chars(self):
        from PyQt6.QtWidgets import QLabel
        w = make_widget({"type": "Label", "label": "<b>Bold & special</b>"})
        assert isinstance(w, QLabel)

    def test_build_stylesheet_empty_button_style(self):
        d = _minimal_design(button_style="NonExistent")
        css = build_stylesheet(d)
        # STYLE_PRESETS.get returns "" for unknown; should still produce valid CSS
        assert isinstance(css, str)

    def test_default_widget_type_with_numbers(self):
        w = default_widget("Label", 12345)
        assert w["name"] == "label_12345"

    def test_apply_project_with_missing_keys_does_not_raise(self, win):
        # Partial project dict – missing some keys
        win.apply_project({"design": {}})
        assert win.original_code == ""

    def test_add_then_clear_then_add_widget_indexes_correctly(self, win):
        from PyQt6.QtWidgets import QListWidgetItem
        win.editor.add_widget(QListWidgetItem("Label"))
        win.editor.clear_widgets()
        win.editor.add_widget(QListWidgetItem("Button"))
        # After clear, next widget should be at index 1 in name
        assert win.editor.widgets[0]["name"] == "button_1"

    def test_generate_gui_code_with_text_edit_widget(self, win):
        d = _minimal_design()
        d["widgets"] = [_make_widget_descriptor("Text Edit", placeholder="Enter text")]
        code = win.generate_gui_code(d, "")
        assert "QTextEdit" in code
        assert "Enter text" in code

    def test_generate_gui_code_with_check_box_widget(self, win):
        d = _minimal_design()
        d["widgets"] = [_make_widget_descriptor("Check Box")]
        code = win.generate_gui_code(d, "")
        assert "QCheckBox" in code