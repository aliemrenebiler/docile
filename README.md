# resgen

Generates a Word CV (`.docx`) from a JSON file, using your own styled Word
file as the template.

## Setup (once)

Needs Python 3.10+. From the project folder:

```sh
python3 -m venv .venv          # create the virtual environment
source .venv/bin/activate      # activate it (Windows: .venv\Scripts\activate)
pip install -e .               # install resgen and its dependencies
```

Activate the venv (`source .venv/bin/activate`) again in every new terminal.
You can also skip activating and call `.venv/bin/resgen` directly.

## Commands

```sh
resgen -h                                      # list the commands
resgen create -h                               # options of one command (any command)

resgen examples                                # copy example files to the current folder
resgen examples -o <folder>                    # ...or to another folder

resgen create <json-file> <template-docx-file>
resgen create <json-file> <template-docx-file> -o <output-docx-file>
```

Without installing the command you can use `python -m resgen` instead of
`resgen`, e.g. `python -m resgen create cv.json template.docx`.

| Command    | What it does |
|------------|--------------|
| `examples` | Copies `input.example.json` and `template.example.docx`. Existing files are never overwritten. `-o` is optional (default: current folder). |
| `create`   | Renders the CV. Both `<json-file>` and `<template-docx-file>` are required; you get a warning if one is missing. `-o` is optional (default: `resgen_<date>_<time>.docx` in the current folder). |
| `schema`   | Prints the JSON Schema of the input, for validating from other tools. |

### Quick start

```sh
resgen examples -o my-cv
resgen create my-cv/input.example.json my-cv/template.example.docx -o my-cv/cv.docx
```

### Output file name

`-o` can contain date/time tokens in `{{ }}`:
`YYYY` `YY` `MMMM` `MMM` `MM` `dd` `HH` `hh` `mm` `ss` `a`, for example
`-o "out/Jane-Doe_CV_{{YYYY}}-{{MM}}-{{dd}}.docx"`. If `-o` is an existing
folder, the file is created in it with the default name.

## Input JSON

Start from `input.example.json` (every field is in there). Notes:

- Dates are `{"month": "Sep", "year": 2016}`. Leave out `end` for "Present".
- Optional values (`description`, `link`, dates, ...) can simply be left out.
- Unknown or misspelled fields are rejected with a clear error.

## Template

The template is a normal Word file. Put tags where values go and keep your
styles as they are:

- Value: `{{ name }}`, `{{ contact.email }}`
- Repeat a block: a line `{%p for job in experience %}`, the block, then
  `{%p endfor %}`
- Optional line: `{%p if job.description %}` ... `{%p endif %}`
- Each tag must be typed in one go, so Word doesn't split it.

The `dates` field (`{{ job.dates }}`) is built for you, e.g. `Mar 2021 – Present`.
See `template.example.docx` for a working template.

## Development

```sh
pip install -e ".[dev]"      # adds Black
black src                    # format
```

The example files live in `src/resgen/examples/`. Generated files go to `tmp/`,
which is git-ignored.
