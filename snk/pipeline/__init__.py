from pathlib import Path
from .main import pipeline_cli_factory

def cli(p):
    pipeline_dir_path = Path(p)
    app = pipeline_cli_factory(pipeline_dir_path)
    app()

