from pathlib import Path
from .cli import CLI


def create_cli(p):
    """
    This is the interface to create the dynamic CLI.
    Changing this function name will break backwards compatibility.
    """
    workflow_dir_path = Path(p)
    cli = CLI(workflow_dir_path)
    cli()
