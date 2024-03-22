# Snk

[![PyPI - Version](https://img.shields.io/pypi/v/snk.svg)](https://pypi.org/project/snk)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/snk.svg)](https://pypi.org/project/snk)
[![write-the - docs](https://badgen.net/badge/write-the/docs/blue?icon=https://raw.githubusercontent.com/Wytamma/write-the/master/images/write-the-icon.svg)](https://write-the.wytamma.com/)
[![Hits](https://hits.seeyoufarm.com/api/count/incr/badge.svg?url=https%3A%2F%2Fgithub.com%2FWytamma%2Fsnk&count_bg=%2379C83D&title_bg=%23555555&icon=&icon_color=%23E7E7E7&title=hits&edge_flat=false)](https://github.com/Wytamma/snk)

---

**Documentation**: <a href="https://snk.wytamma.com" target="_blank">https://snk.wytamma.com</a>

**Source Code**: <a href="https://github.com/Wytamma/snk" target="_blank">https://github.com/Wytamma/snk</a>

---

Snk (pronounced snek) is a Snakemake workflow management system. Snk allows you to install Snakemake workflows as dynamically generated Command Line Interfaces (via [snk-cli](https://github.com/Wytamma/snk-cli)). Using a workflow as a CLI increases its interoperability and allows complex workflows to be used as modular components in a larger system.

## Installation

```console
pip install snk
```

## Basic Use

### Install a workflow as a CLI

The snk install command can be use to install Snakemake workflows as CLIs. Snk can install Snakemake workflows from GitHub repos or local paths. An index of publicly available Snakemake workflows can be found on the [snakemake workflow catalog](https://snakemake.github.io/snakemake-workflow-catalog/).

Install the [dna-seq-gatk-variant-calling](https://github.com/snakemake-workflows/dna-seq-gatk-variant-calling) workflow (v2.1.1) as `variant-calling`.

```
snk install snakemake-workflows/dna-seq-gatk-variant-calling --name variant-calling -t v2.1.1
```
Successfully installed variant-calling (v2.1.1)!

### Inspect the CLI   

Snk will automatically create a fully featured CLI for the Snakemake workflow using [snk-cli](https://github.com/Wytamma/snk-cli). 

```
variant-calling --help
```
<img width="862" alt="cli help" src="https://github.com/Wytamma/snk/assets/13726005/3e6e4134-efe5-47e1-b6f4-81b60e1c9ea7">


### View run options

Workflow configuration options are automatically generated from the snakemake config file.

```
variant-calling run --help
```
<img width="862" alt="run cli help" src="https://github.com/Wytamma/snk/assets/13726005/ef1dd9ca-1ba2-4a77-921a-4de16dd57631">


### Create a DAG

Here we use the `.test` resources included in the workflow to create the DAG.

```bash
variant-calling run -r .test/config -r .test/data --dag dag.pdf
```
<img width="862" alt="run cli help" src="https://github.com/Wytamma/snk/assets/13726005/0c25886c-0ab1-49ad-9fdd-315827dcaeb8">

### Configure 

Snk will dynamically generate config options for the CLI. For example if the config.yaml file has the option `fasta: null` you can set this option with `--fasta`.

```bash
variant-calling run --fasta example.fa
```

You can also configure the workflow using a config file. 

```bash
variant-calling config --pretty # print the config 
variant-calling config > config.yml # save the config 
variant-calling run --config config.yml # run with config 
```

### Manage Installed Workflows

You can list installed workflows with `snk list` and uninstall them with `snk uninstall`.

```bash
snk list
```
| Workflow | Version | 
| --- | --- |
| variant-calling | v2.1.1 | 

```bash
snk uninstall variant-calling
```
Successfully uninstalled variant-calling!

## Documentation

Read the [documentation](https://snk.wytamma.com) for more information.

## License

`snk` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
