---
title: profile
---

# Access the workflow profiles

The `profile` subcommand provides several commands to manage the workflow profiles. Profiles are used to define different configurations for the workflow e.g. you can configure how the workflow will run on a HPC. You can read more about profiles in the [Snakemake documentation](https://snakemake.readthedocs.io/en/stable/executing/cli.html#profiles).

!!! note

    For snk to be able to access the profiles, the profiles must be located in the `profiles` directory of the workflow.

## List

List the profiles in the workflow.

```bash
snk-basic-pipeline profile list
```

## Show

The show command will display the contents of a profile.

```bash
snk-basic-pipeline profile show slurm
```

