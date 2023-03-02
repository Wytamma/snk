from pathlib import Path
from .main import snk_cli

def cli(p):
    pipeline_dir_path = Path(p)
    app = snk_cli(pipeline_dir_path)
    app()

