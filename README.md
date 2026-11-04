# docxer

Generates a Word document (`.docx`) from a JSON file, using your own styled
Word file as the template. It works with any template: the tags inside the
template decide which values it needs from the JSON.

## Install

macOS and Linux, one command (no Python needed):

```sh
curl -fsSL https://raw.githubusercontent.com/aliemrenebiler/docxer/main/install.sh | sh
```

It downloads the right binary for your machine to `~/.local/bin/docxer` and
tells you if that folder needs to be added to your `PATH`. Then:

```sh
docxer -h                # list the commands
docxer --version
docxer update            # update to the latest release
docxer update --check    # only check if there is a newer release
```

## Commands

```sh
docxer -h                                      # list the commands
docxer create -h                               # options of one command (any command)

docxer examples                                # copy example files to the current folder
docxer examples -o <folder>                    # ...or to another folder

docxer create <json-file> <template-docx-file>
docxer create <json-file> <template-docx-file> -o <output-docx-file>
```

- `examples`: copies `input.example.json` and `template.example.docx`.
  Existing files are never overwritten. `-o` is optional (default: current
  folder).
- `create`: fills the template with the JSON data. `<json-file>` and `<template-docx-file>` are
  required, and you get a warning if one is missing. `-o` is optional (default:
  `docxer_<date>_<time>.docx` in the current folder).

- `update`: replaces `docxer` with the latest release (`--check` only checks).

### Quick start

```sh
docxer examples -o my-cv
docxer create my-cv/input.example.json my-cv/template.example.docx -o my-cv/cv.docx
```

### Output file name

`-o` can contain date/time tokens in `{{ }}`:
`YYYY` `YY` `MMMM` `MMM` `MM` `dd` `HH` `hh` `mm` `ss` `a`, for example
`-o "out/Jane-Doe_CV_{{YYYY}}-{{MM}}-{{dd}}.docx"`. If `-o` is an existing
folder, the file is created in it with the default name.

## JSON data

Any JSON object works. Its keys are what the template tags refer to, so
`{"name": "Jane"}` fills `{{ name }}`. `input.example.json` is a full CV example.

- A tag whose key is missing in the JSON renders as empty; `create` prints a
  warning for top-level names the template uses but the JSON does not have.
- A missing parent object (e.g. `contact` when the template uses
  `{{ contact.email }}`) is an error.
- Dates and similar values are just data. In the example, `end` is either
  `"Present"` or `{"month": "Jun", "year": 2016}`, and the template handles both.

## Template

The template is a normal Word file. Put tags where values go and keep your
styles as they are:

- Value: `{{ name }}`, `{{ contact.email }}`
- Repeat a block: a line `{%p for job in experience %}`, the block, then
  `{%p endfor %}`
- Optional line: `{%p if job.description %}` ... `{%p endif %}`
- Inline choice: `{% if job.end is string %}{{ job.end }}{% else %}{{ job.end.month }} {{ job.end.year }}{% endif %}`
- Each tag must be typed in one go, so Word doesn't split it.

Templates use Jinja syntax (via `docxtpl`). See `template.example.docx` for a
working template.

## Development

Needs Python 3.10+. From the project folder:

```sh
python3 -m venv .venv          # create the virtual environment
source .venv/bin/activate      # activate it
pip install -e ".[dev]"        # install docxer, Black and PyInstaller
```

You can also call `.venv/bin/docxer` or `python -m docxer` directly.

```sh
black src                      # format
```

The example files live in `src/docxer/examples/`.

### Releasing

1. Bump `__version__` in `src/docxer/__init__.py` and commit it.
2. Tag and push: `git tag v0.2.0 && git push origin v0.2.0`.

The `release` workflow builds the binaries for macOS (arm64, x86_64) and Linux
(x86_64, aarch64), smoke-tests them, and publishes them with `SHA256SUMS` and
`VERSION` to a GitHub Release. `install.sh` and `docxer update` read from the
latest release. The workflow can also be started by hand (Actions tab) to build
and test the binaries without publishing.
