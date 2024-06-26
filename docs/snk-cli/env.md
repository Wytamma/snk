---
title: Env
---

# Access the workflow conda environments

The `env` subcommand in the `workflow` tool allows you to access and manage the conda environments used within the workflow. This guide provides an overview of the available options and commands for working with workflow environments.

## Options

- `--help`, `-h`: Show the help message and exit.

## Commands

The `env` subcommand provides several commands to manage the workflows conda environments.

### `list`

List the environments in the workflow.

```bash
snk-basic-pipeline env list [OPTIONS]
```

### `activate`

Activate a workflow conda environment.

```bash
snk-basic-pipeline env activate [OPTIONS] ENV_NAME
```

- `ENV_NAME`: Name of the environment to activate.

This command activates the specified conda environment within the workflow.

### `create`

This command creates all the conda environments specified in the `envs` dir. Individual conda envs can be create with `workflow env create ENV_NAME`.

Snakemake workflows that use a lot of conda environments can take a long time to install as each env is created sequentially. Running `workflow env create --workers number_of_workers` will create all the conda envs in parallel up to the `number of workers` requested (defaults to 1).

```bash
snk-basic-pipeline env create --workers 4  # create up to 4 conda envs at a time
```

!!! warning

    Some conda envs may not support parallel creation. If you encounter an error, try reducing the number of workers.


### `remove`

Delete conda environments.

```bash
snk-basic-pipeline env remove [OPTIONS] [ENV_NAME...]
```

This command deletes all the conda environments in the workflow. You can also delete individual environments by specifying the environment name. Use the `--force` option to skip the confirmation prompt.

### `run`

The `env run` command in the `workflow` tool allows you to run a command within one of the workflow environments.

#### Arguments

- `cmd`: The command to run in the environment. This argument is required.

#### Options

- `--env`, `-e`: The name of the environment in which to run the command.
- `--help`, `-h`: Show the help message and exit.

#### Usage

To run a command in one of the workflow environments, use the following command format:

```bash
snk-basic-pipeline env run --env ENV_NAME CMD...
```

- `CMD...`: The command and its arguments to execute within the specified environment.

Make sure to replace `ENV_NAME` with the actual name of the desired environment, and `CMD...` with the command you want to run.

#### Example

Here's an example command that demonstrates the usage of `workflow env run`:

```bash
snk-basic-pipeline env run -e my_environment "python script.py --input input_file.txt --output output_file.txt"
```

This command runs the `python script.py --input input_file.txt --output output_file.txt` command within the `my_environment` environment in the workflow. Adjust the command and environment name according to your specific use case.


- `ENV_NAME`: Name of the environment in which to run the command.
- `COMMAND [ARGS]...`: The command and its arguments to execute within the specified environment.

This command runs the provided command within the specified conda environment in the workflow.

### `show`

Show the environments config file contents.

```bash
snk-basic-pipeline env show [OPTIONS]
```

This command displays the contents of the environments configuration file used in the workflow.
