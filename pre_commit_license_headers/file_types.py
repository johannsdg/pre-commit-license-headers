# Copyright (c) 2019-2021 The Pre-Commit License Headers Authors
# Use of this source code is governed by a BSD-3-clause license that can
# be found in the LICENSE file or at https://opensource.org/licenses/BSD-3-Clause

from identify.extensions import EXTENSIONS


ALL_TEXT_FILE_TYPES = [k for k, v in EXTENSIONS.items() if "text" in v]
DEFAULT_FILE_TYPES = [
    "cython",
    "dockerfile",
    "graphql",
    "ini",
    "jupyter",
    "markdown",
    "makefile",
    "perl",
    "plain-text",
    "puppet",
    "python",
    "r",
    "shell",
    "toml",
    "yaml",
]
