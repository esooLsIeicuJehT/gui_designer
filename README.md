# GUI Designer for Python Scripts (PyQt6)

A drag-and-drop desktop app to wrap existing Python scripts with a customizable GUI, preview changes live, and generate production-ready output code.

## What’s New (Major Upgrades)

This version adds the features requested in review:

- JSON/YAML template import/export for design presets.
- Undo/redo history for layout and widget edits.
- Per-widget component property editor (name, label, placeholder, min/max, required validation flag).
- Qt Designer `.ui` export support.
- Built-in smoke-test harness for generated scripts (`py_compile`).
- Starter templates (3 non-basic and fully different presets).
- Save/load full project sessions so users can resume later.
- Assistant tab with prompt box and multi-target generation mode (`PyQt6`, `Generic GUI`, `ImGui` skeleton).
- Ownership watermark + proprietary licensing metadata.

---

## Key Features

### 1) Script + Project Workflow
- Drop a `.py` file in the main panel.
- Save project sessions as `.gdp.json`.
- Load previous sessions and continue editing.

### 2) Design Presets and Templates
- Export/import **JSON** templates from File menu.
- Export/import **YAML** templates (requires `PyYAML`).
- Starter presets included:
  - **Data Dashboard**
  - **Neon Game Launcher**
  - **Glass CRM Panel**

### 3) Layout + Widget Authoring
- Layout modes: Vertical, Horizontal, Grid, Tabbed.
- Property controls for margin, spacing, grid columns, tab position.
- Widget palette with live component editor.
- Widget-level fields:
  - Name
  - Label/Text
  - Placeholder
  - Min / Max
  - Required toggle

### 4) Undo/Redo
- Built-in history snapshots for design/project mutations.
- Menu shortcuts:
  - `Ctrl+Z` Undo
  - `Ctrl+Y` Redo

### 5) Export + Validation
- Generate merged Python script.
- Export Qt Designer `.ui` file.
- Run smoke test (compilation check) on generated output.

### 6) Assistant Tab (Prompt-Based)
- Framework targets:
  - `PyQt6` (full generated output)
  - `Generic GUI` (conceptual layout)
  - `ImGui` (starter draw function skeleton)

> Note: ImGui output is a starting scaffold and expects runtime integration (e.g., pyimgui/glfw).

---

## Installation

```bash
pip install PyQt6
```

Optional for YAML templates:

```bash
pip install pyyaml
```

Run:

```bash
python gui_designer.py
```

---

## File Menu Features

- Save Project (`.gdp.json`)
- Load Project (`.gdp.json`)
- Export Template (JSON)
- Import Template (JSON)
- Export Template (YAML)
- Import Template (YAML)

## Edit Menu Features

- Undo (`Ctrl+Z`)
- Redo (`Ctrl+Y`)

---

## How generated scripts run original logic

Generated output embeds the dropped source code in `ORIGINAL_SCRIPT`, executes it in namespace `__embedded_script__`, and attempts to call `main()` then `run()` if present.

---

## Proprietary watermarking + licensing

- Main app and generated scripts include watermark text with owner contact.
- License restrictions are declared in `LICENSE`.

Copyright © 2026 Justin Lorenc  
Contact: `midnight-repo@engineer.com`

---

## Packaging snippets

### Docker

```dockerfile
FROM python:3.11-slim
RUN pip install PyQt6 pyyaml
WORKDIR /app
COPY gui_designer.py /app/
CMD ["python", "gui_designer.py"]
```

### Standalone build (example)

```bash
pip install pyinstaller
pyinstaller --onefile --windowed gui_designer.py
```

---

## Smoke testing generated output

Use the **Smoke Test Generated Script** button in the Code tab.

It writes a temporary generated file and runs:

```bash
python -m py_compile <temp_generated.py>
```

---

## Notes on “can’t be copied/sold”

Watermarks and license notices strongly improve attribution and legal position, but no client-side code can absolutely prevent copying. Pair this with legal terms, distribution tracking, and (if needed) server-side license checks.
