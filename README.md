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
docxer create <json-file> <template-docx-file> -s <schema-json-file>
```

- `examples`: copies `input.example.json`, `template.example.docx` and
  `schema.example.json`.
  Existing files are never overwritten. `-o` is optional (default: current
  folder).
- `create`: fills the template with the JSON data. `<json-file>` and `<template-docx-file>` are
  required, and you get a warning if one is missing. `-o` is optional (default:
  `docxer_<date>_<time>.docx` in the current folder). `-s`/`--schema` is
  optional: see [Schema check](#schema-check).

- `mcp`: runs docxer as an MCP server for Claude Desktop, see
  [Use with Claude Desktop](#use-with-claude-desktop).

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

## Schema check

`-s <schema-json-file>` validates the JSON against a
[JSON Schema](https://json-schema.org) before anything is created. If it does
not match, every problem is listed with its location and no `.docx` is written:

```
Error: input.json does not match schema.json:
  $.contact: 'email' is a required property
  $.experience[0].start.year: 'x' is not of type 'integer'
```

`schema.example.json` (from `docxer examples`) matches `input.example.json`.

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

## Use with Claude Desktop

`docxer mcp` lets Claude Desktop use docxer as a tool, so you can ask Claude to
fill a template without a terminal. Claude Desktop starts it by itself when it
opens and stops it when it quits, so there is nothing to keep running.

Add this to Claude Desktop's config (Settings → Developer → Edit Config, the
file is `~/Library/Application Support/Claude/claude_desktop_config.json`),
with the full path from `which docxer`, then restart Claude Desktop:

```json
{
  "mcpServers": {
    "docxer": { "command": "/Users/<you>/.local/bin/docxer", "args": ["mcp"] }
  }
}
```

Claude gets these tools. All file paths must be absolute.

- `get_template_variables`: the names a `.docx` template uses (what the JSON needs).
- `get_examples`: the example JSON and schema.
- `validate_json`: check JSON against a schema and list the problems.
- `create_docx_file`: fill a template with the JSON Claude wrote. Takes an
  optional schema and output path (default: the template's folder).

Example: "Fill `/Users/me/cv/template.docx` with my details and check it with
`/Users/me/cv/schema.json`."

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

### Project layout

```
src/docxer/
  core/            shared logic: render, schema check, output names, create
  cli.py           command line (thin: arguments, printing)
  mcp_server.py    MCP server (thin: tool definitions)
  update.py        self-update
  examples/        example JSON, schema and template
```

New behavior goes in `core/`, so the CLI and the MCP server stay in sync.

### Releasing

1. Bump `__version__` in `src/docxer/__init__.py` and commit it.
2. Tag and push: `git tag v0.2.0 && git push origin v0.2.0`.

The `release` workflow builds the binaries for macOS (arm64, x86_64) and Linux
(x86_64, aarch64), smoke-tests them, and publishes them with `SHA256SUMS` and
`VERSION` to a GitHub Release. `install.sh` and `docxer update` read from the
latest release. The workflow can also be started by hand (Actions tab) to build
and test the binaries without publishing.
