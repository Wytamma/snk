from pathlib import Path
from typing import List
import snakemake
from dataclasses import dataclass, field

import yaml

@dataclass
class SnkConfig:
    """
    SNK config holds dynamic cli config and option annotations.
    """
    resources: List[Path] = field(default_factory=list)
    annotations: dict = field(default_factory=dict)

    @classmethod
    def from_path(cls, snk_config_path: Path):
        """
        Load and validate SNK config from .snk file.
        """
        if snk_config_path.exists():
            snk_config_dict = snakemake.load_configfile(snk_config_path)
            snk_config = cls(**snk_config_dict)
            snk_config.resources = [snk_config_path.parent / resource for resource in snk_config.resources]
            snk_config.validate_resources(snk_config.resources)
            return snk_config
        return cls()
    
    def validate_resources(self, resources):
        """
    Validate resources.
    Args:
      resources (List[Path]): List of resources to validate.
    Raises:
      FileNotFoundError: If a resource is not found.
    Notes:
      This function does not modify the resources list.
    """
        for resource in resources:
            assert resource.exists(), FileNotFoundError(f"Could not find resource: {resource}")

    def add_resources(self, resources: List[Path], pipeline_dir_path: Path = None):
        """
        Add and validate resources. 
        It takes a list of resources, and if the resource is not absolute, it appends the
        pipeline_dir_path to the resource
        
        :param resources: List[Path]
        :param pipeline_dir_path: The path to the directory containing the pipeline
        """
        processed = []
        for resource in resources:
            if pipeline_dir_path and not resource.is_absolute():
                resource = pipeline_dir_path / resource
            processed.append(resource)
        self.validate_resources(processed)
        self.resources.extend(processed)

    def to_yaml(self, path: Path) -> None:
        """
        Write SNK config to YAML file.
        Args:
            path (Path): Path to write the YAML file to.
        Returns:
            None
        Side Effects:
            Writes the SNK config to the specified path.
        """
        with open(path, 'w') as f:
            yaml.dump(vars(self), f)
                             
    

def get_config_from_pipeline_dir(pipeline_dir_path: Path):
    """Search possible config locations"""
    for path in [Path('config') / 'config.yaml', Path('config') / 'config.yml', 'config.yaml', 'config.yml']:
        if (pipeline_dir_path / path).exists():
            return pipeline_dir_path / path 
    return None



def load_pipeline_snakemake_config(pipeline_dir_path: Path):
    """
    Load snakemake config.
    """
    pipeline_config_path = get_config_from_pipeline_dir(pipeline_dir_path)
    if not pipeline_config_path.exists():
        return []
    return snakemake.load_configfile(pipeline_config_path)
