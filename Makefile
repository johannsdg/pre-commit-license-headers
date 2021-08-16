# Copyright (c) 2021 The Pre-Commit License Headers Authors
# Use of this source code is governed by a BSD-3-clause license that can
# be found in the LICENSE file or at https://opensource.org/licenses/BSD-3-Clause

BUMPVERSION = poetry run bump2version --verbose

# cleanup
clean:
	$(MAKE) clean-files

clean-files: clean-test-files
	rm -rf build dist ./*.egg-info

clean-test-files:
	rm -rf coverage htmlcov .pytest_cache

# linting
lint:
	poetry run pre-commit run check-ast
	poetry run pre-commit run --show-diff-on-failure

lint-all:
	poetry run pre-commit run -a check-ast
	poetry run pre-commit run -a --show-diff-on-failure


# testing
test: clean-test-files
	poetry run coverage erase
	poetry run pytest --cov=pre_commit_license_headers --cov-report=term --cov-report=html tests/

test-with-html: test
	cd htmlcov && poetry run python -m http.server 9000

# other
dev-setup:
	poetry install
	poetry run pre-commit install --install-hooks -t pre-commit -t pre-push -t commit-msg

commit: lint
	poetry run cz c

commit-retry:
	poetry run cz c --retry

package:
	poetry build
	poetry run twine check dist/*

changelog:
	poetry run cz ch --incremental

check-packages:
	poetry show --outdated

bump-major:
	$(BUMPVERSION) major

bump-minor:
	$(BUMPVERSION) minor

bump-patch:
	$(BUMPVERSION) patch

bump-build:
	$(BUMPVERSION) build

.PHONY: test clean lint package commit changelog
