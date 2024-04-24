---
title: Config
---

# Show the Workflow Configuration

The config subcommand will display the workflow configuration file contents. You can use the `--pretty` (`-p`) flag to display the configuration in a more readable format.

```bash
snk-basic-pipeline config
```
```yaml
genome: data/genome.fa
samples_dir: data/samples
sample:
- A
- B
- C
```

You can pipe the output to a file to save the configuration.

```bash
snk-basic-pipeline config > config.yaml
```

You can then edit the configuration file and use it to run the workflow.

```bash
snk-basic-pipeline run --config config.yaml
```
