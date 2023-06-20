---
title: Home
---
# SNK (Snek)

[![PyPI - Version](https://img.shields.io/pypi/v/snk.svg)](https://pypi.org/project/snk)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/snk.svg)](https://pypi.org/project/snk)
[![write-the - docs](https://badgen.net/badge/write-the/docs/blue?icon=https://raw.githubusercontent.com/Wytamma/write-the/master/images/write-the-icon.svg)](https://write-the.wytamma.com/)
[![Hits](https://hits.seeyoufarm.com/api/count/incr/badge.svg?url=https%3A%2F%2Fgithub.com%2FWytamma%2Fsnk&count_bg=%2379C83D&title_bg=%23555555&icon=&icon_color=%23E7E7E7&title=hits&edge_flat=false)](https://github.com/Wytamma/snk)

---

**Documentation**: <a href="https://snk.wytamma.com" target="_blank">https://snk.wytamma.com</a>

**Source Code**: <a href="https://github.com/Wytamma/snk" target="_blank">https://github.com/Wytamma/snk</a>

---

Snk (pronounced snek) is a SNaKemake pipeline management system. Snk allows you to install Snakemake pipelines as dynamically generated Command Line Interfaces (CLIs). Using a pipeline as a CLI increases its interoperability and allows complex pipelines to be used as modular components in a larger system.

## Installation

```console
pip install snk
```

## Basic Use

### Install a pipeline as a CLI

Install the dna-seq-gatk-variant-calling pipeline (v2.1.1) as `variant-calling`.

```
snk install snakemake-workflows/dna-seq-gatk-variant-calling --name variant-calling -t v2.1.1
```
Successfully installed variant-calling (v2.1.1)!

### Inspect the CLI   

```
variant-calling --help
```
<img width="862" alt="main cli" src="https://github.com/Wytamma/snk/assets/13726005/bb3997c5-9ee6-465d-8f79-c94067ce9997">

### View run options

```
variant-calling run -h
```
<img width="862" alt="run cli" src="https://github.com/Wytamma/snk/assets/13726005/34c40a7c-72c2-4245-9589-7c3c8982be08">


### Create a DAG

Here we use the `.test` resources included in the pipeline to create the DAG.

```
variant-calling run -r .test/config -r .test/data --dag dag.pdf
```
<img width="862" alt="dag" src="https://github.com/Wytamma/snk/assets/13726005/f79bcfd3-f6cd-401e-b5d8-904e7d5f1835">


### Configure 

Snk will dynamically generate config options for the CLI. For example if your config.yaml file has the option `fasta: null` you can set this option with `--fasta`.

```
variant-calling run --fasta example.fa
```

You can also configure the pipeline using a config file. 

```
variant-calling config --pretty # print the config 
variant-calling config > config.yml # save the config 
variant-calling run --config config.yml # run with config 
```

## how it works

When installing a pipeline snk will

- create directory `$PYTHON_BIN_DIR/../snk/pipelines/PIPELINE`
- install the pipeline into this directory
- expose CLI at `$PYTHON_BIN_DIR` that point to pipeline directory in `snk/pipelines/PIPELINE/bin`
- As long as `$PYTHON_BIN_DIR` is on your PATH, you can now invoke the pipeline globally


## License

`snk` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
