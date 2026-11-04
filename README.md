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
You can also skip activating and call `.venv/bin/resgen` or
`.venv/bin/python` directly.

## Use

Always run from the project folder (paths are relative to it).

```sh
# As a command (after setup)
resgen                                  # uses data/settings.json
resgen data/inputs/me.json              # a specific input file
resgen data/inputs/me.json -o out.docx  # a specific output file

# As a script (no command needed)
python -m resgen
python -m resgen data/inputs/me.json
```

The result is written to `data/outputs/`, named by `output_name` in the
settings (date and time included).

## Folders

```
data/
  settings.json         which template/input to use, output file name
  templates/cv.docx     your Word template (tags like {{ name }} inside)
  inputs/me.json        your CV content
  outputs/              generated files (git-ignored)
```

Everything in `data/` is git-ignored except the `example` files, so you can
copy them as a starting point:

- `data/settings.example.json`
- `data/templates/example.docx`
- `data/inputs/example.json`

Try the example: `resgen data/inputs/example.json -s data/settings.example.json -t data/templates/example.docx`

## Settings (`data/settings.json`)

```json
{
  "template_name": "cv",
  "input_name": "me",
  "output_name": "My-Name_CV_{{YYYY}}-{{MM}}-{{dd}}_{{HH}}-{{mm}}-{{ss}}"
}
```

- `template_name`: file in `data/templates/`, without `.docx`
- `input_name`: file in `data/inputs/`, without `.json`
- `output_name`: output file name without `.docx`. Date/time tokens:
  `YYYY` `YY` `MMMM` `MMM` `MM` `dd` `HH` `hh` `mm` `ss` `a`

## Input JSON

See `data/inputs/example.json` for every field. Print the full schema (for
validating from other tools) with:

```sh
resgen --schema > schema.json
```

Notes:
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
