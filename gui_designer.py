#!/usr/bin/env python3
"""Advanced GUI Designer for Python Scripts (PyQt6)."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from copy import deepcopy
from pathlib import Path
from typing import Any

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QDragEnterEvent, QDropEvent, QFont
from PyQt6.QtWidgets import (
    QApplication,
    QCheckBox,
    QColorDialog,
    QComboBox,
    QFileDialog,
    QFormLayout,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QSplitter,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

AUTHOR_NAME = "Justin Lorenc"
AUTHOR_EMAIL = "midnight-repo@engineer.com"
WATERMARK_TEXT = f"© {AUTHOR_NAME} | Licensed use only | Contact: {AUTHOR_EMAIL}"

STARTER_PRESETS: dict[str, dict[str, Any]] = {
    "Data Dashboard": {
        "window_title": "Telemetry Dashboard",
        "theme": "Dark",
        "layout_type": "Grid",
        "grid_columns": 2,
        "button_style": "Modern",
        "widgets": [
            {"type": "Label", "name": "title_1", "label": "System Status", "placeholder": "", "min": 0, "max": 100, "required": False},
            {"type": "Text Edit", "name": "log_1", "label": "Live logs...", "placeholder": "Log stream", "min": 0, "max": 100, "required": False},
            {"type": "Spin Box", "name": "interval_1", "label": "Refresh ms", "placeholder": "", "min": 100, "max": 5000, "required": True},
            {"type": "Button", "name": "refresh_1", "label": "Refresh now", "placeholder": "", "min": 0, "max": 100, "required": False},
        ],
    },
    "Neon Game Launcher": {
        "window_title": "Arcade Launcher",
        "theme": "Gradient",
        "layout_type": "Vertical",
        "button_style": "Neon",
        "widgets": [
            {"type": "Label", "name": "hero_1", "label": "Choose Your Arena", "placeholder": "", "min": 0, "max": 100, "required": False},
            {"type": "Combo Box", "name": "mode_1", "label": "Mode", "placeholder": "", "min": 0, "max": 100, "required": False},
            {"type": "Check Box", "name": "vsync_1", "label": "Enable VSync", "placeholder": "", "min": 0, "max": 100, "required": False},
            {"type": "Button", "name": "play_1", "label": "Launch", "placeholder": "", "min": 0, "max": 100, "required": True},
        ],
    },
    "Glass CRM Panel": {
        "window_title": "Client Command Center",
        "theme": "Glass",
        "layout_type": "Horizontal",
        "button_style": "Rounded",
        "widgets": [
            {"type": "Line Edit", "name": "search_1", "label": "Search client", "placeholder": "Type customer name", "min": 1, "max": 80, "required": True},
            {"type": "Text Edit", "name": "notes_1", "label": "Engagement notes", "placeholder": "Key details", "min": 0, "max": 2000, "required": False},
            {"type": "Button", "name": "save_1", "label": "Save snapshot", "placeholder": "", "min": 0, "max": 100, "required": False},
        ],
    },
}

STYLE_PRESETS = {
    "Default": "",
    "Flat": "QPushButton { border: none; background:#ddd; padding: 7px; } QPushButton:hover {background:#bbb;}",
    "Modern": "QPushButton { background:#3498db; color:white; border-radius:6px; padding:8px; } QPushButton:hover {background:#2980b9;}",
    "Rounded": "QPushButton { border:2px solid #aaa; border-radius:14px; padding:7px; } QPushButton:hover {background:#eee;}",
    "Neon": "QPushButton {color:#00ff9f; border:1px solid #00ff9f; background:#101820; border-radius:8px; padding:8px;} QPushButton:hover {background:#152a2b;}",
}


def default_widget(widget_type: str, idx: int) -> dict[str, Any]:
    return {
        "type": widget_type,
        "name": f"{widget_type.lower().replace(' ', '_')}_{idx}",
        "label": f"{widget_type} {idx}",
        "placeholder": "",
        "min": 0,
        "max": 100,
        "required": False,
    }


def yaml_available() -> bool:
    try:
        import yaml  # type: ignore # noqa: F401

        return True
    except Exception:
        return False


class DropArea(QLabel):
    def __init__(self, main_window: "MainWindow"):
        super().__init__("Drop your Python file here\n(.py)")
        self.main_window = main_window
        self.setAcceptDrops(True)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setMinimumHeight(220)
        self.setStyleSheet("border: 3px dashed #8a8a8a; border-radius: 10px; padding: 38px;")

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        for url in event.mimeData().urls():
            path = url.toLocalFile()
            if path.endswith(".py"):
                self.main_window.load_script(path)
                self.setText(f"Loaded: {os.path.basename(path)}")
                break
        event.acceptProposedAction()


class PropertyEditor(QWidget):
    available_widgets = [
        "Label",
        "Button",
        "Line Edit",
        "Text Edit",
        "Check Box",
        "Combo Box",
        "Spin Box",
        "Group Box",
    ]

    def __init__(self, main_window: "MainWindow"):
        super().__init__(main_window)
        self.main_window = main_window
        self.widgets: list[dict[str, Any]] = []

        self.tabs = QTabWidget()
        self._style_tab()
        self._layout_tab()
        self._widgets_tab()
        self._preview_tab()
        self._code_tab()
        self._assistant_tab()

        root = QVBoxLayout(self)
        root.addWidget(self.tabs)

        self._wire_updates()

    def _style_tab(self):
        tab = QWidget()
        form = QFormLayout(tab)
        self.window_title = QLineEdit("My Custom GUI")
        self.bg_btn = QPushButton("Background Color")
        self.bg_label = QLabel("#ffffff")
        self.accent_btn = QPushButton("Accent Color")
        self.accent_label = QLabel("#3498db")
        self.theme = QComboBox()
        self.theme.addItems(["Light", "Dark", "Gradient", "Glass"])
        self.button_style = QComboBox()
        self.button_style.addItems(list(STYLE_PRESETS))

        self.bg_btn.clicked.connect(lambda: self._pick_color(self.bg_label))
        self.accent_btn.clicked.connect(lambda: self._pick_color(self.accent_label))

        form.addRow("Window Title", self.window_title)
        form.addRow("Background", self.bg_btn)
        form.addRow("", self.bg_label)
        form.addRow("Accent", self.accent_btn)
        form.addRow("", self.accent_label)
        form.addRow("Theme", self.theme)
        form.addRow("Button Style", self.button_style)
        self.tabs.addTab(tab, "Style")

    def _layout_tab(self):
        tab = QWidget()
        form = QFormLayout(tab)
        self.layout_type = QComboBox()
        self.layout_type.addItems(["Vertical", "Horizontal", "Grid", "Tabbed"])
        self.tab_pos = QComboBox()
        self.tab_pos.addItems(["North", "South", "West", "East"])
        self.grid_cols = QSpinBox()
        self.grid_cols.setRange(1, 8)
        self.grid_cols.setValue(2)
        self.margin = QSpinBox()
        self.margin.setRange(0, 60)
        self.margin.setValue(10)
        self.spacing = QSpinBox()
        self.spacing.setRange(0, 40)
        self.spacing.setValue(8)

        self.layout_type.currentTextChanged.connect(self._layout_mode_sync)

        form.addRow("Layout", self.layout_type)
        form.addRow("Tab Position", self.tab_pos)
        form.addRow("Grid Columns", self.grid_cols)
        form.addRow("Margin", self.margin)
        form.addRow("Spacing", self.spacing)
        self.tabs.addTab(tab, "Layout")

    def _widgets_tab(self):
        tab = QWidget()
        h = QHBoxLayout(tab)

        left = QVBoxLayout()
        self.widget_catalog = QListWidget()
        for item in self.available_widgets:
            self.widget_catalog.addItem(item)
        self.widget_catalog.itemDoubleClicked.connect(self.add_widget)

        self.widgets_list = QListWidget()
        self.widgets_list.currentRowChanged.connect(self._load_widget_properties)
        remove_btn = QPushButton("Remove")
        remove_btn.clicked.connect(self.remove_widget)
        clear_btn = QPushButton("Clear")
        clear_btn.clicked.connect(self.clear_widgets)

        left.addWidget(QLabel("Double-click to add"))
        left.addWidget(self.widget_catalog)
        left.addWidget(QLabel("Added widgets"))
        left.addWidget(self.widgets_list)
        left.addWidget(remove_btn)
        left.addWidget(clear_btn)

        right_group = QGroupBox("Component Property Editor")
        form = QFormLayout(right_group)
        self.prop_name = QLineEdit()
        self.prop_label = QLineEdit()
        self.prop_placeholder = QLineEdit()
        self.prop_min = QSpinBox()
        self.prop_min.setRange(-100000, 100000)
        self.prop_max = QSpinBox()
        self.prop_max.setRange(-100000, 100000)
        self.prop_required = QCheckBox("Required")
        apply_props = QPushButton("Apply Widget Properties")
        apply_props.clicked.connect(self.apply_widget_properties)

        form.addRow("Name", self.prop_name)
        form.addRow("Label/Text", self.prop_label)
        form.addRow("Placeholder", self.prop_placeholder)
        form.addRow("Min", self.prop_min)
        form.addRow("Max", self.prop_max)
        form.addRow("Validation", self.prop_required)
        form.addRow("", apply_props)

        h.addLayout(left, 2)
        h.addWidget(right_group, 3)
        self.tabs.addTab(tab, "Widgets")

    def _preview_tab(self):
        tab = QWidget()
        v = QVBoxLayout(tab)
        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        open_preview = QPushButton("Open Live Preview")
        open_preview.clicked.connect(self.main_window.open_live_preview)

        starter_row = QHBoxLayout()
        self.starter_combo = QComboBox()
        self.starter_combo.addItems(list(STARTER_PRESETS.keys()))
        apply_starter = QPushButton("Apply Starter")
        apply_starter.clicked.connect(self.apply_starter)
        starter_row.addWidget(self.starter_combo)
        starter_row.addWidget(apply_starter)

        v.addWidget(QLabel("Starter presets"))
        v.addLayout(starter_row)
        v.addWidget(self.preview_text)
        v.addWidget(open_preview)
        self.tabs.addTab(tab, "Preview")

    def _code_tab(self):
        tab = QWidget()
        v = QVBoxLayout(tab)
        self.code_preview = QTextEdit()
        self.code_preview.setReadOnly(True)
        self.code_preview.setFont(QFont("Monospace", 10))

        row = QHBoxLayout()
        refresh = QPushButton("Refresh")
        save = QPushButton("Save Generated Script")
        export_ui = QPushButton("Export .ui")
        smoke = QPushButton("Smoke Test Generated Script")

        refresh.clicked.connect(self.main_window.refresh_code_preview)
        save.clicked.connect(self.save_script)
        export_ui.clicked.connect(self.main_window.export_ui_file)
        smoke.clicked.connect(self.main_window.run_smoke_test)

        row.addWidget(refresh)
        row.addWidget(save)
        row.addWidget(export_ui)
        row.addWidget(smoke)

        v.addWidget(self.code_preview)
        v.addLayout(row)
        self.tabs.addTab(tab, "Code")

    def _assistant_tab(self):
        tab = QWidget()
        v = QVBoxLayout(tab)
        self.framework_combo = QComboBox()
        self.framework_combo.addItems(["PyQt6", "Generic GUI", "ImGui"])
        self.prompt_input = QTextEdit()
        self.prompt_input.setPlaceholderText("Describe your desired UI and behavior...")
        self.assistant_output = QTextEdit()
        self.assistant_output.setReadOnly(True)
        run = QPushButton("Generate from Prompt")
        run.clicked.connect(self.generate_from_prompt)

        v.addWidget(QLabel("Framework target"))
        v.addWidget(self.framework_combo)
        v.addWidget(self.prompt_input)
        v.addWidget(run)
        v.addWidget(self.assistant_output)
        self.tabs.addTab(tab, "Assistant")

    def _wire_updates(self):
        for control, signal_name in [
            (self.window_title, "textChanged"),
            (self.theme, "currentTextChanged"),
            (self.button_style, "currentTextChanged"),
            (self.layout_type, "currentTextChanged"),
            (self.tab_pos, "currentTextChanged"),
            (self.grid_cols, "valueChanged"),
            (self.margin, "valueChanged"),
            (self.spacing, "valueChanged"),
        ]:
            getattr(control, signal_name).connect(self.main_window.on_design_change)

    def _pick_color(self, label: QLabel):
        color = QColorDialog.getColor()
        if color.isValid():
            label.setText(color.name())
            label.setStyleSheet(f"background:{color.name()}; padding:4px; border:1px solid #ccc;")
            self.main_window.on_design_change()

    def _layout_mode_sync(self, mode: str):
        self.tab_pos.setEnabled(mode == "Tabbed")
        self.grid_cols.setEnabled(mode == "Grid")
        self.main_window.on_design_change()

    def add_widget(self, item: QListWidgetItem):
        widget = default_widget(item.text(), len(self.widgets) + 1)
        self.widgets.append(widget)
        self.widgets_list.addItem(f"{widget['type']} • {widget['name']}")
        self.widgets_list.setCurrentRow(len(self.widgets) - 1)
        self.main_window.record_history()
        self.main_window.on_design_change()

    def remove_widget(self):
        row = self.widgets_list.currentRow()
        if row < 0:
            return
        self.widgets.pop(row)
        self.widgets_list.takeItem(row)
        self.main_window.record_history()
        self.main_window.on_design_change()

    def clear_widgets(self):
        self.widgets.clear()
        self.widgets_list.clear()
        self.main_window.record_history()
        self.main_window.on_design_change()

    def _load_widget_properties(self, row: int):
        if row < 0 or row >= len(self.widgets):
            return
        w = self.widgets[row]
        self.prop_name.setText(w["name"])
        self.prop_label.setText(w["label"])
        self.prop_placeholder.setText(w.get("placeholder", ""))
        self.prop_min.setValue(int(w.get("min", 0)))
        self.prop_max.setValue(int(w.get("max", 100)))
        self.prop_required.setChecked(bool(w.get("required", False)))

    def apply_widget_properties(self):
        row = self.widgets_list.currentRow()
        if row < 0 or row >= len(self.widgets):
            return
        self.widgets[row].update(
            {
                "name": self.prop_name.text().strip() or self.widgets[row]["name"],
                "label": self.prop_label.text().strip() or self.widgets[row]["label"],
                "placeholder": self.prop_placeholder.text().strip(),
                "min": self.prop_min.value(),
                "max": self.prop_max.value(),
                "required": self.prop_required.isChecked(),
            }
        )
        self.widgets_list.item(row).setText(f"{self.widgets[row]['type']} • {self.widgets[row]['name']}")
        self.main_window.record_history()
        self.main_window.on_design_change()

    def apply_starter(self):
        starter = deepcopy(STARTER_PRESETS[self.starter_combo.currentText()])
        self.window_title.setText(starter.get("window_title", "My Custom GUI"))
        self.theme.setCurrentText(starter.get("theme", "Light"))
        self.layout_type.setCurrentText(starter.get("layout_type", "Vertical"))
        self.grid_cols.setValue(int(starter.get("grid_columns", 2)))
        self.button_style.setCurrentText(starter.get("button_style", "Default"))
        self.widgets = starter.get("widgets", [])
        self.widgets_list.clear()
        for w in self.widgets:
            self.widgets_list.addItem(f"{w['type']} • {w['name']}")
        self.main_window.record_history()
        self.main_window.on_design_change()

    def save_script(self):
        if not self.main_window.original_script_path:
            QMessageBox.warning(self, "No Script", "Drop a Python script first.")
            return
        path, _ = QFileDialog.getSaveFileName(self, "Save Generated Script", "", "Python Files (*.py)")
        if path:
            self.main_window.generate_merged_script(path)

    def generate_from_prompt(self):
        prompt = self.prompt_input.toPlainText().strip()
        if not prompt:
            return
        framework = self.framework_combo.currentText()
        generated = self.main_window.generate_prompt_result(prompt, framework)
        self.assistant_output.setPlainText(generated)

    def design(self) -> dict[str, Any]:
        return {
            "window_title": self.window_title.text().strip() or "Custom GUI",
            "bg_color": self.bg_label.text(),
            "accent_color": self.accent_label.text(),
            "theme": self.theme.currentText(),
            "button_style": self.button_style.currentText(),
            "layout_type": self.layout_type.currentText(),
            "tab_position": self.tab_pos.currentText(),
            "grid_columns": self.grid_cols.value(),
            "margin": self.margin.value(),
            "spacing": self.spacing.value(),
            "widgets": deepcopy(self.widgets),
        }

    def load_design(self, data: dict[str, Any]):
        self.window_title.setText(data.get("window_title", "Custom GUI"))
        self.bg_label.setText(data.get("bg_color", "#ffffff"))
        self.accent_label.setText(data.get("accent_color", "#3498db"))
        self.theme.setCurrentText(data.get("theme", "Light"))
        self.button_style.setCurrentText(data.get("button_style", "Default"))
        self.layout_type.setCurrentText(data.get("layout_type", "Vertical"))
        self.tab_pos.setCurrentText(data.get("tab_position", "North"))
        self.grid_cols.setValue(int(data.get("grid_columns", 2)))
        self.margin.setValue(int(data.get("margin", 10)))
        self.spacing.setValue(int(data.get("spacing", 8)))

        self.widgets = deepcopy(data.get("widgets", []))
        self.widgets_list.clear()
        for w in self.widgets:
            self.widgets_list.addItem(f"{w['type']} • {w['name']}")


class PreviewWindow(QWidget):
    def __init__(self, design: dict[str, Any]):
        super().__init__()
        self.setWindowTitle(f"Preview • {design['window_title']}")
        self.resize(700, 430)
        self.setStyleSheet(build_stylesheet(design))

        root = QVBoxLayout(self)
        root.setContentsMargins(design["margin"], design["margin"], design["margin"], design["margin"])
        root.setSpacing(design["spacing"])
        root.addWidget(QLabel(design["window_title"]))

        area = QWidget()
        lay = build_layout(design, area)
        for w in design["widgets"]:
            lay.addWidget(make_widget(w))
        root.addWidget(area)

        wm = QLabel(WATERMARK_TEXT)
        wm.setObjectName("watermark")
        wm.setAlignment(Qt.AlignmentFlag.AlignRight)
        root.addWidget(wm)


def make_widget(widget: dict[str, Any]) -> QWidget:
    t = widget["type"]
    label = widget.get("label", t)
    if t == "Label":
        return QLabel(label)
    if t == "Button":
        return QPushButton(label)
    if t == "Line Edit":
        line = QLineEdit()
        line.setPlaceholderText(widget.get("placeholder", label))
        return line
    if t == "Text Edit":
        text = QTextEdit()
        text.setPlaceholderText(widget.get("placeholder", label))
        text.setMinimumHeight(90)
        return text
    if t == "Check Box":
        return QCheckBox(label)
    if t == "Combo Box":
        combo = QComboBox()
        combo.addItems(["Option A", "Option B", "Option C"])
        return combo
    if t == "Spin Box":
        s = QSpinBox()
        s.setRange(int(widget.get("min", 0)), int(widget.get("max", 100)))
        return s
    if t == "Group Box":
        g = QGroupBox(label)
        v = QVBoxLayout(g)
        v.addWidget(QLabel("Group content"))
        return g
    return QLabel(f"Unsupported: {t}")


def build_layout(design: dict[str, Any], parent: QWidget):
    lt = design["layout_type"]
    if lt == "Horizontal":
        lay = QHBoxLayout(parent)
    elif lt == "Grid":
        lay = QGridLayout(parent)
    else:
        lay = QVBoxLayout(parent)
    lay.setContentsMargins(design["margin"], design["margin"], design["margin"], design["margin"])
    lay.setSpacing(design["spacing"])
    return lay


def build_stylesheet(design: dict[str, Any]) -> str:
    bg = design["bg_color"]
    accent = design["accent_color"]
    theme_css = {
        "Light": f"QWidget {{ background: {bg}; color: #1f2937; }}",
        "Dark": f"QWidget {{ background: {bg}; color: #ecf0f1; }}",
        "Gradient": f"QWidget {{ background: qlineargradient(x1:0,y1:0,x2:1,y2:1, stop:0 {bg}, stop:1 {accent}); color: #f9fafb; }}",
        "Glass": (
            f"QWidget {{ background: {bg}; color:#f9fafb; }}"
            "QGroupBox, QTextEdit, QLineEdit { background: rgba(255,255,255,0.1); border:1px solid rgba(255,255,255,0.2); border-radius:8px; }"
        ),
    }
    return "\n".join(
        [
            theme_css.get(design["theme"], theme_css["Light"]),
            STYLE_PRESETS.get(design["button_style"], ""),
            "#watermark { font-size: 10px; color: rgba(255,255,255,0.55); }",
        ]
    )


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GUI Designer")
        self.resize(1360, 900)
        self.original_script_path: str | None = None
        self.original_code = ""
        self.preview_window: PreviewWindow | None = None

        self.history: list[dict[str, Any]] = []
        self.history_index = -1

        self._build_menu()

        splitter = QSplitter(Qt.Orientation.Horizontal)
        left = QWidget()
        lv = QVBoxLayout(left)
        self.drop_area = DropArea(self)
        self.summary = QLabel()
        self.summary.setFrameStyle(QFrame.Shape.Box)
        self.summary.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self.summary.setMinimumHeight(310)
        self.watermark = QLabel(WATERMARK_TEXT)
        self.watermark.setStyleSheet("font-style:italic; color:#7f8c8d;")

        lv.addWidget(self.drop_area)
        lv.addWidget(self.summary)
        lv.addWidget(self.watermark)

        self.editor = PropertyEditor(self)
        splitter.addWidget(left)
        splitter.addWidget(self.editor)
        splitter.setSizes([690, 670])

        self.setCentralWidget(splitter)
        self.statusBar().showMessage(f"License: Proprietary • {AUTHOR_NAME} • {AUTHOR_EMAIL}")

        self.record_history()
        self.on_design_change()

    def _build_menu(self):
        file_menu = self.menuBar().addMenu("File")

        save_project = file_menu.addAction("Save Project")
        save_project.triggered.connect(self.save_project)
        load_project = file_menu.addAction("Load Project")
        load_project.triggered.connect(self.load_project)

        export_json = file_menu.addAction("Export Template (JSON)")
        export_json.triggered.connect(lambda: self.export_template("json"))
        import_json = file_menu.addAction("Import Template (JSON)")
        import_json.triggered.connect(lambda: self.import_template("json"))

        export_yaml = file_menu.addAction("Export Template (YAML)")
        export_yaml.triggered.connect(lambda: self.export_template("yaml"))
        import_yaml = file_menu.addAction("Import Template (YAML)")
        import_yaml.triggered.connect(lambda: self.import_template("yaml"))

        edit_menu = self.menuBar().addMenu("Edit")
        undo = edit_menu.addAction("Undo")
        undo.setShortcut("Ctrl+Z")
        undo.triggered.connect(self.undo)
        redo = edit_menu.addAction("Redo")
        redo.setShortcut("Ctrl+Y")
        redo.triggered.connect(self.redo)

    def load_script(self, path: str):
        self.original_script_path = path
        self.original_code = Path(path).read_text(encoding="utf-8")
        self.on_design_change()

    def open_live_preview(self):
        self.preview_window = PreviewWindow(self.editor.design())
        self.preview_window.show()

    def on_design_change(self):
        d = self.editor.design()
        self.summary.setText(
            "\n".join(
                [
                    f"Window: {d['window_title']}",
                    f"Theme: {d['theme']}",
                    f"Layout: {d['layout_type']}",
                    f"Widgets: {len(d['widgets'])}",
                    f"Script loaded: {'yes' if self.original_script_path else 'no'}",
                ]
            )
        )
        self.editor.preview_text.setPlainText(json.dumps(d, indent=2))
        self.refresh_code_preview()

    def current_project(self) -> dict[str, Any]:
        return {
            "original_script_path": self.original_script_path,
            "original_code": self.original_code,
            "design": self.editor.design(),
        }

    def apply_project(self, project: dict[str, Any]):
        self.original_script_path = project.get("original_script_path")
        self.original_code = project.get("original_code", "")
        self.editor.load_design(project.get("design", {}))
        self.on_design_change()

    def record_history(self):
        snap = deepcopy(self.current_project())
        if self.history_index >= 0 and self.history_index < len(self.history):
            if snap == self.history[self.history_index]:
                return
        self.history = self.history[: self.history_index + 1]
        self.history.append(snap)
        self.history_index = len(self.history) - 1

    def undo(self):
        if self.history_index <= 0:
            return
        self.history_index -= 1
        self.apply_project(deepcopy(self.history[self.history_index]))

    def redo(self):
        if self.history_index >= len(self.history) - 1:
            return
        self.history_index += 1
        self.apply_project(deepcopy(self.history[self.history_index]))

    def save_project(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save Project", "", "GUI Designer Project (*.gdp.json)")
        if not path:
            return
        Path(path).write_text(json.dumps(self.current_project(), indent=2), encoding="utf-8")
        QMessageBox.information(self, "Saved", f"Project saved to:\n{path}")

    def load_project(self):
        path, _ = QFileDialog.getOpenFileName(self, "Load Project", "", "GUI Designer Project (*.gdp.json)")
        if not path:
            return
        project = json.loads(Path(path).read_text(encoding="utf-8"))
        self.apply_project(project)
        self.record_history()

    def export_template(self, fmt: str):
        design = self.editor.design()
        if fmt == "json":
            path, _ = QFileDialog.getSaveFileName(self, "Export JSON Template", "", "JSON (*.json)")
            if path:
                Path(path).write_text(json.dumps(design, indent=2), encoding="utf-8")
            return

        if not yaml_available():
            QMessageBox.warning(self, "Missing dependency", "Install PyYAML to export YAML templates: pip install pyyaml")
            return

        import yaml  # type: ignore

        path, _ = QFileDialog.getSaveFileName(self, "Export YAML Template", "", "YAML (*.yml *.yaml)")
        if path:
            Path(path).write_text(yaml.safe_dump(design, sort_keys=False), encoding="utf-8")

    def import_template(self, fmt: str):
        if fmt == "json":
            path, _ = QFileDialog.getOpenFileName(self, "Import JSON Template", "", "JSON (*.json)")
            if not path:
                return
            design = json.loads(Path(path).read_text(encoding="utf-8"))
        else:
            if not yaml_available():
                QMessageBox.warning(self, "Missing dependency", "Install PyYAML to import YAML templates: pip install pyyaml")
                return
            import yaml  # type: ignore

            path, _ = QFileDialog.getOpenFileName(self, "Import YAML Template", "", "YAML (*.yml *.yaml)")
            if not path:
                return
            design = yaml.safe_load(Path(path).read_text(encoding="utf-8"))

        self.editor.load_design(design)
        self.record_history()
        self.on_design_change()

    def refresh_code_preview(self):
        code = self.generate_gui_code(self.editor.design(), self.original_code)
        self.editor.code_preview.setPlainText(code[:15000] + ("\n# ... truncated" if len(code) > 15000 else ""))

    def generate_merged_script(self, output_path: str):
        code = self.generate_gui_code(self.editor.design(), self.original_code)
        Path(output_path).write_text(code, encoding="utf-8")
        QMessageBox.information(self, "Saved", f"Generated script saved to:\n{output_path}")

    def export_ui_file(self):
        path, _ = QFileDialog.getSaveFileName(self, "Export Qt Designer UI", "", "Qt Designer UI (*.ui)")
        if not path:
            return
        d = self.editor.design()
        ui_lines = [
            "<?xml version=\"1.0\" encoding=\"UTF-8\"?>",
            "<ui version=\"4.0\">",
            " <class>MainWindow</class>",
            " <widget class=\"QMainWindow\" name=\"MainWindow\">",
            f"  <property name=\"windowTitle\"><string>{d['window_title']}</string></property>",
            "  <widget class=\"QWidget\" name=\"centralwidget\">",
            "   <layout class=\"QVBoxLayout\" name=\"verticalLayout\">",
        ]
        for w in d["widgets"]:
            qt_class = {
                "Label": "QLabel",
                "Button": "QPushButton",
                "Line Edit": "QLineEdit",
                "Text Edit": "QTextEdit",
                "Check Box": "QCheckBox",
                "Combo Box": "QComboBox",
                "Spin Box": "QSpinBox",
                "Group Box": "QGroupBox",
            }.get(w["type"], "QLabel")
            ui_lines.extend(
                [
                    "    <item>",
                    f"     <widget class=\"{qt_class}\" name=\"{w['name']}\">",
                    f"      <property name=\"toolTip\"><string>{w.get('label', '')}</string></property>",
                    "     </widget>",
                    "    </item>",
                ]
            )
        ui_lines.extend(
            [
                "   </layout>",
                "  </widget>",
                " </widget>",
                " <resources/>",
                " <connections/>",
                "</ui>",
            ]
        )
        Path(path).write_text("\n".join(ui_lines), encoding="utf-8")
        QMessageBox.information(self, "Exported", f".ui file exported to:\n{path}")

    def run_smoke_test(self):
        generated = self.generate_gui_code(self.editor.design(), self.original_code)
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "generated.py"
            p.write_text(generated, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, "-m", "py_compile", str(p)],
                capture_output=True,
                text=True,
                check=False,
            )
        if result.returncode == 0:
            QMessageBox.information(self, "Smoke Test", "Smoke test passed: generated script compiles.")
        else:
            QMessageBox.critical(self, "Smoke Test Failed", result.stderr or result.stdout or "Unknown error")

    def generate_prompt_result(self, prompt: str, framework: str) -> str:
        if framework == "ImGui":
            return (
                "# ImGui skeleton generated from prompt\n"
                "# NOTE: Integrate with pyimgui/glfw runtime in your project.\n"
                f"# Prompt: {prompt}\n\n"
                "def draw_ui():\n"
                "    import imgui\n"
                "    imgui.begin('AI Panel')\n"
                "    imgui.text('Generated from prompt')\n"
                "    imgui.text_wrapped('" + prompt.replace("'", "\\'") + "')\n"
                "    if imgui.button('Run action'):\n"
                "        pass\n"
                "    imgui.end()\n"
            )
        if framework == "Generic GUI":
            return f"# Generic GUI concept\n# Prompt: {prompt}\nSections: Header, Controls, Output, Footer watermark."
        return self.generate_gui_code(self.editor.design(), self.original_code)

    def generate_gui_code(self, design: dict[str, Any], original_code: str) -> str:
        widgets = design["widgets"] or [default_widget("Label", 1)]

        create_lines: list[str] = []
        add_lines: list[str] = []
        for i, w in enumerate(widgets):
            n = w["name"]
            label = str(w.get("label", w["type"])).replace('"', '\\"')
            placeholder = str(w.get("placeholder", "")).replace('"', '\\"')
            wmin = int(w.get("min", 0))
            wmax = int(w.get("max", 100))
            t = w["type"]

            if t == "Label":
                create_lines.append(f'self.{n} = QLabel("{label}")')
            elif t == "Button":
                create_lines.append(f'self.{n} = QPushButton("{label}")')
            elif t == "Line Edit":
                create_lines.append(f'self.{n} = QLineEdit(); self.{n}.setPlaceholderText("{placeholder or label}")')
            elif t == "Text Edit":
                create_lines.append(f'self.{n} = QTextEdit(); self.{n}.setPlaceholderText("{placeholder or label}")')
            elif t == "Check Box":
                create_lines.append(f'self.{n} = QCheckBox("{label}")')
            elif t == "Combo Box":
                create_lines.append(f"self.{n} = QComboBox(); self.{n}.addItems(['Option A', 'Option B', 'Option C'])")
            elif t == "Spin Box":
                create_lines.append(f"self.{n} = QSpinBox(); self.{n}.setRange({wmin}, {wmax})")
            elif t == "Group Box":
                create_lines.append(f'self.{n} = QGroupBox("{label}"); _{n} = QVBoxLayout(self.{n}); _{n}.addWidget(QLabel("Group content"))')
            else:
                create_lines.append(f'self.{n} = QLabel("Unsupported: {t}")')

            if design["layout_type"] == "Grid":
                cols = max(1, int(design["grid_columns"]))
                r, c = divmod(i, cols)
                add_lines.append(f"layout.addWidget(self.{n}, {r}, {c})")
            else:
                add_lines.append(f"layout.addWidget(self.{n})")

        connect_lines = [f"self.{w['name']}.clicked.connect(self.run_original)" for w in widgets if w["type"] == "Button"]

        return f'''"""
