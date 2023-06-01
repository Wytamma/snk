# SNK (Snek)

[![PyPI - Version](https://img.shields.io/pypi/v/snk.svg)](https://pypi.org/project/snk)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/snk.svg)](https://pypi.org/project/snk)
[![write-the - docs](https://badgen.net/badge/write-the/docs/blue?icon=https://raw.githubusercontent.com/Wytamma/write-the/master/images/write-the-icon.svg)](https://write-the.wytamma.com/)
[![Hits](https://hits.seeyoufarm.com/api/count/incr/badge.svg?url=https%3A%2F%2Fgithub.com%2FWytamma%2Fsnk&count_bg=%2379C83D&title_bg=%23555555&icon=&icon_color=%23E7E7E7&title=hits&edge_flat=false)](https://hits.seeyoufarm.com)
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
rna-seq-star-deseq2 run --config config.yml # run with config 
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
