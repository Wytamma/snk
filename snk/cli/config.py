from pathlib import Path
import snakemake

def get_config_from_pipeline_dir(pipeline_dir_path: Path):
    """Search possible config locations"""
    for path in [Path('config') / 'config.yaml', Path('config') / 'config.yml', 'config.yaml', 'config.yml']:
        if (pipeline_dir_path / path).exists():
            return pipeline_dir_path / path 
    return None

def load_snk_config(pipeline_dir_path: Path):
    """
    Load SNK config from .snk or snakemake-workflow-catalog.yml.
    SNK config holds dynamic cli config and option annotations.
    returns empty dict if none is found 
    """
    snk_config_path = pipeline_dir_path / '.snk'
    if snk_config_path.exists():
        snk_config = snakemake.load_configfile(snk_config_path)
    else:
        snk_config = {}
    return snk_config

def load_pipeline_snakemake_config(pipeline_dir_path: Path):
    """
    Load snakemake config.
    """
    pipeline_config_path = get_config_from_pipeline_dir(pipeline_dir_path)
    if not pipeline_config_path.exists():
        return []
    return snakemake.load_configfile(pipeline_config_path)
