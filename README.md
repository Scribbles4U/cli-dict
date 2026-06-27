# CLI Dictionary Lookup
Simple command line dictionary lookup tool.

#### Installation:
Setup alias to main (replacing <PATHTOREPO> with actual path) in your .bashrc or .zshrc:

```
alias def="<PATHTOREPO>/main.py"
```

Use updated config in current terminal session:

```
. .zshrc
```

Install requirements (setup a virtual env if desired):

```
pip install -r requirements.txt
```

#### Usage:

Lookup words:

```
def pneumonoultramicroscopicsilicovolcanoconiosis
```

Default output uses Rich formatting with color, bold headings, a bordered panel, and a table. Use `--plain` or `--no-color` for scripts and terminals where styling is unwanted.

Plain output:

```
def pneumonoultramicroscopicsilicovolcanoconiosis --plain
```

```
Word: pneumonoultramicroscopicsilicovolcanoconiosis

[1] noun
Definition: A disease of the lungs, allegedly caused by inhaling microscopic silicate particles originating from eruption of a volcano.
```

Show every returned definition:

```
def test --all
```

Return normalized JSON for scripts:

```
def test --json --all
```
