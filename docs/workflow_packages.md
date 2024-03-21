---
title: Workflow Packages
---
# Using Snk CLI to build self contained tools

While `snk` is useful for managing workflows, using snk does add an extra step to typical install processes. Users must first install snk before they can `snk install` your workflow. However, it is possible to build a workflow as a standalone package (relying on `pip` or `conda` to do the installation) and only using `snk` to dynamically generate the CLI. 

Turning a workflow into a package means that you are committing to a different style of project. A good example of this style is [pangolin](https://github.com/cov-lineages/pangolin), a tool for assigning SARS-CoV-2 genome sequences to global lineages. Pangolin has a CLI that wraps serval Snakemake rules. From the user perspective they `conda install pangolin` and then use the CLI `pangolin <query>` to run the tool. Pangolin abstracts away the execution of the Snakemake workflow. Using the snk CLI class can do the same except by using snk you don't have to build the Snakemake wrapper. 

!!! info

    All the code from this guide can be found in the repo [snk-workflow-package-example](https://github.com/Wytamma/snk-workflow-package-example)

## Project structure

To start you should structure your workflow as a Python package. When building packages it's useful to use a project manager like [hatch](https://hatch.pypa.io/latest/) or [poetry](https://python-poetry.org/). 

Using hatch we can run `hatch new "Workflow Name" --cli` to scaffold a project. This would create the following structure in your current working directory:

```
workflow-name
├── src
│   └── workflow_name
│       ├── cli
│       │   └── __init__.py
│       ├── __about__.py
│       ├── __init__.py
│       └── __main__.py
├── tests
│   └── __init__.py
├── LICENSE.txt
├── README.md
└── pyproject.toml
```

## Configuration

The `pyproject.toml` file is used to configure the project metadata, dependencies, environments, etc. (see https://hatch.pypa.io/latest/config/metadata/ for details). Replace the default dependency of `click` with `snk` e.g.

```toml
dependencies = [
  "snk",
]
```

The `[project.scripts]` section in the `pyproject.toml` file is used to define the entry point for our tool (the CLI). 

```
[project.scripts]
workflow-name = "workflow_name.cli:workflow_name"
```

Modify the the default hatch CLI to the dynamic CLI generated with snk by replacing the contents of `src/workflow_name/cli/__init__.py` with the following:

```python
from pathlib import Path

from snk.cli import CLI

workflow_name = CLI(Path(__file__).parent.parent)
```

!!! note
    
    Remember to replace `workflow_name` with the name of your tool

## Adding the workflow 

All that's left to do it add the Snakemake workflow. The simplest way to do this is to add a `Snakefile` and `config`. Here we add a simple workflow that saves a message to a file. 

```python
# src/workflow_name/workflow/Snakefile
configfile: "config.yaml"

rule hello_world:
    output: config['output']
    params:
        text=config['text']
    shell: "echo {params.text} > {output}"
```

```yaml
# src/workflow_name/config.yaml
text: "hello world!"
output: "message.txt"
```

Resulting in the following project structure:

```
workflow-name
├── LICENSE.txt
├── README.md
├── pyproject.toml
├── src
│   └── workflow_name
│       ├── __about__.py
│       ├── __init__.py
│       ├── __main__.py
│       ├── cli
│       │   └── __init__.py
│       ├── config.yaml <-
│       └── workflow
│           └── Snakefile <-
└── tests
    └── __init__.py
```

Activate the hatch env with `hatch shell` (this will install the workflow in development mode).

You can now test the workflow is working with `workflow-name -h` which should return the following:

```
 Usage: workflow-name [OPTIONS] COMMAND [ARGS]...                           
                                                                            
        _             _  _                                                  
  _ __ (_) _ __  ___ | |(_) _ _   ___       _ _   __ _  _ __   ___          
 | '_ \| || '_ \/ -_)| || || ' \ / -_)     | ' \ / _` || '  \ / -_)         
 | .__/|_|| .__/\___||_||_||_||_|\___| ___ |_||_|\__,_||_|_|_|\___|         
 |_|      |_|                         |___|                                 
 A Snakemake workflow CLI generated with snk                                
                                                                            
╭─ Options ────────────────────────────────────────────────────────────────╮
│ --version             -v        Show the workflow version.               │
│ --path                -p        Show the workflow path.                  │
│ --install-completion            Install completion for the current       │
│                                 shell.                                   │
│ --show-completion               Show completion for the current shell,   │
│                                 to copy it or customize the              │
│                                 installation.                            │
│ --help                -h        Show this message and exit.              │
╰──────────────────────────────────────────────────────────────────────────╯
╭─ Commands ───────────────────────────────────────────────────────────────╮
│ config     Access the workflow configuration.                            │
│ env        Access the workflow conda environments.                       │
│ info       Display information about current workflow install.           │
│ profile    Access the workflow profiles.                                 │
│ run        Run the dynamically generated workflow CLI.                   │
╰──────────────────────────────────────────────────────────────────────────╯
```

Run the workflow with `workflow-name run --text "Hello from Snakemake"`

```
       _             _  _                                         
 _ __ (_) _ __  ___ | |(_) _ _   ___       _ _   __ _  _ __   ___ 
| '_ \| || '_ \/ -_)| || || ' \ / -_)     | ' \ / _` || '  \ / -_)
| .__/|_|| .__/\___||_||_||_||_|\___| ___ |_||_|\__,_||_|_|_|\___|
|_|      |_|                         |___|                        
A Snakemake workflow CLI generated with snk

Building DAG of jobs...
Using shell: /bin/bash
Provided cores: 8
Rules claiming more threads will be scaled down.
Job stats:
job            count    min threads    max threads
-----------  -------  -------------  -------------
hello_world        1              1              1
total              1              1              1

Select jobs to execute...

[Wed May 31 14:21:44 2023]
rule hello_world:
    output: message.txt
    jobid: 0
    reason: Missing output files: message.txt
    resources: tmpdir=/var/folders/hs/3sl81nqd6mzcbz1sc_td3bv00000gn/T

[Wed May 31 14:21:45 2023]
Finished job 0.
1 of 1 steps (100%) done
Complete log: .snakemake/log/2023-05-31T142144.694274.snakemake.log
```

We can also add a `snk.yaml` file to add annotations to the CLI. See [Snk Config](/snk_config_file/) docs for details.

```
workflow-name
├── LICENSE.txt
├── README.md
├── pyproject.toml
├── src
│   └── workflow_name
│       ├── __about__.py
│       ├── __init__.py
│       ├── __main__.py
│       ├── snk.yaml <-
│       ├── cli
│       │   └── __init__.py
│       ├── config.yaml
│       └── workflow
│           └── Snakefile
└── tests
    └── __init__.py
```

At this point you can delete the `config.yaml` file and use the `snk.yaml` file to specify the parameters for your workflow. The `snk.yaml` file will be used to generate the CLI, and the parameters will be available in the `config` dictionary in your `Snakefile` (just remember to set defaults!).  

```yaml
cli:
  text:
    type: str
    help: "The message to save to the file"
    default: "hello world!"
  output:
    type: path
    help: "The path to save the message to"
    default: "message.txt"
```

## Add additional commands to the workflow

To add commands to the workflow cli you can access the underlying typer app:

```python
from pathlib import Path

from snk.cli import CLI

workflow_name = CLI(workflow_dir_path = Path(__file__).parent.parent)

@workflow_name.app.command()
def hello(name: str):
    print(f"Hello {name}!")
```

You can now access the hello command from the workflow cli e.g.

```bash
❯ workflow-name hello Wytamma
Hello Wytamma!
```

## Publishing the workflow

You can use hatch to build and publish your workflow to PYPI (requires PYPI account).

To build run `hatch build` 
```
❯ hatch build  
[sdist]
dist/workflow_name-0.0.1.tar.gz

[wheel]
dist/workflow_name-0.0.1-py3-none-any.whl
```

To publish run `hatch publish`
```
❯ hatch publish
dist/workflow_name-0.0.1-py3-none-any.whl ... success
dist/workflow_name-0.0.1.tar.gz ... success

[workflow-name]
https://pypi.org/project/workflow-name/0.0.1/
```

The workflow is now on pypi and can be installed with `pip`!

```bash
pip install workflow-name
```

Your workflow is now installed as a CLI package.
```bash
workflow-name -h
```

