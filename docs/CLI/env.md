---
title: ENV
---

# The CLI ENV command 

The `env` subcommand in the `pipeline` tool allows you to access and manage the conda environments used within the pipeline. This guide provides an overview of the available options and commands for working with pipeline environments.

## Options

- `--help`, `-h`: Show the help message and exit.

## Commands

The `env` subcommand provides several commands to manage the pipelines conda environments.

### `activate`

Activate a pipeline conda environment.

```bash
pipeline env activate [OPTIONS] ENV_NAME
```

- `ENV_NAME`: Name of the environment to activate.

This command activates the specified conda environment within the pipeline.

### `create`

Create all conda environments.

```bash
pipeline env create [OPTIONS]
```

This command creates all the conda environments specified in the `envs` dir.

### `list`

List the environments in the pipeline.

```bash
pipeline env list [OPTIONS]
```

This command lists all the conda environments present in the pipeline.

### `prune`

Delete all conda environments.

```bash
pipeline env prune [OPTIONS]
```

This command deletes all the conda environments in the pipeline.

### `run`

The `env run` command in the `pipeline` tool allows you to run a command within one of the pipeline environments. This guide provides an overview of the available options and arguments for the `env run` command.

#### Arguments

- `cmd`: The command to run in the environment. This argument is required.

#### Options

- `--env`, `-e`: The name of the environment in which to run the command. This option is required.
- `--help`, `-h`: Show the help message and exit.

#### Usage

To run a command in one of the pipeline environments, use the following command format:

```bash
pipeline env run --env ENV_NAME CMD...
```

- `CMD...`: The command and its arguments to execute within the specified environment.

Make sure to replace `ENV_NAME` with the actual name of the desired environment, and `CMD...` with the command you want to run.

#### Example

Here's an example command that demonstrates the usage of `pipeline env run`:

```bash
pipeline env run -e my_environment "python script.py --input input_file.txt --output output_file.txt"
```

This command runs the `python script.py --input input_file.txt --output output_file.txt` command within the `my_environment` environment in the pipeline. Adjust the command and environment name according to your specific use case.


- `ENV_NAME`: Name of the environment in which to run the command.
- `COMMAND [ARGS]...`: The command and its arguments to execute within the specified environment.

This command runs the provided command within the specified conda environment in the pipeline.

### `show`

Show the environments config file contents.

```bash
pipeline env show [OPTIONS]
```

This command displays the contents of the environments configuration file used in the pipeline.