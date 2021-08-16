# Pre-Commit License Headers

A [pre-commit](https://github.com/pre-commit/pre-commit) hook to check the license
headers of your source code files.

At present, it only supports checking files that use hash mark `#` comment syntax. For
more info, see [Supported file types](#supported-file-types).

### Usage

Add an entry like this to your `.pre-commit-config.yaml`

```yaml
- repo: https://github.com/johannsdg/pre-commit-license-headers
  rev: v0.1.0 # Use the ref you want to point at
  hooks:
    - id: check-license-headers
      args:
        - "--template"
        - |
          Copyright (c) [YEARS] [OWNER]
          Use of this source code is governed by a BSD-3-clause license that can
          be found in the LICENSE file or at https://opensource.org/licenses/BSD-3-Clause
        - "--owner=The Pre-Commit License Headers Authors"
```

(Note that the template provided above is the default, so if you are using BSD-3-clause
and are happy with the wording, you can skip `--template` and just provide `--owner`)

`[YEARS]` and `[OWNER]` are optional variables in the header template. If used, they
will automatically be replaced with:

- `[YEARS]`: a regular expression that accepts various combinations of years, such as:
  - Single years, such as '2019' or '2021'
  - Year ranges, such as '2018-2020'
  - Combinations, such as '2014, 2016-2018, 2020'
  - Note that ranges ending in '-present' are not supported
- `[OWNER]`: the contents of the `--owner` argument
  - Note that `--owner` is optional unless the template uses the `[OWNER]` variable

### Supported file types

`Pre-Commit License Headers` supports checking file types that use hash mark `#` comment
syntax.

This includes:

- python
- shell
- yaml
- toml
- plain-text
- etc

For the list of file types checked by default, see
[file_types.py](pre_commit_license_headers/file_types.py) You may override the default
list with your own via the `-f` or `--file-type` option (may be specified multiple
times).

File types are determined using the [identify](https://github.com/pre-commit/identify)
library. For more information about file types, see:
https://pre-commit.com/#filtering-files-with-types

### As a standalone package

`Pre-Commit License Headers` is also available as a standalone package.

To install via pip:

`pip install pre-commit-license-headers`

You may also clone this repo and install via [poetry](https://python-poetry.org/):

`poetry install --no-dev`

Either installation option will place the `check-license-headers` executable in your
environment's configured binary directory (e.g., '.venv/bin')

To use:

```console
foo@bar:~$ check-license-headers --help
usage: check-license-headers [-h] [-d] [--list-file-types] [-s] [-f FILE_TYPE]
                             [-o COPYRIGHT_OWNER] -t TEMPLATE
                             [FILE [FILE ...]]

Checks if file headers match a provided template.

positional arguments:
  FILE

optional arguments:
  -h, --help            show this help message and exit
  -d, --debug
  --list-file-types     lists all text file types and exits
  -s, --summary         prints a summary after checking the files
  -f FILE_TYPE, --file-type FILE_TYPE
                        may be specified multiple times
  -o COPYRIGHT_OWNER, --owner COPYRIGHT_OWNER
  -t TEMPLATE, --template TEMPLATE
```
