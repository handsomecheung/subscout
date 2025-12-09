#!/usr/bin/env python3
"""Word management utilities for handling known words."""

from pathlib import Path
from typing import Set, List

from app.core.config import settings


class KnownWordManager:
    """Manager for known words persistence."""

    def __init__(self, lang: str):
        """
        Initialize known word manager.

        Args:
            lang: Language code ('en' or 'jp')
        """
        self.lang = lang
        self.file_path = self._get_known_file()

    def _get_known_file(self) -> Path:
        """Get the path to the known words file for this language."""
        file_path = settings.HOME_DIR / f"known-words.{self.lang}.txt"
        file_path.touch(exist_ok=True)
        return file_path

    def load_words(self) -> Set[str]:
        """
        Load known words from file.

        Returns:
            Set of known words
        """
        words = set()
        with open(self.file_path, "r", encoding="utf-8") as f:
            for line in f:
                word = line.strip()
                if word:
                    words.add(word)
        return words

    def save_words(self, words: Set[str]):
        """
        Append new words to the known words file.

        Args:
            words: Set of words to add
        """
        if not words:
            return

        with open(self.file_path, "a", encoding="utf-8") as f:
            f.write("\n".join(sorted(words)) + "\n")

    def filter_known_words(self, all_words: List[str]) -> List[str]:
        """
        Filter out known words from a list.

        Args:
            all_words: List of all words

        Returns:
            List of unknown words (not in known words set)
        """
        known = self.load_words()
        unknown = []

        for word in all_words:
            if word not in known:
                unknown.append(word)

        return unknown

    def get_count(self) -> int:
        """
        Get the count of known words.

        Returns:
            Number of known words
        """
        return len(self.load_words())

    def get_all_words(self) -> List[str]:
        """
        Get all known words as a sorted list.

        Returns:
            Sorted list of known words
        """
        return sorted(self.load_words())
