# CLI Dictionary Lookup
Simple command line dictionary look up tool

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

Output:

```
Word: pneumonoultramicroscopicsilicovolcanoconiosis
Type: noun
Definition: A disease of the lungs, allegedly caused by inhaling microscopic silicate particles originating from eruption of a volcano.
Example: None
```
