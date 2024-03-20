# SPDX-FileCopyrightText: 2022-present wytamma <wytamma.wirth@me.com>
#
# SPDX-License-Identifier: MIT
from .nest import Nest # noqa: F401
from pathlib import Path
from snk_cli import CLI, validate_config # noqa: F401

def create_cli(p):
    """
    This is the interface to create the dynamic CLI.
    Changing this function name will break backwards compatibility.

    Args:
      p (str): The path to the workflow directory.

    Returns:
      None

    Examples:
      >>> create_cli('/path/to/workflow')
      ... # CLI is created and executed
    """
    workflow_dir_path = Path(p)
    cli = CLI(workflow_dir_path)
    cli()
