#!/usr/bin/env python3
"""Interactive starter for installing and running GUI Designer."""

from __future__ import annotations

import platform
import subprocess
import sys


def ask(prompt: str, options: list[str]) -> str:
    while True:
        print(f"\n{prompt}")
        for i, item in enumerate(options, 1):
            print(f"  {i}) {item}")
        value = input("Select number: ").strip()
        if value.isdigit() and 1 <= int(value) <= len(options):
            return options[int(value) - 1]
        print("Invalid selection, try again.")


def maybe_run(cmd: list[str]):
    print("\nCommand:", " ".join(cmd))
    if input("Run this now? [y/N]: ").strip().lower() == "y":
        subprocess.run(cmd, check=False)


def main() -> int:
    print("GUI Designer setup wizard")
    print("Detected OS:", platform.system())

    os_choice = ask("Which OS are you on?", ["Windows", "Linux", "macOS"])

    if os_choice == "Linux":
        distro = ask("Which Linux family?", ["Ubuntu/Debian", "Fedora/RHEL", "Arch", "Other"])
        print("Selected Linux family:", distro)
    elif os_choice == "macOS":
        print("Tip: Homebrew Python is recommended.")

    install_mode = ask(
        "How do you want to run GUI Designer?",
        [
            "Python directly",
            "Docker",
            "PyInstaller executable",
            "Package format help (RPM/AppImage notes)",
        ],
    )

    print("\nInstalling base dependencies from requirements.txt...")
    maybe_run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])

    if install_mode == "Docker":
        print("Docker path selected.")
        print("Run: docker build -t gui-designer .")
    elif install_mode == "PyInstaller executable":
        maybe_run([sys.executable, "-m", "pip", "install", "pyinstaller"])
        maybe_run(["pyinstaller", "--onefile", "--windowed", "gui_designer.py"])
    elif install_mode == "Package format help (RPM/AppImage notes)":
        print("RPM: build onefile binary first, then package via fpm/rpmbuild.")
        print("AppImage: use linuxdeploy tooling around packaged binary.")

    launch_mode = ask(
        "Choose launch command format",
        ["python gui_designer.py", "./dist/gui_designer (if built)", "docker run ..."],
    )

    print("\nNext step:", launch_mode)
    if launch_mode.startswith("python"):
        maybe_run([sys.executable, "gui_designer.py"])

    print("\nDone. If anything fails, run: python -m py_compile gui_designer.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
