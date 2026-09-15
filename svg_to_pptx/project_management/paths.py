#!/usr/bin/env python3
"""
pptx-compiler - Project Management Paths

Own the package resource roots used by project-management modules.

Usage:
    Import the required path constants from project_management.paths.

Examples:
    from svg_to_pptx.project_management.paths import projects_root, SCHEMA_DIR

Dependencies:
    None (only uses the standard library)
"""

from pathlib import Path

PACKAGE_DIR = Path(__file__).resolve().parent
PACKAGE_ROOT = PACKAGE_DIR.parent
# "skill" scope names in page-context reports predate the package layout;
# they now refer to the package root.
SKILL_DIR = PACKAGE_ROOT


def projects_root() -> Path:
    """Default workspace for projects: ./projects under the caller's cwd.

    Evaluated per call so it follows the directory the tool is invoked from
    rather than a location inside the installed package.
    """
    return Path.cwd() / "projects"


CHARTS_DIR = PACKAGE_ROOT / "templates" / "charts"
SCHEMA_DIR = PACKAGE_ROOT / "templates" / "schemas"
SCAFFOLD_DIR = PACKAGE_ROOT / "templates" / "scaffolds"
