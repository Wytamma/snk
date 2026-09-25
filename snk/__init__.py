# SPDX-FileCopyrightText: 2022-present wytamma <wytamma.wirth@me.com>
#
# SPDX-License-Identifier: MIT
import os
from pathlib import Path

from snk_cli import CLI, validate_config  # noqa: F401

from .nest import Nest  # noqa: F401


def create_cli(p):
    """
    This is the interface to create the dynamic CLI.
    Changing this function name will break backwards compatibility.

    Args:
      p (str): The path to the workflow directory.

    Returns:
      None

    Examples:
      >>> create_cli("/path/to/workflow")
      ... # CLI is created and executed
    """
    workflow_dir_path = Path(p)
    # Move CONDA_PREFIX to $SNK_HOME/conda/<pipeline_name> to prevent
    # editable packages from being polluted with a .conda folder
    snk_home = os.environ.get("SNK_HOME")
    if not snk_home and workflow_dir_path.parent.name == "workflows":
        snk_home = str(workflow_dir_path.parent.parent)
    if snk_home:
        conda_prefix = Path(snk_home) / "conda" / workflow_dir_path.name
        os.environ["CONDA_PREFIX"] = str(conda_prefix)
    cli = CLI(workflow_dir_path)
    cli()
