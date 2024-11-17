---
title: Snk Config File
---

# Snk Configuration File

The `snk.yaml` file serves as the main interface for configuring the Snk workflow CLI. Users can tailor the workflow's settings, specify required resources, and control the appearance of the command line interface by setting various options in the `snk.yaml` file.

## Modifying the `snk.yaml` File

The `snk.yaml` file should be located in the root directory of the Snakemake workflow. It is used to configure the Snk CLI and provide additional information about the workflow. The `snk.yaml` file is written in YAML format and can be edited with any text editor.

For convenience, you can use the `snk edit [WORKFLOW_NAME]` command to open the `snk.yaml` file in your default text editor. This command will create a new `snk.yaml` file if one does not already exist.

```bash
snk edit workflow
```

## Available Configuration Options

The following options are available for configuration in `snk.yaml`:

| Name                      | Description                                                                                                              | Type                | Default                                                          |
|---------------------------|--------------------------------------------------------------------------------------------------------------------------|---------------------|------------------------------------------------------------------|
| `logo`                    | The text used to dynamically generate the ASCII art displayed in the CLI.                                                 | String              | `<name-of-workflow>`                                              |
| `art`                     | A string representing ASCII art to display in the CLI (overwrites `logo`).                                                | String or `null`    | `null`                                                           |
| `tagline`                 | A string representing the tagline displayed in the CLI.                                                                   | String              | `"A Snakemake workflow CLI generated with Snk"`                   |
| `font`                    | A string representing the font used in the CLI (see [FontList](https://www.ascii-art.site/FontList.html)).                 | String              | `"small"`                                                         |
| `resources`               | A list of resource files required for the workflow.                                                                       | List                | `[]`                                                             |
| `symlink_resources`        | A boolean that controls whether symbolic links are created for resources (avoid using this unless you know).               | Boolean             | `False`                                                          |
| `conda`                   | A boolean that controls whether the workflow should use conda. The `--use-conda` flag will only be passed to snakemake if True.         | Boolean             | `True`                                                           |
| `additional_snakemake_args`| A list of additional arguments to pass to snakemake.                                                                      | List                | `[]`                                                             |
| `skip_missing`            | Skip any missing CLI options (i.e. those in config but not in the snk file).                                               | Boolean             | `False`                                                          |
| `commands`                | A list of subcommands to include in the CLI.                                                                               | List                | `["run", "script", "env", "profile", "info", "config"]`           |
| `min_snk_cli_version`     | The minimum version of the Snk CLI required to run the workflow.                                                          | String or `null`    | `null`                                                           |
| `cli`                     | Annotations for the workflow CLI parameters (see [CLI section](https://snk.wytamma.com/snk_config_file/#cli) below).       | Object              | None                                                             |


## Example `snk.yaml` File

Below is an example of a `snk.yaml` file illustrating all available options:

```yaml
logo: "MyWorkflow"
font: "small"
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
min_snk_cli_version: "0.6.1"
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

- The workflow dynamically generated `logo` is set to "MyWorkflow".
- The `font` used for the logo is "small".
- ASCII art is specified directly in the `art` configuration, taking precedence over the logo if both are provided.
- The `tagline` is "A workflow to illustrate the use of snk.yaml". This will be printed in the CLI help under the logo.
- Two resource files, `data/input1.txt` and `data/input2.txt`, are required for the workflow. They will be copied to the working directory at runtime.
- The `conda` flag is enabled (True), indicating that the workflow should utilise Conda environments for executing tasks, provided the conda command is accessible in the system environment.
- Additional Snakemake arguments are specified under `additional_snakemake_args`, including --reason which will display the reasons for rule execution.
- The `skip_missing` option is enabled (True), which means that only config defined in the `snk.yaml` file, will be included in the dynamically generate CLI.
- The `min_snk_cli_version` is set to "0.6.1", indicating that the workflow requires at least version 0.6.1 of the Snk CLI to run.
- An annotation is provided for the `input` parameter, which is of type `str` and comes with a help message "Path to the input file".

## CLI

Annotations play a crucial role in configuring the dynamic Snk CLI. They provide metadata about the configuration parameters used in your Snakemake workflow and can dictate how the CLI will prompt users for these parameters. The `snk.yaml` file supports the following fields under the `cli` option:

- `type`: Determines the datatype of the configuration parameter. It can be one of the following: `int`, `str`, `path`, `bool`, `list`, `list[str]`, `list[path]`, `list[int]`, `list[float]`, `pair`, or `dict`.
- `help`: This is a descriptive text that provides users with information or guidance on what the parameter is used for.
- `required`: A boolean value (either `True` or `False`) that indicates whether the parameter is mandatory. If a parameter is marked as `required: True`, the Snk CLI will insist that a user provides a value for it.
- `default`: A default value for the parameter. If a user does not provide a value for the parameter, the Snk CLI will use this default value instead.
- `short`: A short (-) flag to use with the option.
- `choices`: A list of possible values that the parameter can take. If a user provides a value that is not in this list, the Snk CLI will raise an error.

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
  value_pair:
    type: pair[str, int]
    default: ["key", 1]
    help: "A key-value pair"
    required: False
  dict:
    type: dict[str, str]
    default: [["key1", "value1"], ["key2", value2"]]
    help: "A dictionary"
    required: False
  choice:
    help: "A choice to select"
    choices:
      - "option1"
      - "option2"
    required: False
```

In this example, the `input` and `count` parameters are required, while the `text`, `flag` and `choice` parameters are optional. the flag `-i` can be used as shorthand for `--input`. The `text` parameter has a default value of "Hello, world!" that will be used if the user does not provide a value. 

The parameter `value_pair` is a pair of a string and an integer, with a default value of `["key", 1]`. The `dict` parameter is a dictionary of strings, with a default value of `[["key1", "value1"], ["key2", value2"]]` that will be convert to a dictionary when passed to snakemake. The `choice` parameter can only take one of the values specified in the `choices` list. 

The `type` and `help` attributes provide additional information about each parameter, informing the user of the expected datatype and what the parameter is used for, respectively.

### Nested Annotations in the `snk.yaml` File

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

If you don't have a `config.yaml` file, you can still use the `snk.yaml` file to specify the parameters and defaults for your workflow. The `snk.yaml` file will be used to generate the CLI, and the parameters will be available in the `config` dictionary in your `Snakefile`. However, you should probably still have a `config.yaml` file to store your config, as this is the standard way to manage configuration in Snakemake workflows (unless you're creating a [workflow package](https://snk.wytamma.com/workflow_packages)).

### Validating Config with the `snk.yaml` File

Snk provides a function that can be use to validate snakemake config using the `snk.yaml` cli annotations. The `validate_config` function will convert values to the correct type if possible. If the value cannot be converted to the correct type, an error will be raised. This can be added to the start of your `Snakefile` to ensure that the config is valid before running the workflow.

```python
try:
  from snk_cli import validate_config
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
