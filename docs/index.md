---
title: Home
---
# snk

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

Snk is a SnakeMake pipeline management system. Snk allows you to install SnakeMake pipelines as Command Line Interfaces (CLIs). Using a pipeline as a CLI increases its interoperability and allows complex pipelines to be used as modular components in a larger system.

## Basic Use

### Install a pipeline as a CLI

```
snk install snakemake-workflows/rna-seq-star-deseq2
```

### Inspect the CLI   

```
rna-seq-star-deseq2 --help
```
<img width="747" alt="image" src="https://user-images.githubusercontent.com/13726005/213120475-a025e741-c9be-4aaa-ae62-37ed6c39b698.png">


### View the dag  

```
rna-seq-star-deseq2 dag --pdf 
```

### Run the pipeline 

```
rna-seq-star-deseq2 run
```

### Configure 

Snk will dynamically generate config options for the CLI. For example if your config.yaml file has the option `fasta: null` you can set this option with `--fasta`.

```
rna-seq-star-deseq2 run --fasta example.fa
```

You can also configure the pipeline using a config file. 

```
rna-seq-star-deseq2 config # print the config 
rna-seq-star-deseq2 config > config.yml # save the config 
rna-seq-star-deseq2 run --configfile config.yml # run with config 
```

# how it works

When installing a pipeline snk will

- create directory `$PYTHON_BIN_DIR/../snk/pipelines/PIPELINE`
- install the pipeline into this directory
- expose CLI at `$PYTHON_BIN_DIR` that point to pipeline directory in `snk/pipelines/PIPELINE/bin`
- As long as `$PYTHON_BIN_DIR` is on your PATH, you can now invoke the pipeline globally

# hey what about snakedeploy??
yes

## License

`snk` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
