# Docile

Generates a Word document (`.docx`) from a JSON file, using your own styled
Word file as the template. It works with any template: the tags inside the
template decide which values it needs from the JSON.

## Install

macOS and Linux, one command (no Python needed):

```sh
curl -fsSL https://raw.githubusercontent.com/aliemrenebiler/docile/main/install.sh | sh
```

It downloads the right binary for your machine to `~/.local/bin/docile` and
tells you if that folder needs to be added to your `PATH`. Check it with:

```sh
docile --version
```

## Commands

```sh
docile -h                # list the commands
docile <command> -h      # options of one command
docile update            # update Docile to the latest release
docile update --check    # only check if there is a newer release
docile uninstall         # remove Docile from this computer
```

### examples

Copies the example files (see [Files](#files)) so you can try Docile or use
them as a starting point.

```sh
docile examples                  # into the current folder
docile examples -d my-cv         # into another folder (-d / --dir)
```

Files that already exist are skipped, never overwritten.

### render

Fills a template with the data from a JSON file and saves a `.docx`.

```sh
docile render <json-file> <template-docx-file>
docile render <json-file> <template-docx-file> -o <output-docx-file>
docile render <json-file> <template-docx-file> -s <schema-json-file>
docile render <json-file> <template-docx-file> -o <output-docx-file> -y
```

- `<json-file>` and `<template-docx-file>` are required.
- `-o` / `--output` is the file to write. Default: `docile_<date>_<time>.docx`
  in the current folder. If it is an existing folder, the file is created in it
  with the default name.
- If the output file already exists, Docile asks `Overwrite? [y/N]` and writes
  nothing unless you answer `y`. Add `-y` / `--yes` to overwrite without asking
  (needed when there is no terminal to answer, like in a script).
- `-s` / `--schema` checks the JSON against a schema first. If it does not
  match, every problem is listed and no file is written.

The output name can contain date/time tokens in `{{ }}`: `YYYY` `YY` `MMMM`
`MMM` `MM` `dd` `HH` `hh` `mm` `ss` `a`. For example:

```sh
docile render input.json template.docx -o "out/Jane-Doe_CV_{{YYYY}}-{{MM}}-{{dd}}.docx"
```

### mcp

Runs Docile as an MCP server, so Claude Desktop can use it as a tool. You don't
run this yourself: Claude Desktop starts it. See
[Use with Claude Desktop](#use-with-claude-desktop).

### uninstall

Removes the Docile binary (it asks first; `-y` skips the question). Docile keeps
no other files, so nothing else is left behind. If you added Docile to Claude
Desktop, also remove its entry from the config (the same place you added it).

## Files

`docile examples` copies an example of each file below.

### Data

Any JSON object. Its keys are what the template tags refer to, so
`{"name": "Jane"}` fills `{{ name }}`. (`input.example.json`)

- A key the template uses but the JSON lacks renders empty, with a warning.
- A missing parent object (like `contact` for `{{ contact.email }}`) is an error.

### Schema

An optional [JSON Schema](https://json-schema.org) that says what the JSON must
look like (required keys, types). Used with `render -s`. Any file name works.
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

Claude Desktop can't run commands on your computer, but it can use Docile as a
tool through `docile mcp`. Then you can ask Claude to fill a template in plain
language. Claude Desktop starts Docile by itself when it opens and stops it
when it quits, so there is nothing to keep running. These steps are for macOS.

1. **Install Docile** (see [Install](#install)) and run `which docile`. Copy the
   path it prints, for example `/Users/<your-username>/.local/bin/docile`.
   (`<your-username>` is your Mac user name; run `whoami` to see it.)

2. **Add Docile to Claude Desktop.** Go to Settings → Desktop App → Extensions →
   Local MCP Servers and click Edit Config.
   This shows `claude_desktop_config.json` in Finder; open it with any text
   editor and paste this, with your own path from step 1. If the file already has
   `"mcpServers"`, add only the `"docile"` line inside it.

   ```json
   {
     "mcpServers": {
       "docile": { "command": "/Users/<your-username>/.local/bin/docile", "args": ["mcp"] }
     }
   }
   ```

3. **Restart Claude Desktop** completely (Cmd+Q, then open it again). In
   Settings → Desktop App → Extensions → Local MCP Servers, `docile` should be
   listed as running.

4. **Ask Claude.** Give full file paths, because Claude can't see your files
   on its own. For example:

   > Fill `/Users/<your-username>/cv/template.docx` with my details below, check it with
   > `/Users/<your-username>/cv/schema.json`, and save it in `/Users/<your-username>/Documents`.
   > My details: ...

   Claude asks you to allow each tool call the first time.

   The data can be JSON that Claude writes in the chat, or the path of a file on
   your computer. The template and the schema must be files on your computer:
   if Claude made one, download it first and give Claude its path.

If `docile` doesn't show up, check that the config is valid JSON, that the path
is the one from `which docile`, and that you fully restarted Claude Desktop.
The log is at `~/Library/Logs/Claude/mcp-server-docile.log`.
