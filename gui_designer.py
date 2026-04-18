 (cd "$(git rev-parse --show-toplevel)" && git apply --3way <<'EOF' 
diff --git a/gui_designer.py b/gui_designer.py
new file mode 100644
index 0000000000000000000000000000000000000000..bd0086cd11e4a46f31455a8e62e49057b81e6543
--- /dev/null
+++ b/gui_designer.py
@@ -0,0 +1,766 @@
+#!/usr/bin/env python3
+"""
+GUI Designer for Python Scripts
+- Drop any Python file
+- Design a custom GUI menu (PyQt6) with many combinations
+- Generate merged script with your logic + the designed GUI
+"""
+
+from __future__ import annotations
+
+import os
+import sys
+import textwrap
+
+from PyQt6.QtCore import Qt
+from PyQt6.QtGui import QDragEnterEvent, QDropEvent, QFont
+from PyQt6.QtWidgets import (
+    QApplication,
+    QCheckBox,
+    QColorDialog,
+    QComboBox,
+    QDialog,
+    QFileDialog,
+    QFontDialog,
+    QFormLayout,
+    QFrame,
+    QGridLayout,
+    QGroupBox,
+    QHBoxLayout,
+    QLabel,
+    QLineEdit,
+    QListWidget,
+    QListWidgetItem,
+    QMainWindow,
+    QMessageBox,
+    QPushButton,
+    QSlider,
+    QSpinBox,
+    QSplitter,
+    QTabWidget,
+    QTableWidget,
+    QTextEdit,
+    QVBoxLayout,
+    QWidget,
+)
+
+
+STYLE_PRESETS = {
+    "Default": "",
+    "Flat": """
+        QPushButton { border: none; background-color: #dcdcdc; padding: 6px; }
+        QPushButton:hover { background-color: #c5c5c5; }
+    """,
+    "Modern": """
+        QPushButton { background-color: #3498db; color: white; border-radius: 6px; padding: 8px; }
+        QPushButton:hover { background-color: #2980b9; }
+    """,
+    "Rounded": """
+        QPushButton { border: 2px solid #909090; border-radius: 14px; padding: 6px; }
+        QPushButton:hover { background-color: #efefef; }
+    """,
+    "Neon": """
+        QPushButton {
+            color: #00ff9f;
+            border: 1px solid #00ff9f;
+            border-radius: 8px;
+            background-color: #101820;
+            padding: 8px;
+        }
+        QPushButton:hover { background-color: #152a2b; }
+    """,
+}
+
+
+class PreviewDialog(QDialog):
+    """Lightweight, real-time preview window built from current design data."""
+
+    def __init__(self, design: dict, parent=None):
+        super().__init__(parent)
+        self.setWindowTitle(f"Preview - {design['window_title']}")
+        self.resize(640, 420)
+
+        self.setStyleSheet(self._build_stylesheet(design))
+
+        root = QWidget()
+        root_layout = QVBoxLayout(root)
+        root_layout.setContentsMargins(design["margin"], design["margin"], design["margin"], design["margin"])
+        root_layout.setSpacing(design["spacing"])
+
+        if design["show_header"]:
+            header = QLabel(design["header_text"] or "Preview Header")
+            header.setObjectName("header")
+            header.setAlignment(Qt.AlignmentFlag.AlignCenter)
+            root_layout.addWidget(header)
+
+        layout_widget = self._build_widget_area(design)
+        root_layout.addWidget(layout_widget)
+
+        wrapper = QVBoxLayout()
+        wrapper.addWidget(root)
+        self.setLayout(wrapper)
+
+    def _build_widget_area(self, design: dict) -> QWidget:
+        layout_type = design["layout_type"]
+        widgets = design["widgets"]
+
+        container = QWidget()
+        if layout_type == "Vertical":
+            layout = QVBoxLayout(container)
+            for descriptor in widgets:
+                layout.addWidget(self._make_widget(descriptor))
+        elif layout_type == "Horizontal":
+            layout = QHBoxLayout(container)
+            for descriptor in widgets:
+                layout.addWidget(self._make_widget(descriptor))
+        elif layout_type == "Grid":
+            layout = QGridLayout(container)
+            columns = max(1, design["grid_columns"])
+            for i, descriptor in enumerate(widgets):
+                row, col = divmod(i, columns)
+                layout.addWidget(self._make_widget(descriptor), row, col)
+        else:  # Tabbed
+            tab_widget = QTabWidget()
+            positions = {
+                "North": QTabWidget.TabPosition.North,
+                "South": QTabWidget.TabPosition.South,
+                "West": QTabWidget.TabPosition.West,
+                "East": QTabWidget.TabPosition.East,
+            }
+            tab_widget.setTabPosition(positions.get(design["tab_position"], QTabWidget.TabPosition.North))
+            for idx, descriptor in enumerate(widgets, 1):
+                tab = QWidget()
+                v = QVBoxLayout(tab)
+                v.addWidget(self._make_widget(descriptor))
+                tab_widget.addTab(tab, f"Widget {idx}")
+            layout = QVBoxLayout(container)
+            layout.addWidget(tab_widget)
+
+        layout.setContentsMargins(design["margin"], design["margin"], design["margin"], design["margin"])
+        layout.setSpacing(design["spacing"])
+        return container
+
+    @staticmethod
+    def _make_widget(descriptor: dict) -> QWidget:
+        wtype = descriptor["type"]
+        label = descriptor.get("label", wtype)
+
+        if wtype == "Label":
+            return QLabel(label)
+        if wtype == "Button":
+            return QPushButton(label)
+        if wtype == "Line Edit":
+            line = QLineEdit()
+            line.setPlaceholderText(label)
+            return line
+        if wtype == "Text Edit":
+            text = QTextEdit()
+            text.setPlaceholderText(label)
+            text.setFixedHeight(80)
+            return text
+        if wtype == "Check Box":
+            return QCheckBox(label)
+        if wtype == "Combo Box":
+            combo = QComboBox()
+            combo.addItems(["Option A", "Option B", "Option C"])
+            return combo
+        if wtype == "Slider":
+            slider = QSlider(Qt.Orientation.Horizontal)
+            slider.setRange(0, 100)
+            slider.setValue(30)
+            return slider
+        if wtype == "Spin Box":
+            spin = QSpinBox()
+            spin.setRange(0, 999)
+            return spin
+        if wtype == "Group Box":
+            group = QGroupBox(label)
+            v = QVBoxLayout(group)
+            v.addWidget(QLabel("Group content"))
+            return group
+        if wtype == "Table":
+            table = QTableWidget(3, 3)
+            table.setMinimumHeight(120)
+            return table
+        return QLabel(f"Unsupported widget: {wtype}")
+
+    @staticmethod
+    def _build_stylesheet(design: dict) -> str:
+        theme = design["theme"]
+        bg = design["bg_color"]
+        accent = design["accent_color"]
+        header_css = "#header { font-size: 18px; font-weight: bold; padding: 8px; }"
+
+        theme_css = {
+            "Light": f"QWidget {{ background-color: {bg}; color: #1f2937; }}",
+            "Dark": f"QWidget {{ background-color: {bg}; color: #ecf0f1; }}",
+            "Gradient": (
+                "QWidget {"
+                f"background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 {bg}, stop:1 {accent});"
+                "color: #f8f9fa; }"
+            ),
+            "Contrast": f"QWidget {{ background-color: {bg}; color: {accent}; }}",
+        }
+
+        base = theme_css.get(theme, theme_css["Light"])
+        anim = "QPushButton { transition: all 0.2s ease; }" if design["enable_animation"] else ""
+        return "\n".join([base, STYLE_PRESETS.get(design["button_style"], ""), header_css, anim])
+
+
+class DropArea(QLabel):
+    """Central widget that accepts dropped .py files."""
+
+    def __init__(self, main_window: "MainWindow"):
+        super().__init__("Drop your Python file here\n(.py)")
+        self.main_window = main_window
+        self.setAcceptDrops(True)
+        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
+        self.setStyleSheet("border: 3px dashed #8a8a8a; border-radius: 12px; padding: 40px;")
+        self.setMinimumHeight(220)
+
+    def dragEnterEvent(self, event: QDragEnterEvent):
+        if event.mimeData().hasUrls():
+            event.acceptProposedAction()
+        else:
+            super().dragEnterEvent(event)
+
+    def dropEvent(self, event: QDropEvent):
+        for url in event.mimeData().urls():
+            file_path = url.toLocalFile()
+            if file_path.endswith(".py"):
+                self.setText(f"Loaded: {os.path.basename(file_path)}")
+                self.main_window.load_script(file_path)
+                break
+        event.acceptProposedAction()
+
+
+class PropertyEditor(QWidget):
+    """Side panel with tabs for style, layout, widgets, preview, and code generation."""
+
+    AVAILABLE_WIDGETS = [
+        "Label",
+        "Button",
+        "Line Edit",
+        "Text Edit",
+        "Check Box",
+        "Combo Box",
+        "Slider",
+        "Spin Box",
+        "Group Box",
+        "Table",
+    ]
+
+    def __init__(self, main_window: "MainWindow"):
+        super().__init__(main_window)
+        self.main_window = main_window
+        self.added_widgets: list[dict] = []
+
+        self.tabs = QTabWidget()
+        self._create_style_tab()
+        self._create_layout_tab()
+        self._create_widgets_tab()
+        self._create_preview_tab()
+        self._create_code_tab()
+
+        root = QVBoxLayout(self)
+        root.addWidget(self.tabs)
+
+        self._connect_live_updates()
+
+    def _create_style_tab(self):
+        tab = QWidget()
+        form = QFormLayout(tab)
+
+        self.window_title_edit = QLineEdit("My Custom GUI")
+        self.header_toggle = QCheckBox("Show header banner")
+        self.header_toggle.setChecked(True)
+        self.header_text_edit = QLineEdit("Welcome to your generated interface")
+
+        self.bg_color_btn = QPushButton("Choose Background Color")
+        self.bg_color_btn.clicked.connect(self._choose_bg_color)
+        self.bg_color_label = QLabel("#ffffff")
+
+        self.accent_color_btn = QPushButton("Choose Accent Color")
+        self.accent_color_btn.clicked.connect(self._choose_accent_color)
+        self.accent_color_label = QLabel("#3498db")
+
+        self.font_btn = QPushButton("Choose Font")
+        self.font_btn.clicked.connect(self._choose_font)
+        self.font_label = QLabel("Default 10pt")
+
+        self.theme_combo = QComboBox()
+        self.theme_combo.addItems(["Light", "Dark", "Gradient", "Contrast"])
+
+        self.button_style_combo = QComboBox()
+        self.button_style_combo.addItems(list(STYLE_PRESETS.keys()))
+
+        self.animation_toggle = QCheckBox("Enable button hover transitions")
+
+        form.addRow("Window Title:", self.window_title_edit)
+        form.addRow("Header:", self.header_toggle)
+        form.addRow("Header Text:", self.header_text_edit)
+        form.addRow("Background:", self.bg_color_btn)
+        form.addRow("", self.bg_color_label)
+        form.addRow("Accent:", self.accent_color_btn)
+        form.addRow("", self.accent_color_label)
+        form.addRow("Global Font:", self.font_btn)
+        form.addRow("", self.font_label)
+        form.addRow("Theme:", self.theme_combo)
+        form.addRow("Button Style:", self.button_style_combo)
+        form.addRow("Animations:", self.animation_toggle)
+
+        self.tabs.addTab(tab, "Style")
+
+    def _create_layout_tab(self):
+        tab = QWidget()
+        form = QFormLayout(tab)
+
+        self.layout_combo = QComboBox()
+        self.layout_combo.addItems(["Vertical", "Horizontal", "Grid", "Tabbed"])
+
+        self.tab_position_combo = QComboBox()
+        self.tab_position_combo.addItems(["North", "South", "West", "East"])
+        self.tab_position_combo.setEnabled(False)
+
+        self.margin_spin = QSpinBox()
+        self.margin_spin.setRange(0, 60)
+        self.margin_spin.setValue(10)
+
+        self.spacing_spin = QSpinBox()
+        self.spacing_spin.setRange(0, 40)
+        self.spacing_spin.setValue(8)
+
+        self.grid_columns_spin = QSpinBox()
+        self.grid_columns_spin.setRange(1, 8)
+        self.grid_columns_spin.setValue(2)
+        self.grid_columns_spin.setEnabled(False)
+
+        self.layout_combo.currentTextChanged.connect(self._sync_layout_controls)
+
+        form.addRow("Main Layout:", self.layout_combo)
+        form.addRow("Tab Position:", self.tab_position_combo)
+        form.addRow("Grid Columns:", self.grid_columns_spin)
+        form.addRow("Margin (px):", self.margin_spin)
+        form.addRow("Spacing (px):", self.spacing_spin)
+
+        self.tabs.addTab(tab, "Layout")
+
+    def _create_widgets_tab(self):
+        tab = QWidget()
+        layout = QVBoxLayout(tab)
+
+        self.widget_list = QListWidget()
+        self.widget_list.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
+        for name in self.AVAILABLE_WIDGETS:
+            self.widget_list.addItem(name)
+        self.widget_list.itemDoubleClicked.connect(self._add_widget)
+
+        self.custom_widget_name = QLineEdit()
+        self.custom_widget_name.setPlaceholderText("Custom label for next widget (optional)")
+
+        buttons_row = QHBoxLayout()
+        self.remove_widget_btn = QPushButton("Remove Selected")
+        self.clear_widgets_btn = QPushButton("Clear All")
+        buttons_row.addWidget(self.remove_widget_btn)
+        buttons_row.addWidget(self.clear_widgets_btn)
+
+        self.added_widgets_list = QListWidget()
+
+        self.remove_widget_btn.clicked.connect(self._remove_widget)
+        self.clear_widgets_btn.clicked.connect(self._clear_widgets)
+
+        layout.addWidget(QLabel("Double-click to add widget:"))
+        layout.addWidget(self.widget_list)
+        layout.addWidget(self.custom_widget_name)
+        layout.addLayout(buttons_row)
+        layout.addWidget(QLabel("Widgets included in generated GUI:"))
+        layout.addWidget(self.added_widgets_list)
+
+        self.tabs.addTab(tab, "Widgets")
+
+    def _create_preview_tab(self):
+        tab = QWidget()
+        layout = QVBoxLayout(tab)
+
+        self.preview_summary = QTextEdit()
+        self.preview_summary.setReadOnly(True)
+
+        self.open_preview_btn = QPushButton("Open Live Preview Window")
+        self.open_preview_btn.clicked.connect(self.main_window.open_live_preview)
+
+        layout.addWidget(QLabel("Live configuration summary"))
+        layout.addWidget(self.preview_summary)
+        layout.addWidget(self.open_preview_btn)
+
+        self.tabs.addTab(tab, "Preview")
+
+    def _create_code_tab(self):
+        tab = QWidget()
+        layout = QVBoxLayout(tab)
+
+        self.code_preview = QTextEdit()
+        self.code_preview.setReadOnly(True)
+        self.code_preview.setFont(QFont("Monospace", 10))
+
+        btn_row = QHBoxLayout()
+        self.refresh_code_btn = QPushButton("Refresh Code Preview")
+        self.save_btn = QPushButton("Save Generated Script")
+        btn_row.addWidget(self.refresh_code_btn)
+        btn_row.addWidget(self.save_btn)
+
+        self.refresh_code_btn.clicked.connect(self.main_window.refresh_code_preview)
+        self.save_btn.clicked.connect(self._save_generated_script)
+
+        layout.addWidget(QLabel("Generated code (preview):"))
+        layout.addWidget(self.code_preview)
+        layout.addLayout(btn_row)
+
+        self.tabs.addTab(tab, "Code")
+
+    def _connect_live_updates(self):
+        controls = [
+            self.window_title_edit,
+            self.header_toggle,
+            self.header_text_edit,
+            self.theme_combo,
+            self.button_style_combo,
+            self.animation_toggle,
+            self.layout_combo,
+            self.tab_position_combo,
+            self.margin_spin,
+            self.spacing_spin,
+            self.grid_columns_spin,
+        ]
+        for control in controls:
+            signal = getattr(control, "textChanged", None) or getattr(control, "stateChanged", None) or getattr(control, "currentTextChanged", None) or getattr(control, "valueChanged", None)
+            if signal:
+                signal.connect(self.main_window.update_preview)
+
+    def _sync_layout_controls(self, current_text: str):
+        self.tab_position_combo.setEnabled(current_text == "Tabbed")
+        self.grid_columns_spin.setEnabled(current_text == "Grid")
+        self.main_window.update_preview()
+
+    def _add_widget(self, item: QListWidgetItem):
+        wtype = item.text()
+        index = len(self.added_widgets) + 1
+        label = (self.custom_widget_name.text() or f"{wtype} {index}").strip()
+        name = f"{wtype.lower().replace(' ', '_')}_{index}"
+
+        descriptor = {"type": wtype, "name": name, "label": label}
+        self.added_widgets.append(descriptor)
+        self.added_widgets_list.addItem(f"{wtype} • {label} • {name}")
+        self.custom_widget_name.clear()
+        self.main_window.update_preview()
+
+    def _remove_widget(self):
+        row = self.added_widgets_list.currentRow()
+        if row < 0:
+            return
+        self.added_widgets.pop(row)
+        self.added_widgets_list.takeItem(row)
+        self.main_window.update_preview()
+
+    def _clear_widgets(self):
+        self.added_widgets.clear()
+        self.added_widgets_list.clear()
+        self.main_window.update_preview()
+
+    def _save_generated_script(self):
+        if not self.main_window.original_script_path:
+            QMessageBox.warning(self, "No Script", "Please drop a Python file first.")
+            return
+
+        file_path, _ = QFileDialog.getSaveFileName(self, "Save Merged Script", "", "Python Files (*.py)")
+        if file_path:
+            self.main_window.generate_merged_script(file_path)
+
+    def _choose_bg_color(self):
+        color = QColorDialog.getColor()
+        if color.isValid():
+            self.bg_color_label.setText(color.name())
+            self.bg_color_label.setStyleSheet(f"background-color: {color.name()}; padding: 4px; border: 1px solid #ccc;")
+            self.main_window.update_preview()
+
+    def _choose_accent_color(self):
+        color = QColorDialog.getColor()
+        if color.isValid():
+            self.accent_color_label.setText(color.name())
+            self.accent_color_label.setStyleSheet(f"background-color: {color.name()}; padding: 4px; border: 1px solid #ccc;")
+            self.main_window.update_preview()
+
+    def _choose_font(self):
+        font, ok = QFontDialog.getFont()
+        if ok:
+            self.font_label.setText(f"{font.family()} {font.pointSize()}pt")
+            self.font_label.setFont(font)
+            self.main_window.update_preview()
+
+    def get_design_data(self) -> dict:
+        return {
+            "window_title": self.window_title_edit.text().strip() or "Custom GUI",
+            "show_header": self.header_toggle.isChecked(),
+            "header_text": self.header_text_edit.text().strip(),
+            "bg_color": self.bg_color_label.text(),
+            "accent_color": self.accent_color_label.text(),
+            "font": self.font_label.text(),
+            "theme": self.theme_combo.currentText(),
+            "button_style": self.button_style_combo.currentText(),
+            "enable_animation": self.animation_toggle.isChecked(),
+            "layout_type": self.layout_combo.currentText(),
+            "tab_position": self.tab_position_combo.currentText(),
+            "margin": self.margin_spin.value(),
+            "spacing": self.spacing_spin.value(),
+            "grid_columns": self.grid_columns_spin.value(),
+            "widgets": [w.copy() for w in self.added_widgets],
+        }
+
+
+class MainWindow(QMainWindow):
+    def __init__(self):
+        super().__init__()
+        self.setWindowTitle("GUI Designer - Drop your Python script")
+        self.resize(1320, 860)
+
+        self.original_script_path: str | None = None
+        self.original_code = ""
+        self.preview_dialog: PreviewDialog | None = None
+
+        splitter = QSplitter(Qt.Orientation.Horizontal)
+
+        left_widget = QWidget()
+        left_layout = QVBoxLayout(left_widget)
+
+        self.drop_area = DropArea(self)
+        self.preview_label = QLabel("Configure the right-side tabs to preview generated GUI details.")
+        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
+        self.preview_label.setFrameStyle(QFrame.Shape.Box)
+        self.preview_label.setMinimumHeight(320)
+
+        self.preview_hint = QLabel("Tip: use the Preview tab's button to open a live preview window.")
+        self.preview_hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
+
+        left_layout.addWidget(self.drop_area)
+        left_layout.addWidget(self.preview_label)
+        left_layout.addWidget(self.preview_hint)
+
+        self.property_editor = PropertyEditor(self)
+
+        splitter.addWidget(left_widget)
+        splitter.addWidget(self.property_editor)
+        splitter.setSizes([730, 590])
+
+        self.setCentralWidget(splitter)
+        self.update_preview()
+
+    def load_script(self, path: str):
+        self.original_script_path = path
+        with open(path, "r", encoding="utf-8") as file:
+            self.original_code = file.read()
+        self.update_preview()
+
+    def open_live_preview(self):
+        design = self.property_editor.get_design_data()
+        self.preview_dialog = PreviewDialog(design, self)
+        self.preview_dialog.show()
+
+    def refresh_code_preview(self):
+        design = self.property_editor.get_design_data()
+        merged_head = self.generate_gui_code(design, self.original_code)
+        snippet = merged_head if len(merged_head) < 12000 else merged_head[:12000] + "\n\n# ... truncated"
+        self.property_editor.code_preview.setPlainText(snippet)
+
+    def generate_merged_script(self, output_path: str):
+        if not self.original_script_path:
+            return
+
+        design = self.property_editor.get_design_data()
+        payload = self.generate_gui_code(design, self.original_code)
+
+        with open(output_path, "w", encoding="utf-8") as file:
+            file.write(payload)
+
+        QMessageBox.information(self, "Success", f"Merged script saved to:\n{output_path}")
+        self.refresh_code_preview()
+
+    @staticmethod
+    def _format_widget_creation(widget: dict) -> str:
+        wtype = widget["type"]
+        name = widget["name"]
+        label = widget["label"].replace("\"", "\\\"")
+
+        mapping = {
+            "Label": f"self.{name} = QLabel(\"{label}\")",
+            "Button": f"self.{name} = QPushButton(\"{label}\")",
+            "Line Edit": f"self.{name} = QLineEdit(); self.{name}.setPlaceholderText(\"{label}\")",
+            "Text Edit": f"self.{name} = QTextEdit(); self.{name}.setPlaceholderText(\"{label}\")",
+            "Check Box": f"self.{name} = QCheckBox(\"{label}\")",
+            "Combo Box": f"self.{name} = QComboBox(); self.{name}.addItems(['Option A', 'Option B', 'Option C'])",
+            "Slider": f"self.{name} = QSlider(Qt.Orientation.Horizontal); self.{name}.setRange(0, 100)",
+            "Spin Box": f"self.{name} = QSpinBox(); self.{name}.setRange(0, 999)",
+            "Group Box": (
+                f"self.{name} = QGroupBox(\"{label}\"); _{name}_layout = QVBoxLayout(self.{name}); "
+                f"_{name}_layout.addWidget(QLabel('Group content'))"
+            ),
+            "Table": f"self.{name} = QTableWidget(3, 3)",
+        }
+        return mapping.get(wtype, f"self.{name} = QLabel('Unsupported: {wtype}')")
+
+    def generate_gui_code(self, design: dict, original_code: str = "") -> str:
+        widgets = design["widgets"] or [{"type": "Label", "name": "label_1", "label": "No widgets selected yet"}]
+        creation_lines = [self._format_widget_creation(widget) for widget in widgets]
+
+        add_lines: list[str] = []
+        if design["layout_type"] == "Grid":
+            cols = max(1, design["grid_columns"])
+            for i, widget in enumerate(widgets):
+                row, col = divmod(i, cols)
+                add_lines.append(f"layout.addWidget(self.{widget['name']}, {row}, {col})")
+        elif design["layout_type"] == "Tabbed":
+            add_lines.extend(
+                [
+                    "tabs = QTabWidget()",
+                    "tabs.setTabPosition(QTabWidget.TabPosition.%s)" % design["tab_position"],
+                ]
+            )
+            for i, widget in enumerate(widgets, 1):
+                add_lines.extend(
+                    [
+                        f"tab_{i} = QWidget()",
+                        f"tab_{i}_layout = QVBoxLayout(tab_{i})",
+                        f"tab_{i}_layout.addWidget(self.{widget['name']})",
+                        f"tabs.addTab(tab_{i}, '{widget['type']} {i}')",
+                    ]
+                )
+            add_lines.append("shell_layout.addWidget(tabs)")
+        else:
+            for widget in widgets:
+                add_lines.append(f"layout.addWidget(self.{widget['name']})")
+
+        layout_ctor = {
+            "Vertical": "QVBoxLayout(content)",
+            "Horizontal": "QHBoxLayout(content)",
+            "Grid": "QGridLayout(content)",
+            "Tabbed": "QVBoxLayout(content)",
+        }.get(design["layout_type"], "QVBoxLayout(content)")
+
+        style_text = PreviewDialog._build_stylesheet(design).strip()
+        font = design["font"]
+        window_title = design["window_title"]
+        original_source_literal = repr(original_code)
+
+        header_line = ""
+        if design["show_header"]:
+            header_text = design["header_text"].replace('\"', '\\\"') or "Welcome"
+            header_line = (
+                f'header = QLabel("{header_text}"); '
+                'header.setObjectName("header"); shell_layout.addWidget(header)'
+            )
+
+        connect_lines = [
+            f"self.{widget['name']}.clicked.connect(self.run_original)" for widget in widgets if widget["type"] == "Button"
+        ]
+
+        code = f"""
+import sys
+from PyQt6.QtCore import Qt
+from PyQt6.QtGui import QFont
+from PyQt6.QtWidgets import (
+    QApplication, QCheckBox, QComboBox, QGridLayout, QGroupBox, QHBoxLayout,
+    QLabel, QLineEdit, QMainWindow, QPushButton, QSlider, QSpinBox,
+    QTabWidget, QTableWidget, QTextEdit, QVBoxLayout, QWidget
+)
+
+
+class CustomGUI(QMainWindow):
+    def __init__(self, original_script_func):
+        super().__init__()
+        self.original_script_func = original_script_func
+        self.setWindowTitle({window_title!r})
+        self.resize(1000, 700)
+
+        self.setStyleSheet({style_text!r})
+
+        font_parts = "{font}".split()
+        if len(font_parts) >= 2 and font_parts[-1].endswith("pt"):
+            QApplication.setFont(QFont(font_parts[0], int(font_parts[-1].replace('pt', ''))))
+
+        container = QWidget()
+        self.setCentralWidget(container)
+
+        shell_layout = QVBoxLayout(container)
+        shell_layout.setContentsMargins({design['margin']}, {design['margin']}, {design['margin']}, {design['margin']})
+        shell_layout.setSpacing({design['spacing']})
+
+        {header_line}
+
+        content = QWidget()
+        shell_layout.addWidget(content)
+        layout = {layout_ctor}
+        layout.setContentsMargins({design['margin']}, {design['margin']}, {design['margin']}, {design['margin']})
+        layout.setSpacing({design['spacing']})
+
+        {textwrap.indent(chr(10).join(creation_lines), '        ')}
+
+        {textwrap.indent(chr(10).join(add_lines), '        ')}
+
+        {textwrap.indent(chr(10).join(connect_lines) if connect_lines else '# No button callbacks configured.', '        ')}
+
+    def run_original(self):
+        if callable(self.original_script_func):
+            self.original_script_func()
+
+
+def original_main():
+    namespace = {{"__name__": "__embedded_script__"}}
+    exec(ORIGINAL_SCRIPT, namespace, namespace)
+    for candidate_name in ("main", "run"):
+        candidate = namespace.get(candidate_name)
+        if callable(candidate):
+            return candidate()
+    return None
+
+
+def main():
+    app = QApplication(sys.argv)
+    window = CustomGUI(original_main)
+    window.show()
+    sys.exit(app.exec())
+
+
+if __name__ == "__main__":
+    main()
+""".strip()
+        return f"ORIGINAL_SCRIPT = {original_source_literal}\n\n" + code + "\n"
+
+    def update_preview(self):
+        design = self.property_editor.get_design_data()
+        summary = (
+            f"Preview summary\n"
+            f"----------------\n"
+            f"Window: {design['window_title']}\n"
+            f"Theme: {design['theme']}\n"
+            f"Background: {design['bg_color']}\n"
+            f"Accent: {design['accent_color']}\n"
+            f"Button style: {design['button_style']}\n"
+            f"Layout: {design['layout_type']}\n"
+            f"Tab position: {design['tab_position']}\n"
+            f"Grid columns: {design['grid_columns']}\n"
+            f"Margin/Spacing: {design['margin']} / {design['spacing']}\n"
+            f"Widgets: {len(design['widgets'])}\n"
+            f"Header enabled: {'yes' if design['show_header'] else 'no'}"
+        )
+        self.preview_label.setText(summary)
+        self.property_editor.preview_summary.setPlainText(summary)
+        self.refresh_code_preview()
+
+
+def main():
+    app = QApplication(sys.argv)
+    window = MainWindow()
+    window.show()
+    sys.exit(app.exec())
+
+
+if __name__ == "__main__":
+    main()
 
EOF
)
