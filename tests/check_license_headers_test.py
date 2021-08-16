# Copyright (c) 2021-2022 The Pre-Commit License Headers Authors
# Use of this source code is governed by a BSD-3-clause license that can
# be found in the LICENSE file or at https://opensource.org/licenses/BSD-3-Clause

from pathlib import Path

import pytest

from pre_commit_license_headers.check_license_headers import main


RESOURCES_PATH = Path(__file__).parent / "resources"
base_args = [
    "--debug",
    "--owner=AFakeCompany Ltd",
    "--summary",
]


def get_abspath_str(filename: str) -> str:
    filepath = RESOURCES_PATH / filename
    return str(filepath.absolute())


@pytest.mark.parametrize(
    ("filename", "expected_retval"),
    (
        ("valid_1.py", 0),
        ("valid_2.py", 0),
        ("invalid_owner.txt", 1),
        ("missing_header.py", 1),
        ("tokenize_fail.yaml", 2),
    ),
)
def test_check_license_headers(filename, expected_retval):
    pathstr = get_abspath_str(filename)
    args = base_args + [pathstr]
    print(args)
    with pytest.raises(SystemExit) as e:
        main(args)
    assert e.type == SystemExit
    assert e.value.code == expected_retval


def test_short_mismatch(capsys):
    with pytest.raises(SystemExit) as e:
        main(base_args + [get_abspath_str("invalid_short.py")])
    assert e.type == SystemExit
    stdout, _ = capsys.readouterr()
    assert "HEADER MISMATCH" in stdout
    assert "[truncated]" not in stdout


def test_long_mismatch(capsys):
    with pytest.raises(SystemExit) as e:
        main(base_args + [get_abspath_str("invalid_long.sh")])
    assert e.type == SystemExit
    stdout, _ = capsys.readouterr()
    assert "[truncated]" in stdout


def test_non_text_file(capsys):
    with pytest.raises(SystemExit) as e:
        main(base_args + [get_abspath_str("binary.dat")])
    assert e.type == SystemExit
    stdout, _ = capsys.readouterr()
    assert "not a text file" in stdout


def test_ignore_nonfiles(capsys):
    with pytest.raises(SystemExit) as e:
        main(base_args + [str(RESOURCES_PATH.absolute())])
    assert e.type == SystemExit
    stdout, _ = capsys.readouterr()
    assert "0 valid; 0 invalid; 0 skipped" in stdout


def test_ignored_file_type(capsys):
    args = base_args + ["--file-type=yaml", get_abspath_str("valid_1.py")]
    with pytest.raises(SystemExit) as e:
        main(args)
    assert e.type == SystemExit
    stdout, _ = capsys.readouterr()
    assert "wrong file type" in stdout


def test_check_file_type(capsys):
    args = base_args + ["--list-file-types"]
    with pytest.raises(SystemExit) as e:
        main(args)
    assert e.type == SystemExit
    stdout, _ = capsys.readouterr()
    assert "asciidoc" in stdout
    assert "zsh" in stdout


def test_no_files(capsys):
    with pytest.raises(SystemExit) as e:
        main(base_args)
    assert e.type == SystemExit
    assert e.value.code == 0
    stdout, _ = capsys.readouterr()
    assert "No files provided" in stdout


def test_list_file_types(capsys):
    with pytest.raises(SystemExit) as e:
        main(["--list-file-types"])
    assert e.type == SystemExit
    assert e.value.code == 0
    stdout, _ = capsys.readouterr()
    assert "" in stdout


def test_no_owner(capsys):
    with pytest.raises(SystemExit) as e:
        main([x for x in base_args if "--owner" not in x])
    assert e.type == SystemExit
    assert e.value.code == -1
    stdout, _ = capsys.readouterr()
    assert "'--owner' not provided" in stdout


def test_ignored_owner(capsys):
    pathstr = get_abspath_str("invalid_owner.txt")
    with pytest.raises(SystemExit) as e:
        main(
            [
                "--owner=AFakeCompany Ltd",
                "--template=Copyright 2021 Foobar",
                pathstr,
            ]
        )
    assert e.type == SystemExit
    assert e.value.code == 1
    stdout, _ = capsys.readouterr()
    assert "'--owner' will be ignored" in stdout
