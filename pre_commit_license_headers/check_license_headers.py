# Copyright (c) 2019-2021 The Pre-Commit License Headers Authors
# Use of this source code is governed by a BSD-3-clause license that can
# be found in the LICENSE file or at https://opensource.org/licenses/BSD-3-Clause

"""Checks if file(s) match the provided license header."""


import argparse
import cmd
import re
import sys
import tokenize
from pathlib import Path
from typing import List, Optional, Sequence

from identify import identify

from pre_commit_license_headers.file_types import (
    ALL_TEXT_FILE_TYPES,
    DEFAULT_FILE_TYPES,
)


HEADER_TOKENS = [tokenize.COMMENT, tokenize.ENCODING, tokenize.NEWLINE, tokenize.NL]
TEMPLATE_OWNER_KEY = "[OWNER]"
TEMPLATE_YEARS_KEY = "[YEARS]"
YEARS_RE_STR = r"\d{4}(?:-\d{4}|,\ \d{4})*"
SHEBANG_RE = re.compile(r"#!/.{1,30}\s*")
DEFAULT_HEADER_TEMPLATE = """Copyright (c) [YEARS] [OWNER]
Use of this source code is governed by a BSD-3-clause license that can
be found in the LICENSE file or at https://opensource.org/licenses/BSD-3-Clause
"""


def check_license_headers(filepath: Path, header_pattern: str, debug: bool) -> bool:
    content_lines = []

    with filepath.open() as f:
        tokens_generator = list(tokenize.generate_tokens(f.readline))

        for token in tokens_generator:
            if token.type not in HEADER_TOKENS:
                # we've reached the end of the header
                break
            elif token.type != tokenize.COMMENT:
                continue

            line = token.string.strip()

            # skip shebang ('#!')
            if any(regex.fullmatch(line) for regex in [SHEBANG_RE]):
                continue

            # these are the lines we care about
            comment = line.replace("#", "").strip()
            if comment:
                content_lines.append(comment)

    if debug:
        print(f"DEBUG: found {len(content_lines)} header content lines")

    content = " ".join(content_lines)

    if not content:
        print(f"MISSING HEADER {filepath}")
        return False

    if not re.fullmatch(header_pattern, content):
        if len(content_lines) > 5:
            content = f"{' '.join(content_lines[:5])}...\n[truncated]"
        print(f"HEADER MISMATCH {filepath}\n{content}")
        return False

    return True


def get_header_pattern(header_template: str, owner: str, debug: bool) -> str:
    """Constructs the expected header regex pattern."""
    header_pattern: str

    header_pattern = " ".join([x.strip() for x in header_template.splitlines()])
    header_pattern = re.escape(header_pattern)

    if TEMPLATE_OWNER_KEY in header_template:
        header_pattern = header_pattern.replace(re.escape(TEMPLATE_OWNER_KEY), owner)
    elif owner:
        print(
            f"WARNING '--owner' will be ignored (template is missing '{TEMPLATE_OWNER_KEY}')"
        )

    if TEMPLATE_YEARS_KEY in header_template:
        header_pattern = header_pattern.replace(
            re.escape(TEMPLATE_YEARS_KEY), YEARS_RE_STR
        )

    if debug:
        print(f"\nDEBUG expected header pattern:\n{header_pattern}\n")

    return header_pattern


def process_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Checks if file headers match a provided template."
    )
    parser.add_argument("-d", "--debug", action="store_true")
    parser.add_argument(
        "--list-file-types",
        action="store_true",
        help="lists all text file types and exits",
    )
    parser.add_argument(
        "-s",
        "--summary",
        action="store_true",
        help="prints a summary after checking the files",
    )
    parser.add_argument(
        "-f",
        "--file-type",
        action="append",
        choices=ALL_TEXT_FILE_TYPES,
        dest="file_types",
        metavar="FILE_TYPE",
        help="may be specified multiple times",
    )
    parser.add_argument("-o", "--owner", default=None, metavar="COPYRIGHT_OWNER")
    parser.add_argument("-t", "--template", default=DEFAULT_HEADER_TEMPLATE)
    parser.add_argument("filenames", type=Path, nargs="*", metavar="FILE")
    args = parser.parse_args(argv)

    if not args.file_types:
        args.file_types = DEFAULT_FILE_TYPES

    cli = cmd.Cmd()

    if args.list_file_types:
        cli.columnize(sorted(ALL_TEXT_FILE_TYPES))
        sys.exit(0)

    if args.debug:
        print("DEBUG checking files matching any of the following:")
        cli.columnize(sorted(args.file_types))

    if not args.owner and TEMPLATE_OWNER_KEY in args.template:
        print(f"ERROR template has '{TEMPLATE_OWNER_KEY}', but '--owner' not provided")
        sys.exit(-1)

    if not args.filenames:
        print("No files provided")
        sys.exit(0)

    return args


def main(argv: Optional[Sequence[str]] = None) -> None:
    args = process_args(argv)
    expected_pattern = get_header_pattern(args.template, args.owner, args.debug)

    valid: List[Path] = []
    invalid: List[Path] = []
    skipped: List[Path] = []

    for filename in args.filenames:
        filepath = Path(filename)

        if not filepath.is_file():
            continue

        file_tags = identify.tags_from_path(str(filepath.absolute()))
        if "text" not in file_tags:
            if args.debug:
                print(f"IGNORING {filepath} (not a text file)")
            continue

        if not any(x in file_tags for x in args.file_types):
            if args.debug:
                print(
                    f"IGNORING {filepath} (wrong file type; types found: {file_tags})"
                )
            continue

        try:
            if args.debug:
                print(f"DEBUG checking {filepath}")

            license_match = check_license_headers(
                filepath,
                expected_pattern,
                debug=args.debug,
            )
            if license_match:
                valid.append(filepath)
            else:
                invalid.append(filepath)
        except tokenize.TokenError:
            print(f"SKIPPING {filepath} (failed to tokenize)")
            skipped.append(filepath)

    if args.summary:
        print("\n")
        if skipped:
            print("The following files were skipped:")
            print("\n".join([str(x) for x in skipped]))
            print("\n")
        if invalid:
            print("The following files have invalid license headers:")
            print("\n".join([str(x) for x in invalid]))
            print("\n")
        print(
            f"SUMMARY: {len(valid)} valid; {len(invalid)} invalid; {len(skipped)} skipped"
        )

    if skipped:
        sys.exit(2)
    elif invalid:
        sys.exit(1)
    else:
        sys.exit(0)
