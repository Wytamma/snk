from dataclasses import dataclass
import subprocess
from typing import List
import pytest
from snk_cli.config import SnkConfig

@dataclass
class Result:
    stdout: str
    stderr: str
    code: int


@dataclass
class CLIRunner:
    """Dynamically create a CLI Runner for testing"""

    command: List[str]

    def __call__(self, args: List[str]) -> Result:
        proc = subprocess.Popen(
            self.command + args,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        out, err = (output.decode("utf-8") for output in proc.communicate())
        return Result(out, err, proc.returncode)

def gen_dynamic_runner_fixture(config: dict = dict, snk: SnkConfig = SnkConfig(), snakefile_text="print(config)") -> CLIRunner:
    return pytest.mark.parametrize('dynamic_runner', [(config, snk, snakefile_text)], indirect=["dynamic_runner"])