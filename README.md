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
resgen data/input.me.json               # a specific input file
resgen data/input.me.json -o out.docx   # a specific output file

# As a script (no command needed)
python -m resgen
python -m resgen data/input.me.json
```

The result is written to the `output` path from the settings (date and time
included). Flags `-t`, `-o` and `-s` override the template, output and settings.

## Files

Everything lives flat in `data/`:

```
data/
  settings.json              which files to use
  template.<name>.docx       Word template (tags like {{ name }} inside)
  input.<name>.json          CV content
  (generated files go to tmp/, see output below)
```

Everything in `data/` is git-ignored except these example files:

- `data/settings.json` (points at the example files)
- `data/template.example.docx`
- `data/input.example.json`

Out of the box `resgen` renders the example. To use your own CV, add
`data/template.<name>.docx` and `data/input.<name>.json`, then point
`data/settings.json` at them. Your own files stay git-ignored.

## Settings (`data/settings.json`)

Full file paths, including the extension:

```json
{
  "template": "data/template.example.docx",
  "input": "data/input.example.json",
  "output": "tmp/example_{{YYYY}}-{{MM}}-{{dd}}_{{HH}}-{{mm}}-{{ss}}.docx"
}
```

- `template`: the Word template
- `input`: the CV JSON
- `output`: where to write the result. Date/time tokens are filled in:
  `YYYY` `YY` `MMMM` `MMM` `MM` `dd` `HH` `hh` `mm` `ss` `a`

## Input JSON

See `data/input.example.json` for every field. Print the full schema (for
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
