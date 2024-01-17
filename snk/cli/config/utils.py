from pathlib import Path
from snakemake import load_configfile

def get_version_from_config(config_path: Path, config_dict: dict = None) -> str:
    """
    Get the version from config. If dict not provided, load from file.
    If the version is a path to a __about__ file, load the version from the file.
    Path must be relative to the config file.
    Args:
      config_path (Path): Path to the config file.
      config_dict (dict): Config dict.
    Returns:
      str: Version.
    Examples:
      >>> get_version_from_config_dict({"version": "0.1.0"})
      '0.1.0'
    """
    if not config_dict:
        config_dict = load_configfile(config_path)
    
    if "version" not in config_dict:
        return None 
    if config_dict["version"] is None:
        return None
    version = str(config_dict["version"])
    if "__about__.py" in version:
        # load version from __about__.py
        about_path = config_path.parent / version
        if not about_path.exists():
            raise FileNotFoundError(
                f"Could not find version file: {about_path}"
            )
        about = {}
        exec(about_path.read_text(), about)
        try:
            version = about["__version__"]
        except KeyError as e:
            raise KeyError(
                f"Could not find __version__ in file: {about_path}"
            ) from e
    return version