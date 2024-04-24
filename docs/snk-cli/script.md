---
title: Script
---

# Access the workflow scripts

The `script` commands allow you to interact with the workflow scripts. Scripts must be located in the `scripts` directory of the workflow.

## List

The list command will list all scripts in the workflow.

```bash
snk-basic-pipeline script list
```

## Show

The show command will display the contents of a script.

```bash
snk-basic-pipeline script show hello.py
```

## Run

The run command will run a script.

```bash
snk-basic-pipeline script run hello.py
```

!!! note
    The executor used to run the script is determined by the suffix of the script file. For example, a script named `hello.py` will be run using the `python` executor.

Use the `--env` option to specify the environment to run the script in.

```bash
snk-basic-pipeline script run --env python hello.py
```

