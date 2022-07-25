#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import sys
import time
import pathlib
import subprocess

import nltk
import enchant

NAME = "sscout"

enchant_dict = enchant.Dict("en_US")
re_word = re.compile(r"[a-zA-Z]")


def main() -> None:
    if len(sys.argv) != 2:
        print(f"usage: python {sys.argv[0]} ${{subtitle_file}}")
        sys.exit(1)

    words = remove_known_words(split_into_words(sys.argv[1]))
    tfile = write_tfile(words)
    subprocess.Popen(("vim", tfile)).wait()

    unknown_words = []
    with open(tfile, "r") as f:
        for new_word in f.readlines():
            w = new_word.strip()
            if w != "":
                unknown_words.append(w)

    add_known_words(set(words) - set(unknown_words))

    top_unknown_words = unknown_words[0:20]
    topfile = pathlib.Path("/mnt/user-data-app/static-resource").joinpath(f"{NAME}.top-words.{tfile.name}")
    with open(topfile, "w") as f:
        f.write("\n".join(top_unknown_words) + "\n")

    print(f"open https://static-server.uen.site/{topfile.name}")


def remove_known_words(words):
    all_known_words = get_known_words()

    unknown_words = []
    for word in words:
        if word not in all_known_words:
            unknown_words.append(word)

    return unknown_words


def add_known_words(words):
    with open(get_known_file(), "a") as f:
        f.write("\n".join(words) + "\n")


def get_home_dir():
    d = pathlib.Path.home().joinpath(f".{NAME}")
    d.mkdir(parents=True, exist_ok=True)
    return d


def get_cache_dir():
    d = get_home_dir().joinpath("cache")
    d.mkdir(parents=True, exist_ok=True)
    return d


def get_known_file():
    f = get_home_dir().joinpath("known-words.txt")
    if not f.exists():
        f.touch()
    return f


def get_known_words():
    words = set()
    with open(get_known_file(), "r") as f:
        for word in f.readlines():
            w = word.strip()
            if w != "":
                words.add(w)
    return words


def write_tfile(words):
    tfilename = get_cache_dir().joinpath(f"{time.strftime('%Y%m%d%H%M%S')}.txt")
    with open(tfilename, "w") as f:
        f.write("\n".join(words))
    return tfilename


def is_word(token):
    return len(token) > 1 and enchant_dict.check(token) and re_word.match(token)


def read_subtitle(filename: str) -> str:
    with open(filename, "r") as f:
        return f.read()


def split_into_words(filename: str) -> set:
    infos = {}
    content = read_subtitle(filename)
    for token in nltk.tokenize.word_tokenize(content):
        if token.endswith(".") and token.count(".") == 1:
            token = token.replace(".", "")

        if not is_word(token):
            continue

        token = token.lower()
        if token not in infos:
            infos[token] = 0

        infos[token] += 1

    return [word for word, _ in sorted(infos.items(), key=lambda items: -items[1])]


if __name__ == "__main__":
    main()
