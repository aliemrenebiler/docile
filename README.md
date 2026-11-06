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
tells you if that folder needs to be added to your `PATH`. Check it with:

```sh
docxer --version
```

## Commands

```sh
docxer -h                # list the commands
docxer <command> -h      # options of one command
docxer update            # update docxer to the latest release
docxer update --check    # only check if there is a newer release
```

### examples

Copies the example files (see [Files](#files)) so you can try docxer or use
them as a starting point.

```sh
docxer examples                  # into the current folder
docxer examples -d my-cv         # into another folder (-d / --dir)
```

Files that already exist are skipped, never overwritten.

### create

Fills a template with the data from a JSON file and saves a `.docx`.

```sh
docxer create <json-file> <template-docx-file>
docxer create <json-file> <template-docx-file> -o <output-docx-file>
docxer create <json-file> <template-docx-file> -s <schema-json-file>
docxer create <json-file> <template-docx-file> -o <output-docx-file> -y
```

- `<json-file>` and `<template-docx-file>` are required.
- `-o` / `--output` is the file to write. Default: `docxer_<date>_<time>.docx`
  in the current folder. If it is an existing folder, the file is created in it
  with the default name.
- If the output file already exists, docxer asks `Overwrite? [y/N]` and writes
  nothing unless you answer `y`. Add `-y` / `--yes` to overwrite without asking
  (needed when there is no terminal to answer, like in a script).
- `-s` / `--schema` checks the JSON against a schema first. If it does not
  match, every problem is listed and no file is written.

The output name can contain date/time tokens in `{{ }}`: `YYYY` `YY` `MMMM`
`MMM` `MM` `dd` `HH` `hh` `mm` `ss` `a`. For example:

```sh
docxer create input.json template.docx -o "out/Jane-Doe_CV_{{YYYY}}-{{MM}}-{{dd}}.docx"
```

### mcp

Runs docxer as an MCP server, so Claude Desktop can use it as a tool. You don't
run this yourself: Claude Desktop starts it. See
[Use with Claude Desktop](#use-with-claude-desktop).

## Files

`docxer examples` copies an example of each file below.

### Data

Any JSON object. Its keys are what the template tags refer to, so
`{"name": "Jane"}` fills `{{ name }}`. (`input.example.json`)

- A key the template uses but the JSON lacks renders empty, with a warning.
- A missing parent object (like `contact` for `{{ contact.email }}`) is an error.

### Schema

An optional [JSON Schema](https://json-schema.org) that says what the JSON must
look like (required keys, types). Used with `create -s`. Any file name works.
(`schema.example.json`)

```
Error: input.json does not match schema.json:
  $.contact: 'email' is a required property
  $.experience[0].start.year: 'x' is not of type 'integer'
```

### Template

A normal Word file with tags where the values go. Your styles are kept.
(`template.example.docx`)

- Value: `{{ name }}`, `{{ contact.email }}`
- Repeat a block: a line `{%p for job in experience %}`, the block, then `{%p endfor %}`
- Optional line: `{%p if job.description %}` ... `{%p endif %}`
- Type each tag in one go, so Word doesn't split it.

Tags use Jinja syntax (via `docxtpl`).

## Use with Claude Desktop

Claude Desktop can't run commands on your computer, but it can use docxer as a
tool through `docxer mcp`. Then you can ask Claude to fill a template in plain
language. Claude Desktop starts docxer by itself when it opens and stops it
when it quits, so there is nothing to keep running. These steps are for macOS.

1. **Install docxer** (see [Install](#install)) and run `which docxer`. Copy the
   path it prints, for example `/Users/jane/.local/bin/docxer`.

2. **Add docxer to Claude Desktop.** Go to Settings → Developer → Edit Config.
   This shows `claude_desktop_config.json` in Finder; open it with any text
   editor and paste this, with your path from step 1. If the file already has
   `"mcpServers"`, add only the `"docxer"` line inside it.

   ```json
   {
     "mcpServers": {
       "docxer": { "command": "/Users/jane/.local/bin/docxer", "args": ["mcp"] }
     }
   }
   ```

3. **Restart Claude Desktop** completely (Cmd+Q, then open it again). In
   Settings → Developer, `docxer` should be listed as running.

4. **Ask Claude.** Give full file paths, because Claude can't see your files
   on its own:

   > Which fields does `/Users/jane/cv/template.docx` need?

   > Fill `/Users/jane/cv/template.docx` with my details below, check it with
   > `/Users/jane/cv/schema.json`, and save it in `/Users/jane/Documents`.
   > My details: ...

   Claude asks you to allow each tool call the first time.

If `docxer` doesn't show up, check that the config is valid JSON, that the path
is the one from `which docxer`, and that you fully restarted Claude Desktop.
The log is at `~/Library/Logs/Claude/mcp-server-docxer.log`.
