# docxer

Generates a Word document (`.docx`) from a JSON file, using your own styled
Word file as the template. It works with any template: the tags inside the
template decide which values it needs from the JSON.

## Setup (once)

Needs Python 3.10+. From the project folder:

```sh
python3 -m venv .venv          # create the virtual environment
source .venv/bin/activate      # activate it (Windows: .venv\Scripts\activate)
pip install -e .               # install docxer and its dependencies
```

Activate the venv (`source .venv/bin/activate`) again in every new terminal.
You can also skip activating and call `.venv/bin/docxer` directly.

## Commands

```sh
docxer -h                                      # list the commands
docxer create -h                               # options of one command (any command)

docxer examples                                # copy example files to the current folder
docxer examples -o <folder>                    # ...or to another folder

docxer create <json-file> <template-docx-file>
docxer create <json-file> <template-docx-file> -o <output-docx-file>
```

Without installing the command you can use `python -m docxer` instead of
`docxer`, e.g. `python -m docxer create cv.json template.docx`.

- `examples`: copies `input.example.json` and `template.example.docx`.
  Existing files are never overwritten. `-o` is optional (default: current
  folder).
- `create`: fills the template with the JSON data. `<json-file>` and `<template-docx-file>` are
  required, and you get a warning if one is missing. `-o` is optional (default:
  `docxer_<date>_<time>.docx` in the current folder).

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

```sh
pip install -e ".[dev]"      # adds Black
black src                    # format
```

The example files live in `src/docxer/examples/`. Generated files go to `tmp/`,
which is git-ignored.
