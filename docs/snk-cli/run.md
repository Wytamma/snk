# Run the snakemake workflow

The `run` subcommand will run the workflow. 

!!! note

   the snk-basic-pipeline workflow used as an example in this documentation can be found [here](https://github.com/Wytamma/snk-basic-pipeline)

## Setup 

Download the test data

```bash
snk-basic-pipeline script run download_data
```

## Running the workflow

To run the workflow, use the `run` command. This will execute the workflow using Snakemake.

```bash
snk-basic-pipeline run # Run the workflow
```
```
Building DAG of jobs...
Using shell: /bin/bash
Provided cores: 8
Rules claiming more threads will be scaled down.
Job stats:
job                count
---------------  -------
all                    1
call_variants          1
map_reads              3
plot_quals             1
sort_alignments        3
total                  9
```

## Options

The `run` command will pass all unrecognized arguments to Snakemake. That means that if you want to use any of the Snakemake options, you can pass them to the `run` command e.g. `snk-basic-pipeline run --use-singularity`. To see all the options available in Snakemake, you can use the `--help-snakemake` (`-h`) flag. Alternatively, you can prepend `--snake` to the Snakemake option e.g. `snk-basic-pipeline run --snake--use-singularity` to pass the `--use-singularity` option to Snakemake.

!!! note 

   You can permanently set additional Snakemake options by adding them to the `additional_snakemake_args` section of the `snk.yaml` file.

The snk-cli provides several options to configure the workflow.

### Configuration

You can use the `--config` flag to specify a configuration file to override the existing workflow configuration. This is the same as using the `--configfile` flag in Snakemake. 

```bash
snk-basic-pipeline run --config config.yaml
```

### Resources

You can use the `--resource` flag to specify additional resources to copy from the workflow directory at run time. The resources must be specified as a path relative to the workflow directory. The resources will be copied to the working directory before the workflow is executed and removed after the workflow completes (unless the `--keep-resources` flag is used).

```bash
snk-basic-pipeline run --resource data/extra
```

### Profile

You can use the `--profile` flag to specify a profile to use for configuring Snakemake. You can specify the profile by name. The profile must be located in the `profiles` directory of the workflow.

```bash
snk-basic-pipeline run --profile slurm
```

### Generate a workflow graph

You can use the `--dag` flag to save the directed acyclic graph to a file. The output file must end in `.pdf`, `.png`, or `.svg`.

```bash
snk-basic-pipeline run --dag workflow.pdf
```

!!! note

   The `--dag` flag requires the `graphviz` package (`dot`) to be installed.

### Other Options

You can use the `--dry` flag to display what would be done without executing anything (this is the same as using the `--dry-run` flag in Snakemake).

The `--lock` flag is used to lock the working directory (by default, the working directory is not locked e.g. `--nolock` is passed to Snakemake).

The `--cores` flag is used to set the number of cores to use. If `None` is specified, all cores will be used by default.

The `--no-conda` flag is used to disable the use of conda environments.

The `--keep-snakemake` flag is used to keep the `.snakemake` folder after the pipeline completes. This is useful for debugging purposes. By default, the `.snakemake` folder is removed after the pipeline completes.

## Help

The `snk-cli` help message is broken into two sections. The first section lists the options available for the `run` command. The second section lists the workflow configuration options (generated from the snakemake configfile).

```bash
snk-basic-pipeline run --help
```
```
 Usage: snk-basic-pipeline run [OPTIONS]                                 
                                                                         
 Run the workflow.                                                       
 All unrecognized arguments are passed onto Snakemake.                   
                                                                         
╭─ Options ─────────────────────────────────────────────────────────────╮
│ --config                   FILE     Path to snakemake config file.    │
│                                     Overrides existing workflow       │
│                                     configuration.                    │
│                                     [default: None]                   │
│ --resource        -r       PATH     Additional resources to copy from │
│                                     workflow directory at run time.   │
│ --profile         -p       TEXT     Name of profile to use for        │
│                                     configuring Snakemake.            │
│                                     [default: None]                   │
│ --dry             -n                Do not execute anything, and      │
│                                     display what would be done.       │
│ --lock            -l                Lock the working directory.       │
│ --dag             -d       PATH     Save directed acyclic graph to    │
│                                     file. Must end in .pdf, .png or   │
│                                     .svg                              │
│                                     [default: None]                   │
│ --cores           -c       INTEGER  Set the number of cores to use.   │
│                                     If None will use all cores.       │
│                                     [default: None]                   │
│ --no-conda                          Do not use conda environments.    │
│ --keep-resources                    Keep resources after pipeline     │
│                                     completes.                        │
│ --keep-snakemake                    Keep .snakemake folder after      │
│                                     pipeline completes.               │
│ --verbose         -v                Run workflow in verbose mode.     │
│ --help-snakemake  -hs               Print the snakemake help and      │
│                                     exit.                             │
│ --help            -h                Show this message and exit.       │
╰───────────────────────────────────────────────────────────────────────╯
╭─ Workflow Configuration ──────────────────────────────────────────────╮
│ --sample       -s      TEXT  Samples to map to the reference genome.  │
│                              [default: A, B, C]                       │
│ --genome       -g      PATH  Path to the reference genome.            │
│                              [default: data/genome.fa]                │
│ --samples-dir          PATH  Directory of samples.                    │
│                              [default: data/samples]                  │
╰───────────────────────────────────────────────────────────────────────╯
```