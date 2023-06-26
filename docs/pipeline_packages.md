---
title: Pipeline Packages
---
# Using Snk CLI to build self contained tools

While `snk` is useful for managing pipelines, using snk does add an extra step to typical install processes. User must first install snk before they can `snk install` your pipeline. However, it is possible to build a pipeline as a standalone package (relying on `pip` or `conda` to do the installation) and only using `snk` to dynamically generate the CLI. 

Turning a pipeline into a package means that you are committing to a different style of project. A good example of this style is [pangolin](https://github.com/cov-lineages/pangolin), a tool for assigning SARS-CoV-2 genome sequences to global lineages. Pangolin has a CLI that wraps serval Snakemake rules. From the user perspective they `conda install pangolin` and then use the CLI `pangolin <query>` to run the tool. Pangolin abstracts away the execution of the Snakemake pipeline. Using the snk CLI class can do the same except by using snk you don't have to build the Snakemake wrapper. 

!!! info

    All the code from this guide can be found in the repo [snk-pipeline-package-example](https://github.com/Wytamma/snk-pipeline-package-example)

## Project structure

To start you should structure your pipeline as a Python package. When building packages it's useful to use a project manager like [hatch](https://hatch.pypa.io/latest/) or [poetry](https://python-poetry.org/). 

Using hatch we can run `hatch new "Pipeline Name" --cli` to scaffold a project. This would create the following structure in your current working directory:

```
pipeline-name
├── src
│   └── pipeline_name
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
pipeline-name = "pipeline_name.cli:pipeline_name"
```

Modify the the default hatch CLI to the dynamic CLI generated with snk by replacing the contents of `src/pipeline_name/cli/__init__.py` with the following:

```python
from pathlib import Path

from snk.cli import CLI

pipeline_name = CLI(pipeline_dir_path = Path(__file__).parent.parent)
```

!!! note
    
    Remember to replace `pipeline_name` with the name of your tool

## Adding the pipeline 

All that's left to do it add the Snakemake pipeline. The simplest way to do this is to add a `Snakefile` and `config`. Here we add a simple pipeline that saves a message to a file. 

```python
# src/pipeline_name/workflow/Snakefile
configfile: "config.yaml"

rule hello_world:
    output: config['output']
    params:
        text=config['text']
    shell: "echo {params.text} > {output}"
```

```yaml
# src/pipeline_name/config.yaml
text: "hello world!"
output: "message.txt"
```

Resulting in the following project structure:

```
pipeline-name
├── LICENSE.txt
├── README.md
├── pyproject.toml
├── src
│   └── pipeline_name
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

Activate the hatch env with `hatch shell` (this will install the pipeline in development mode).

You can now test the pipeline is working with `pipeline-name -h` which should return the following:

```
 Usage: pipeline-name [OPTIONS] COMMAND [ARGS]...                           
                                                                            
        _             _  _                                                  
  _ __ (_) _ __  ___ | |(_) _ _   ___       _ _   __ _  _ __   ___          
 | '_ \| || '_ \/ -_)| || || ' \ / -_)     | ' \ / _` || '  \ / -_)         
 | .__/|_|| .__/\___||_||_||_||_|\___| ___ |_||_|\__,_||_|_|_|\___|         
 |_|      |_|                         |___|                                 
 A Snakemake pipeline CLI generated with snk                                
                                                                            
╭─ Options ────────────────────────────────────────────────────────────────╮
│ --version             -v        Show the pipeline version.               │
│ --path                -p        Show the pipeline path.                  │
│ --install-completion            Install completion for the current       │
│                                 shell.                                   │
│ --show-completion               Show completion for the current shell,   │
│                                 to copy it or customize the              │
│                                 installation.                            │
│ --help                -h        Show this message and exit.              │
╰──────────────────────────────────────────────────────────────────────────╯
╭─ Commands ───────────────────────────────────────────────────────────────╮
│ config     Access the pipeline configuration.                            │
│ env        Access the pipeline conda environments.                       │
│ info       Display information about current pipeline install.           │
│ profile    Access the pipeline profiles.                                 │
│ run        Run the dynamically generated pipeline CLI.                   │
╰──────────────────────────────────────────────────────────────────────────╯
```

Run the pipeline with `pipeline-name run --text "Hello from Snakemake"`

```
       _             _  _                                         
 _ __ (_) _ __  ___ | |(_) _ _   ___       _ _   __ _  _ __   ___ 
| '_ \| || '_ \/ -_)| || || ' \ / -_)     | ' \ / _` || '  \ / -_)
| .__/|_|| .__/\___||_||_||_||_|\___| ___ |_||_|\__,_||_|_|_|\___|
|_|      |_|                         |___|                        
A Snakemake pipeline CLI generated with snk

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
pipeline-name
├── LICENSE.txt
├── README.md
├── pyproject.toml
├── src
│   └── pipeline_name
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

## Publishing the pipeline

You can use hatch to build and publish your pipeline to PYPI (requires PYPI account).

To build run `hatch build` 
```
❯ hatch build  
[sdist]
dist/pipeline_name-0.0.1.tar.gz

[wheel]
dist/pipeline_name-0.0.1-py3-none-any.whl
```

To publish run `hatch publish`
```
❯ hatch publish
dist/pipeline_name-0.0.1-py3-none-any.whl ... success
dist/pipeline_name-0.0.1.tar.gz ... success

[pipeline-name]
https://pypi.org/project/pipeline-name/0.0.1/
```

The pipeline is now on pypi and can be installed with `pip`!

```bash
pip install pipeline-name
```

Your pipeline is now installed as a CLI package.
```bash
pipeline-name -h
```

