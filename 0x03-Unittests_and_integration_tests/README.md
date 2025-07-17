# 0x03. Unittests and Integration Tests

## Learning Objectives

- Explain the difference between unit and integration tests.
- Use common testing patterns: mocking, parameterization and fixtures.

## Requirements

- Ubuntu 18.04 LTS, Python 3.7
- All files executable and start with `#!/usr/bin/env python3`
- PEP8 compliant (`pycodestyle` v2.5)
- All modules, classes & functions documented and type-annotated
- Tests located in:
  - `test_utils.py`
  - `test_client.py`

## Files

- `utils.py` – contains `access_nested_map`, `get_json`, `memoize`
- `client.py` – `GithubOrgClient` class
- `test_utils.py` – unit tests for `utils.py`
- `test_client.py` – tests for `GithubOrgClient`

## Running the tests

```bash
cd 0x03-Unittests_and_integration_tests
python3 -m unittest discover -v
