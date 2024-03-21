---
title: Snk Config File
---

# Snk Configuration File

The `snk.yaml` file serves as the main interface for configuring the Snk workflow CLI. Users can tailor the workflow's settings, specify required resources, and control the appearance of the command line interface by setting various options in the `snk.yaml` file.

## Available Configuration Options

The following options are available for configuration in `snk.yaml`:

- `logo`: The text used to dynamically generate the ASCII art displayed in the CLI. Default: `<name-of-workflow>`.
- `art`: A string representing ASCII art to display in the CLI (overwrites `logo`). Default: `null`.
- `tagline`: A string representing the tagline displayed in the CLI. Default: `"A Snakemake workflow CLI generated with Snk"`.
- `font`: A string representing the font used in the CLI (see [FontList](https://www.ascii-art.site/FontList.html)). Default: `"small"`.
- `resources`: A list of resource files required for the workflow. Default: `[]`.
- `cli`: Annotations for the workflow cli parameters (see [CLI section](https://snk.wytamma.com/snk_config_file/#cli) below.
- `symlink_resources`: A boolean that controls whether symbolic links are created for resources (avoid using this unless you know). Default: `False`.
- `conda`: A boolean that controls whether the workflow should use conda. The `--use-conda` flag will only be passed to snakemake if conda is True and the `conda` command is available. Default: `True`.
- `additional_snakemake_args`: A list of additional arguments to pass to snakemake. Default: `[]`.
- `skip_missing`: skip any missing cli options (i.e. those in config but not in the snk file). Default: `False`.

## Example `snk.yaml` File

Below is an example of a `snk.yaml` file illustrating all available options:

```yaml
logo: "MyWorkflow"
font: "cybermedium"
art: |
  _______  _______  _______  _______ 
 (  ____ \(  ___  )(       )(  ____ \
 | (    \/| (   ) || () () || (    \/
 | (__    | (___) || || || || (_____ 
 |  __)   |  ___  || |(_)| |(_____  )
 | (      | (   ) || |   | |      ) |
 | (____/\| )   ( || )   ( |/\____) |
 (_______/|/     \||/     \|\_______)
tagline: "A comprehensive Snakemake workflow configured with snk.yaml"
resources:
  - "data/input1.txt"
  - "data/input2.txt"
symlink_resources: False
conda: True
additional_snakemake_args:
  - "--reason"
skip_missing: True
cli:
  input:
    type: Path
    help: "Path to the input file"
    required: True
  output:
    type: Path
    help: "Path to the output directory"
    required: True
```

In this example:

- The workflow `logo` is set to "MyWorkflow".
- The `font` used for the CLI logo is "cybermedium".
- ASCII art is specified directly in the `art` configuration, taking precedence over the logo if both are provided.
- The `tagline` is "A workflow to illustrate the use of snk.yaml". This will be printed in the CLI help under the logo.
- Two resource files, `data/input1.txt` and `data/input2.txt`, are required for the workflow. They will be copied to the working directory at runtime.
- The `conda` flag is enabled (True), indicating that the workflow should utilise Conda environments for executing tasks, provided the conda command is accessible in the system environment.
- Additional Snakemake arguments are specified under `additional_snakemake_args`, including --reason which will display the reasons for rule execution.
- The `skip_missing` option is enabled (True), which means that only config defined in the `snk.yaml` file, will be included in the dynamically generate CLI.
- An annotation is provided for the `input` parameter, which is of type `str` and comes with a help message "Path to the input file".

## CLI

Annotations play a crucial role in configuring the dynamic Snk CLI. They provide metadata about the configuration parameters used in your Snakemake workflow and can dictate how the CLI will prompt users for these parameters. The `snk.yaml` file supports the following fields under `annotations`:

- `type`: Determines the datatype of the configuration parameter. It can be one of the following: `int`, `str`, `path`, `bool`, `list`, `list[str]`, `list[path]`, or `list[int]`.
- `help`: This is a descriptive text that provides users with information or guidance on what the parameter is used for.
- `required`: A boolean value (either `True` or `False`) that indicates whether the parameter is mandatory. If a parameter is marked as `required: True`, the Snk CLI will insist that a user provides a value for it.
- `default`: A default value for the parameter. If a user does not provide a value for the parameter, the Snk CLI will use this default value instead.
- `short`: A short (-) flag to use with the option.

### Example `snk.yaml` File with CLI Annotations

Here's an example of a `snk.yaml` file that includes annotations for several configuration parameters:

```yaml
cli:
  input:
    type: path
    help: "Path to the input file"
    required: True
    short: i
  text:
    default: "Hello, world!"
    type: str
    help: "A string to save to a file"
    required: False
  count:
    type: int
    help: "Number of times to perform the operation"
    required: True
  flag:
    type: bool
    help: "A boolean flag to enable or disable a feature"
    required: False
```

In this example, the `input` and `count` parameters are required, while the `text` and `flag` parameters are optional. the flas `-i` can be used as shorthand for `--input`. The `type` and `help` attributes provide additional information about each parameter, informing the user of the expected datatype and what the parameter is used for, respectively.

## Nested Annotations in the `snk.yaml` File

Your `snk.yaml` annotations must match the structure of your `config.yaml` file. If you have nested options in your `config.yaml` file, you must specify these in the `snk.yaml` file as well. Here's an example of how you might specify nested options in a `snk.yaml` file:

```yaml
cli:
  nested:
    input:
      type: path
      help: "Path to the input file"
  option:
    type: str
    default: "Hello, world!"
```

This will produce the following CLI:

```bash
workflow run --nested-input <input> --option <other_option>
```

The matching `config.yaml` would look like this:

```yaml
nested:
  input: "path/to/input"
option: "Hello, world!"
```

### Using snk.yaml without a config.yaml file

If you don't have a `config.yaml` file, you can still use the `snk.yaml` file to specify the parameters for your workflow. The `snk.yaml` file will be used to generate the CLI, and the parameters will be available in the `config` dictionary in your `Snakefile`. However, you should probably still have a `config.yaml` file to store your config, as this is the standard way to manage configuration in Snakemake workflows (unless you're creating a [workflow package](https://snk.wytamma.com/workflow_packages)).

### Validating Config with the `snk.yaml` File

Snk provides a function that can be use to validate snakemake config using the `snk.yaml` cli annotations. The `validate_config` function will convert values to the correct type if possible. If the value cannot be converted to the correct type, an error will be raised. This can be added to the start of your `Snakefile` to ensure that the config is valid before running the workflow.

```python
try:
  from snk import validate_config
  validate_config(config, snk_yaml)
except ImportError:
  pass
```

To ensure that the workflow will still run in the absence of the `snk` package, you can wrap the import statement in a try/except block.

## Resources

Resources represent files or folders that are essential for the execution of the workflow. They must be present in the workflow's working directory at runtime. The `snk.yaml` configuration file allows you to specify these resources.

When the workflow is invoked with the `run` command, the Snk CLI will ensure that the specified resources are available in the working directory. It accomplishes this by either copying the resource files or creating symbolic links (symlinks) to them. The method used depends on the value of the `symlink_resources` option in the `snk.yaml` file. If `symlink_resources` is set to `true`, symlinks will be used. Otherwise, the files will be copied.

!!! warning

    You should only set `symlink_resources` to `true` if the workflow won't modify these resources. Any modifications to symlinked resources will be system-wide!


Once the workflow has successfully completed, the Snk CLI will clean up the working directory by deleting the copied resources or unlinking the symlinks.

### Example `snk.yaml` File with Resources

Here's an example of how you might specify resources in a `snk.yaml` file:

```yaml
resources:
  - "data/input1.txt"
  - "data/input2.txt"
symlink_resources: true
```

In this example, `data/input1.txt` and `data/input2.txt` are listed as required resources for the workflow. The `symlink_resources` option is set to `true`, meaning that symlinks to these files will be created in the working directory when the workflow is run. The symlinks will be removed once the workflow execution has successfully completed.