Generated by GUI Designer
Copyright © {AUTHOR_NAME}
Contact: {AUTHOR_EMAIL}
License: Proprietary (see LICENSE)
"""

ORIGINAL_SCRIPT = {original_code!r}

import sys
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QApplication, QLabel, QPushButton, QLineEdit, QTextEdit, QCheckBox,
    QComboBox, QSpinBox, QGroupBox, QVBoxLayout, QHBoxLayout, QGridLayout,
    QMainWindow, QWidget
)

class CustomGUI(QMainWindow):
    def __init__(self, callback):
        super().__init__()
        self.callback = callback
        self.setWindowTitle({design['window_title']!r})
        self.resize(1020, 720)
        self.setStyleSheet({build_stylesheet(design)!r})

        root = QWidget()
        self.setCentralWidget(root)
        shell = QVBoxLayout(root)
        shell.setContentsMargins({design['margin']}, {design['margin']}, {design['margin']}, {design['margin']})
        shell.setSpacing({design['spacing']})

        content = QWidget()
        shell.addWidget(content)
        layout = {'QHBoxLayout(content)' if design['layout_type'] == 'Horizontal' else 'QGridLayout(content)' if design['layout_type'] == 'Grid' else 'QVBoxLayout(content)'}
        layout.setContentsMargins({design['margin']}, {design['margin']}, {design['margin']}, {design['margin']})
        layout.setSpacing({design['spacing']})

        {chr(10).join('        ' + l for l in create_lines)}
        {chr(10).join('        ' + l for l in add_lines)}
        {chr(10).join('        ' + l for l in connect_lines) if connect_lines else '        # No button callbacks configured'}

        watermark = QLabel({WATERMARK_TEXT!r})
        watermark.setAlignment(Qt.AlignmentFlag.AlignRight)
        shell.addWidget(watermark)

    def run_original(self):
        if callable(self.callback):
            self.callback()


def original_main():
    namespace = {{"__name__": "__embedded_script__"}}
    exec(ORIGINAL_SCRIPT, namespace, namespace)
    for entry in ("main", "run"):
        fn = namespace.get(entry)
        if callable(fn):
            return fn()
    return None


def main():
    app = QApplication(sys.argv)
    window = CustomGUI(original_main)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
'''


def main():
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
