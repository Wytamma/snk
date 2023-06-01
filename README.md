# SNK (Snek)

[![PyPI - Version](https://img.shields.io/pypi/v/snk.svg)](https://pypi.org/project/snk)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/snk.svg)](https://pypi.org/project/snk)
[![write-the - docs](https://badgen.net/badge/write-the/docs/blue?icon=https://raw.githubusercontent.com/Wytamma/write-the/master/images/write-the-icon.svg)](https://write-the.wytamma.com/)
-----

**Table of Contents**

- [Installation](#installation)
- [About](#about)
- [License](#license)

## Installation

```console
pip install snk
```

## About

Snk (pronounced snek) is a SNaKemake pipeline management system. Snk allows you to install Snakemake pipelines as Command Line Interfaces (CLIs). Using a pipeline as a CLI increases its interoperability and allows complex pipelines to be used as modular components in a larger system. Snk, using python magic, will dynamic genrate the pipeline CLI using the pipeline configuration file.

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
<img width="747" alt="image" src="https://user-images.githubusercontent.com/13726005/213120475-a025e741-c9be-4aaa-ae62-37ed6c39b698.png">

### View run options

```
variant-calling run -h
```

### Create a DAG

Here we use the .test resources included in the pipeline to ge teh 

```
variant-calling run -r .test/config -r .test/data --dag dag.pdf
```

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
