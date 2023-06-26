---
title: Snk Config File
---

# Snk Configuration File

The `snk.yaml` file serves as the main interface for configuring the Snk pipeline CLI. Users can tailor the pipeline's settings, specify required resources, and control the appearance of the command line interface by setting various options in the `snk.yaml` file.

## Available Configuration Options

The following options are available for configuration in `snk.yaml`:

- `logo`: The text used to dynamically generate the ASCII art displayed in the CLI.
- `art`: A string representing ASCII art to display in the CLI (overwrites `logo`).
- `tagline`: A string representing the tagline displayed in the CLI.
- `font`: A string representing the font used in the CLI.
- `resources`: A list of resource files required for the pipeline.
- `annotations`: Annotations for the pipeline parameters.
- `symlink_resources`: A boolean that controls whether symbolic links are created for resources.

## Example `snk.yaml` File

Below is an example of a `snk.yaml` file illustrating all available options:

```yaml
logo: "MyPipeline"
tagline: "A pipeline to illustrate the use of snk.yaml"
font: "cybermedium"
resources:
  - "data/input1.txt"
  - "data/input2.txt"
annotations:
  input:
    type: Path
    help: "Path to the input file"
    required: False
```

In this example:

- The pipeline logo is set to "MyPipeline".
- The tagline is "A pipeline to illustrate the use of snk.yaml".
- The font used in the CLI is "cybermedium".
- Two resource files, "data/input1.txt" and "data/input2.txt", are required for the pipeline.
- An annotation is provided for the `input` parameter, which is of type `str` and comes with a help message "Path to the input file".

## Annotations

Annotations play a crucial role in configuring the dynamic Snk CLI. They provide metadata about the configuration parameters used in your Snakemake pipeline and can dictate how the CLI will prompt users for these parameters. The `snk.yaml` file supports the following fields under `annotations`:

- `type`: Determines the datatype of the configuration parameter. It can be one of the following: `int`, `str`, `path`, `bool`, `list`, `list[str]`, `list[path]`, or `list[int]`.
- `help`: This is a descriptive text that provides users with information or guidance on what the parameter is used for.
- `required`: A boolean value (either `True` or `False`) that indicates whether the parameter is mandatory. If a parameter is marked as `required: True`, the Snk CLI will insist that a user provides a value for it.

### Example `snk.yaml` File with Annotations

Here's an example of a `snk.yaml` file that includes annotations for several configuration parameters:

```yaml
annotations:
  input:
    type: path
    help: "Path to the input file"
    required: True
  text:
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

In this example, the `input` and `count` parameters are required, while the `text` and `flag` parameters are optional. The `type` and `help` attributes provide additional information about each parameter, informing the user of the expected datatype and what the parameter is used for, respectively.

## Resources

Resources represent files or folders that are essential for the execution of the pipeline. They must be present in the pipeline's working directory at runtime. The `snk.yaml` configuration file allows you to specify these resources.

When the pipeline is invoked with the `run` command, the Snk CLI will ensure that the specified resources are available in the working directory. It accomplishes this by either copying the resource files or creating symbolic links (symlinks) to them. The method used depends on the value of the `symlink_resources` option in the `snk.yaml` file. If `symlink_resources` is set to `true`, symlinks will be used. Otherwise, the files will be copied.

!!! warning

    You should only set `symlink_resources` to `true` if the pipeline won't modify these resources. Any modifications to symlinked resources will be system-wide!


Once the pipeline has successfully completed, the Snk CLI will clean up the working directory by deleting the copied resources or unlinking the symlinks.

### Example `snk.yaml` File with Resources

Here's an example of how you might specify resources in a `snk.yaml` file:

```yaml
resources:
  - "data/input1.txt"
  - "data/input2.txt"
symlink_resources: true
```

In this example, `data/input1.txt` and `data/input2.txt` are listed as required resources for the pipeline. The `symlink_resources` option is set to `true`, meaning that symlinks to these files will be created in the working directory when the pipeline is run. The symlinks will be removed once the pipeline execution has successfully completed.