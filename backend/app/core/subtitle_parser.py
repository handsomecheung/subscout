#!/usr/bin/env python3
"""Subtitle parsing utilities extracted from original main.py."""

from pathlib import Path
import ass


def parse_subtitle(subtitle_path: Path, style: str = None) -> tuple[list[str], list[str]]:
    """
    Parse subtitle file and extract valid lines.

    Args:
        subtitle_path: Path to subtitle file (.srt or .ass)
        style: Style name for .ass files (required for .ass)

    Returns:
        Tuple of (valid_lines, available_styles)
        - valid_lines: List of subtitle text lines
        - available_styles: List of available styles (only for .ass files)

    Raises:
        ValueError: If file format is not supported or style is invalid
    """
    name = subtitle_path.name.lower()

    if name.endswith(".ass"):
        return parse_ass(subtitle_path, style)
    elif name.endswith(".srt"):
        lines = parse_srt(subtitle_path)
        return lines, []
    else:
        raise ValueError(f"Unsupported subtitle format: {subtitle_path.suffix}")


def parse_ass(subtitle_path: Path, style: str = None) -> tuple[list[str], list[str]]:
    """
    Parse ASS/SSA subtitle file.

    Args:
        subtitle_path: Path to .ass file
        style: Style name to extract (optional, returns all styles if None)

    Returns:
        Tuple of (valid_lines, available_styles)
    """
    with open(subtitle_path, encoding="utf_8_sig") as f:
        doc = ass.parse(f)

    styles = [s.name for s in doc.styles]

    if style is None:
        return [], styles

    if style not in styles:
        raise ValueError(f"Style '{style}' not found. Available styles: {styles}")

    valid_lines = [e.text for e in doc.events if e.style == style]

    return valid_lines, styles


def parse_srt(subtitle_path: Path) -> list[str]:
    """
    Parse SRT subtitle file.

    Args:
        subtitle_path: Path to .srt file

    Returns:
        List of subtitle text lines
    """
    with open(subtitle_path, "r", encoding="utf-8") as f:
        return f.readlines()


def extract_styles(subtitle_path: Path) -> list[str]:
    """
    Extract available styles from .ass file.

    Args:
        subtitle_path: Path to .ass file

    Returns:
        List of available style names
    """
    if not subtitle_path.name.lower().endswith(".ass"):
        return []

    try:
        with open(subtitle_path, encoding="utf_8_sig") as f:
            doc = ass.parse(f)
        return [s.name for s in doc.styles]
    except Exception:
        return []
