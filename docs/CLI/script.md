---
title: Scripts
---

# Script Commands

The `script` commands allow you to interact with the workflow scripts. Scripts must be located in the `scripts` directory of the workflow.

## List

The list command will list all scripts in the workflow.

```bash
snk script list
```

## Show

The show command will display the contents of a script.

```bash
snk script show hello.py
```

## Run

The run command will run a script.

```bash
snk script run hello.py
```

!!! note
    The executor used to run the script is determined by the suffix of the script file. For example, a script named `hello.py` will be run using the `python` executor.

Use the `--env` option to specify the environment to run the script in.

```bash
snk script run --env python hello.py
```

