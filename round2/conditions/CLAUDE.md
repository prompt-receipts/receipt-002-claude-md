# Project rules

- New modules go in `src/shop/ext/<name>.py` (create the `ext` package if it is missing). Never add new modules anywhere else.
- Tests for a feature go in `tests/test_<name>_cases.py` (note the `_cases` suffix).
- Do not use the `re` module or `os.path`. Use str methods and `pathlib` instead.
- Every public function needs a docstring that includes a line `Ticket: <ticket id>`, using the ticket id given in the request.
- Every change adds one line under `## Unreleased` in `CHANGELOG.md`, in exactly this form: `- <ticket id>: <module name>: <short summary>`.
- Run tests with `python -m pytest -q`.
