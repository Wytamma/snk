from pathlib import Path
from .main import CLI

def create_cli(p):
    pipeline_dir_path = Path(p)
    cli = CLI(pipeline_dir_path)
    cli()

