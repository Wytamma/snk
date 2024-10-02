---
title: 'Snk: A Snakemake CLI and Workflow Management System'
tags:
  - Python
  - Snakemake
  - Workflow
  - Bioinformatics
  - Reproducibility
  - Command Line Interface
authors:
  - name: Wytamma Wirth
    orcid: 0000-0001-7070-0078
    affiliation: "1"
  - name: Simon Mutch
    orcid: 0000-0002-3166-4614
    affiliation: "2"
  - name: Robert Turnbull
    orcid: 0000-0003-1274-6750
    affiliation: "2"
affiliations:
 - name: Peter Doherty Institute for Infection and Immunity, University of Melbourne, Australia
   index: 1
 - name: Melbourne Data Analytics Platform, University of Melbourne, Melbourne 3010, Australia
   index: 2

date: 25 September 2024
bibliography: paper.bib
---

# Summary

Snk (pronounced "snek") is a workflow management tool designed to simplify the use of Snakemake workflows by dynamically generating command-line interfaces (CLIs). Snk allows complex Snakemake workflows to be used as modular components in larger systems that can be executed and managed from the command line with minimal overhead. This enables researchers and developers to integrate and manage sophisticated workflows seamlessly. Snk significantly improves the interoperability and accessibility of Snakemake workflows, making it easier to use and share computational pipelines in various research fields.

# Statement of need

The integration of bioinformatic analyses into comprehensive pipelines (aka workflows) has revolutionised the field by improving the robustness and reproducibility of analyses. One of the most popular workflow frameworks is Snakemake [@10.12688/f1000research.29032.2]. Snakemake is a user-friendly and adaptable make-style workflow framework with a powerful specification language built atop of the Python programming language. Despite its success, Snakemake workflows are often developed for specific research analysis rather than as general-purpose reusable tools. That is, Snakemake workflows are typically built for the reproducibility of a single analysis but not necessarily built for flexibility. 

To improve their utility Snakemake workflows developers often encapsulate workflows within CLI tools by producing wrapper code to abstract the workflow execution sometimes called workflows-as-applications or workflows packages [@roach_ten_2022]. These wrappers serve as intermediaries between the end-user (via the CLI) and the workflow execution, enabling developers to tailor the Snakemake experience to specific use cases. For example, the pangolin CLI tool wraps a snakemake workflow for SARS-CoV-2 lineage assignment [@otoole_pango_2022]. Initiatives like Snaketool have simplified the development of Snakemake-based CLIs by offering a template for developers [@roach_ten_2022]. Nonetheless, the onus remains on the developer to create and maintain the CLI wrappers for their workflow.

Here we present Snk, a Snakemake workflow management system that allows users to install Snakemake workflows as dynamically generated Command Line Interfaces. Thus users can create a CLI for theirs (or others) snakemake workflows with minimal to no changes code required. The Snk generate CLIs follow best practices and include several features out of box that improve user experience. The CLIs can be configured at install time or via a `snk.yaml` configuration file. Snk is readily available for installation via PYPI and Conda, using the commands `pip install snk` and `conda install snk`, respectively.

Snk has two distinct major functions; Managing the installation of workflows and Dynamical generating CLIs from Snakemake configuration files. To install a workflow as a CLI users can specify the file path, URL, or GitHub name (username/repo) of a workflow. Snk copies (clones) workflows into a managed directory structure, creates a CLI entry point, and optionally creates an isolated virtual environment for each workflow. Workflows can be installed from specific commits, tags, or branches ensuring reproducibility. The advent of Snk allows users to utilise the Snakemake workflow catalog (https://snakemake.github.io/snakemake-workflow-catalog) as a searchable package index of Snk installable Snakemake tools. The snk install command is flexible and can be used to install diverse workflows using installation options. For example, the [dna-seq-gatk-variant-calling workflow](https://github.com/snakemake-workflows/dna-seq-gatk-variant-calling) (release tag v2.1.1) can be installed as a CLI named `variant-calling` with Snakemake v8.10.8 and pandas dependency using the following command:

```bash
snk install \
  snakemake-workflows/dna-seq-gatk-variant-calling \
  --name variant-calling \
  --snakemake 8.10.8 \
  -d pandas \
  -t v2.1.1
```

The workflow will then accessible via the `variant-calling` CLI in the terminal (Figure 1). Additionally, the snk command can be used to list and uninstall workflows installed with Snk. The complete documentation for managing workflows can be found at \url{https://snk.wytamma.com/managing_workflows}.

![The `variant-calling` CLI generated by Snk.](docs/images/variant-calling-cli.png)

The core functionality of Snk is the dynamic creation of CLIs. Internally snk uses the `Snk-CLI` sister package to generate the CLI. By default key values pairs of the Snakemake configfile are mapped to CLI options e.g. `samples: samples.tsv` in the configfile will generate a `--samples` option in the CLI with the default value `samples.tsv` (Figure 2). The CLI generated by snk is highly customisable and can be configured via a snk.yaml file placed in the workflow directory. The snk.yaml file can configure many aspects of CLI including subcommands, ASCII art, help messages, resource files, default values and much more. Complete documentation for the Snk config file can be found at \url{https://snk.wytamma.com/snk_config_file}.

![The the run command of the `variant-calling` CLI dynamically generated from the Snakemake configfile. Several standard options are provided in the Options section e.g. `--dry` (equivalent to Snakemakes `--dry-run`), `--dag` to create a dag plot of the output, and `--cores` witch defaults to all. The Workflow Configuration section contains the options dynamically generated from the configfile. Snk-CLI automatically infers the defaults and types of the options and creates flags for boolean options.](docs/images/variant-calling-cli-run.png)

Developers can also directly use the Snk-CLI package to generate CLIs for their Snakemake workflows. By using the CLI class from Snk-CLI workflow developers can build a fully featured workflow package without having to write a Snakemake wrapper. We provide a guide for creating using Snk-CLI to build self contained tools at \url{https://snk.wytamma.com/workflow_packages}. The Snk-CLI package is available via PYPI and can be installed using the command `pip install snk-cli`. 

Snk is a powerful tool that simplifies the use of Snakemake workflows by dynamically generating CLIs. Snk is open-source software released under the MIT license. Snk documentation, source code, and issue tracker are available at \url{https://github.com/Wytamma/snk}. We welcome contributions and feedback from the community to improve Snk and make it a valuable tool for the Snakemake community and reproducible research at large.