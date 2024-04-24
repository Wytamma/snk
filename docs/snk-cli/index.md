---
title: The Snk CLI
---

# Snk-cli

[Snk-cli](https://github.com/Wytamma/snk-cli) is used internally by snk to dynamically generate the snakemake CLIs. The generated CLI is modern and feature rich and provides subcommands for interacting with the workflow. Many aspects of the generated CLI can be configured though the [Snk config file](/snk_config_file/).

The CLI provides several commands for interacting with the workflow including:

- [config](/snk-cli/env/) - Show the workflow configuration.
- [env](/snk-cli/env/) - Access the workflow conda environments.
- [script](/snk-cli/script/) - Access the workflow scripts.
- [info](/snk-cli/info) - Show information about the workflow.
- [profile](/snk-cli/info) - Access the workflow profiles.
- [run](/snk-cli/info) - Run the Snakemake workflow.

You can also use `snk-cli` without `snk` to build self contained snakemake tools. See here for more details -> https://snk.wytamma.com/workflow_packages