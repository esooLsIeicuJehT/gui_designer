# GUI Designer for Python Scripts (PyQt6)

A drag-and-drop GUI builder that lets you load any Python script, design a custom PyQt6 interface, and generate a merged output script.

This project focuses on **high customization** and **extensible combinations**:
- multiple layout modes (Vertical, Horizontal, Grid, Tabbed),
- rich style controls (themes, colors, button presets, optional hover transitions),
- expandable widget palette,
- live preview dialog,
- generated code preview + save flow.

---

## Features

### Script ingestion
- Drag and drop any `.py` file into the drop zone.
- The dropped file becomes the “original script” payload and is appended to the generated script.

### Design controls
- **Style tab**:
  - Window title
  - Header banner toggle + custom header text
  - Background and accent color pickers
  - Global font picker
  - Theme mode (`Light`, `Dark`, `Gradient`, `Contrast`)
  - Button style presets (`Default`, `Flat`, `Modern`, `Rounded`, `Neon`)
  - Animation toggle for hover-style transitions

- **Layout tab**:
  - Main layout type (`Vertical`, `Horizontal`, `Grid`, `Tabbed`)
  - Tab position (`North`, `South`, `West`, `East`) for tabbed mode
  - Grid column count for grid mode
  - Margin and spacing controls

- **Widgets tab**:
  - Double-click to add widgets from a larger palette:
    - Label
    - Button
    - Line Edit
    - Text Edit
    - Check Box
    - Combo Box
    - Slider
    - Spin Box
    - Group Box
    - Table
  - Optional custom label for each new widget
  - Remove selected or clear all

### Preview + generation
- **Preview tab**:
  - text summary of current design state
  - one-click live preview window
- **Code tab**:
  - refreshable generated code preview
  - save merged script output
  - generated output embeds the dropped script as a source string and executes it in an isolated namespace (`__embedded_script__`), then attempts to call `main()` or `run()` if present

---

## Endless customization ideas (extending this project)

The script is intentionally structured so you can keep pushing it further:

1. **Add more widgets** in `PropertyEditor.AVAILABLE_WIDGETS`, `PreviewDialog._make_widget`, and `MainWindow._format_widget_creation`.
   - Suggested additions: Date picker, progress bar, list view, tree view, canvas widgets, media widgets.

2. **Add more style options** in:
   - `STYLE_PRESETS` for component-level presets,
   - `PreviewDialog._build_stylesheet` for full-theme CSS blocks.
   - Suggested additions: glassmorphism, animated gradients, custom icon packs, per-widget styles.

3. **Add advanced layout patterns** in `PreviewDialog._build_widget_area` and `MainWindow.generate_gui_code`.
   - Suggested additions: nested split layouts, dock-style panels, flow layouts, responsive breakpoints.

4. **Improve real-time preview behavior**:
   - Keep one preview window open and hot-reload it on each change.
   - Persist control state between refreshes.
   - Add an embedded preview canvas mode.

5. **Enhance Python-script integration**:
   - Parse and auto-detect candidate entry points (`main`, class methods, CLI wrappers).
   - Generate execution adapters for scripts with arguments.
   - Add sandboxed execution mode with stdout/stderr logging panel.

---

## Project structure

```text
.
├── gui_designer.py
└── README.md
```

---

## How to Run

Install dependencies (PyQt6):

```bash
pip install PyQt6
```

Save the script as `gui_designer.py`.

Run it:

```bash
python gui_designer.py
```

Drop any `.py` file into the central area.
Then use the side tabs to customize the GUI (colors, fonts, layout, widgets).
Finally, go to the Code tab and click **Save Generated Script** – it will produce a new Python file that merges your original logic with the designed GUI.

---

## Building an Installable Package

### Docker Image

Create a Dockerfile:

```dockerfile
FROM python:3.10-slim
RUN pip install PyQt6
COPY gui_designer.py /app/
WORKDIR /app
CMD ["python", "gui_designer.py"]
```

Build and run:

```bash
docker build -t gui-designer .
docker run -e DISPLAY=$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix gui-designer
```

(You may need to allow X11 forwarding.)

### RPM Package

Use pyinstaller to create a standalone executable, then package it.

```bash
pip install pyinstaller
pyinstaller --onefile --windowed gui_designer.py
```

Then use `fpm` or `rpmbuild` to create an RPM.

---

## Suggested next upgrades

- Add JSON/YAML template import/export for design presets.
- Add undo/redo history for layout edits.
- Add component property editor per widget (name, placeholder, min/max, validation).
- Support Qt Designer `.ui` export mode.
- Add testing harness for generated script smoke checks.

---

## Troubleshooting

- **PyQt6 install fails**: upgrade pip first (`python -m pip install --upgrade pip`) and retry.
- **No display in Docker/Linux**: ensure display forwarding and X11 permissions are configured.
- **Generated script does not run original logic**: adapt `original_main()` and callback wiring to your script’s real entry point.

---

## License

Add your preferred license (MIT, Apache-2.0, etc.) to clarify usage permissions.
