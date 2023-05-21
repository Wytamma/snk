---
title: Managing Pipelines
---
# Using Snk to manage pipelines

The snk command line interface (CLI) provides several options and commands to manage Snakemake pipelines. Here's a detailed breakdown of the usage.

## Installing pipelines

The `snk install` command is used to install a pipeline. You can specify the path, URL, or GitHub name (user/repo) of the pipeline to install. The simplest way to install a pipeline is from Github. The [Snakemake workflow catalog](https://snakemake.github.io/snakemake-workflow-catalog/) has an index of Snakemake pipelines.

For example we can install snk-basic-pipeline (an example pipeline from the Snakemake tutorial) with the following command:

```bash
snk install Wytamma/snk-basic-pipeline
```

By default Snk pipelines will be installed (cloned) into a `snk` folder in the parent directory of the python `bin` directory (configurable with `$SNK_HOME` or `--home`). Snk will then create a executable for the pipeline at `$SNK_HOME/bin` and symlink the executable to python `bin` directory (configurable with `$SNK_BIN` or `--bin`). 

```
/home/wwirth/.conda/envs/snk/
├── bin ($SNK_BIN)
│   ├── python
│   ├── snk-basic-pipeline -> .../snk/pipelines/snk-basic-pipeline/bin/snk-basic-pipeline
│   └── ...
├── lib
│   └── ...
└── snk ($SNK_HOME)
    └── pipelines
        └── snk-basic-pipeline
            ├── bin
            │   └── snk-basic-pipeline (symlinked to $SNK_BIN)
            ├── config
            └── workflow
                ├── envs
                └── scripts
```

!!! note

    To globally install a pipeline you could run `SNK_BIN=~/.local/bin snk install Wytamma/snk-basic-pipeline` assuming `~/.local/bin` is in you `$PATH` (e.g. `export PATH=$PATH:~/.local/bin` in .bashrc) 

### Local install

To install local pipeline simply pass the path to `snk install`. 

```bash
snk install path/to/snakemake/pipeline
```

Use the `--editable` flag to install local pipelines in editable mode (useful for development). This will symlink the path to the `SNK_HOME` directory so all changes will be reflected in the CLI.

```bash
snk install -e path/to/snakemake/pipeline
```

### Install options 

Several options exist to modify the install process. 

Use `--name` to rename the pipeline. The new name will be used to call the CLI.
```bash
snk install --name my-pipeline Wytamma/snk-basic-pipeline && my-pipeline -h
```

Use `--tag` to specify the tag (version) of the pipeline to install. You can specify a branch name, or tag. If not specified, the latest commit will be installed.
```bash
snk install --tag v1.0 Wytamma/snk-basic-pipeline && my-pipeline -v
```

Use `--config` to install a pipeline with a non-standard config location. This is useful for installing a pipeline that does not follow Snakemake best practices. 
```bash
snk install --config /path/to/config Wytamma/snk-basic-pipeline
```

Use `--resource` specify a resource that is required at run time. Resources will be copied to the run directory at runtime. The path should be relative to the pipeline directory. 

```bash
snk install --resource path/to/resource Wytamma/snk-basic-pipeline
```

Installation can be forced with the `--force` flag. This can be used to overwrite existing pipelines.
```bash
snk install --force Wytamma/snk-basic-pipeline
```

## Listing pipelines

The `snk list` command is used to view the installed pipelines. 

```bash
snk list
```
```
Found 1 pipelines in <SNK_HOME>/pipelines
- pipeline (latest)
```

## Uninstall pipelines

The `snk uninstall` command is used to uninstall pipelines. You must pass uninstall the `name` of the pipeline (e.g. only the `repo` part of `user`/`repo` if installed from Github). 

```bash
snk uninstall pipeline
```
```
Uninstalling pipeline
  Would remove:
    <SNK_HOME>/pipelines/pipeline/*
    <SNK_BIN>/pipeline
Proceed (Y/n)? y
```

!!! Note
    Use `--force` to force uninstall without asking.