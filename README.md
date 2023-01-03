# snk

[![PyPI - Version](https://img.shields.io/pypi/v/snk.svg)](https://pypi.org/project/snk)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/snk.svg)](https://pypi.org/project/snk)

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

Snk is a SnakeMake pipeline management system. Snk allows you to install SnakeMake pipelines as Command Line Interfaces (CLIs). Using a pipeline as a CLI increases it's interoperability and allows complex pipelines to be used as modular components in a larger system.

https://excalidraw.com/#room=4cb5ad1ed651d8a96369,xM0iaXAGVFNiNJOuILncPg

## Basic Use

Install a pipeline as a CLI

```
snk install https://github.com/snakemake-workflows/rna-seq-star-deseq2
```

Inspect the CLI   

```
rna-seq-star-deseq2 --help
```

View the dag  

```
rna-seq-star-deseq2 dag --pdf 
```

Run the pipeline 

```
rna-seq-star-deseq2 run
```

Configure 

```
rna-seq-star-deseq2 config # print the config 
rna-seq-star-deseq2 config > config.yml # save the config 
rna-seq-star-deseq2 run --config config.yml # run with config 
```

# how it works

When installing a pipeline snk will

- create directory ~/.local/snk/pipelines/PIPELINE
- install the pipeline into this directory
- expose CLI at ~/.local/bin that point to pipeline directory in ~/.local/snk/pipelines/PIPELINE/bin 
- As long as ~/.local/bin/ is on your PATH, you can now invoke the pipeline globally

# hey what about snakedeploy??
yes

## License

`snk` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
