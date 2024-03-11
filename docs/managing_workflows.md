---
title: Managing Workflows
---
# Using Snk to manage workflows

The snk command line interface (CLI) provides several options and commands to manage Snakemake workflows. Here's a detailed breakdown of the usage.

## Installing workflows

The `snk install` command is used to install a workflow. You can specify the path, URL, or GitHub name (user/repo) of the workflow to install. The simplest way to install a workflow is from Github. The [Snakemake workflow catalog](https://snakemake.github.io/snakemake-workflow-catalog/) has an index of Snakemake workflows.

For example we can install snk-basic-pipeline (an example workflow from the Snakemake tutorial) with the following command:

```bash
snk install Wytamma/snk-basic-pipeline
```

By default Snk workflows will be installed (cloned) into a `snk` folder in the parent directory of the python `bin` directory (configurable with `$SNK_HOME` or `--home`). Snk will then create a executable for the workflow at `$SNK_HOME/bin` and symlink the executable to python `bin` directory (configurable with `$SNK_BIN` or `--bin`). 

```
/home/wwirth/.conda/envs/snk/
├── bin ($SNK_BIN)
│   ├── python
│   ├── snk-basic-pipeline -> .../snk/bin/snk-basic-pipeline
│   └── ...
├── lib
│   └── ...
└── snk ($SNK_HOME)
    ├── bin
    │   └── snk-basic-pipeline (symlinked to $SNK_BIN)
    └── workflows
        └── snk-basic-pipeline
            ├── config
            └── workflow
                ├── Snakefile
                ├── envs
                └── ...
```

!!! note

    To globally install a workflow you could run `SNK_BIN=~/.local/bin snk install Wytamma/snk-basic-pipeline` assuming `~/.local/bin` is in you `$PATH` (e.g. `export PATH=$PATH:~/.local/bin` in .bashrc) 

### Local install

To install local workflow simply pass the path to `snk install`. 

```bash
snk install path/to/snakemake/workflow
```

Use the `--editable` flag to install local workflows in editable mode (useful for development). This will symlink the path to the `SNK_HOME` directory so all changes will be reflected in the CLI.

```bash
snk install -e path/to/snakemake/workflow
```

### Install options 

Several options exist to modify the install process. 

Use `--name` to rename the workflow. The new name will be used to call the CLI.
```bash
snk install --name my-workflow Wytamma/snk-basic-pipeline && my-workflow -h
```

Use `--tag` to specify the tag (version) of the workflow to install. You can specify a branch name, or tag. If not specified, the latest commit will be installed.
```bash
snk install --tag v1.0 Wytamma/snk-basic-pipeline && my-workflow -v
```

Use `--commit` to specify the commit (SHA) of the workflow to install. If not specified, the latest commit will be installed.
```bash
snk install --commit a725d3a4 Wytamma/snk-basic-pipeline && snk-basic-pipeline -v
```

Use `--config` to install a workflow with a non-standard config location. This is useful for installing a workflow that does not follow Snakemake best practices. 
```bash
snk install --config /path/to/config Wytamma/snk-basic-pipeline
```

Use `--resource` specify a resource that is required at run time. Resources will be copied to the run directory at runtime. The path should be relative to the workflow directory. 

```bash
snk install --resource path/to/resource Wytamma/snk-basic-pipeline
```

If the the workflow should not use conda environments, use `--no-conda`. This will prevent the workflow from creating a conda environment and will not use the `--use-conda` flag when running the workflow. 
```bash
snk install --no-conda Wytamma/snk-basic-pipeline
```

Installation can be forced with the `--force` flag. This can be used to overwrite existing workflows.
```bash
snk install --force Wytamma/snk-basic-pipeline
```

## Listing workflows

The `snk list` command is used to view the installed workflows. 

```bash
snk list
```
```
┏━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━┓
┃ Workflow              ┃ Version  ┃
┡━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━┩
│ snk-basic-pipeline    │ 3445c7cd │
├───────────────────────┼──────────┤
│ variant-calling       │ v2.1.1   │
├───────────────────────┼──────────┤
│ workflow              │ editable │
└───────────────────────┴──────────┘
```

!!! note 
    
    Use `--verbose` (`-v`) to show workflow installation paths.

## Uninstall workflows

The `snk uninstall` command is used to uninstall workflows. You must pass uninstall the `name` of the workflow (e.g. only the `repo` part of `user`/`repo` if installed from Github). 

```bash
snk uninstall workflow
```
```
Uninstalling workflow
  Would remove:
    <SNK_HOME>/workflows/workflow/*
    <SNK_BIN>/workflow
Proceed (Y/n)? y
```

!!! Note
    Use `--force` to force uninstall without asking.

## Ejecting workflows

The `cp -r $(workflow-name -p) workflow-name` command is used to eject the workflow from the package. This will copy the workflow files to the current working directory. This will allow you to modify the workflow and run it with the standard `snakemake` command.

Following modification of the workflow you can run `snk install ./workflow-name --force` to install the updated workflow.
