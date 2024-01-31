import pytest

@pytest.mark.parametrize("cmd,expected_in_stdout,expected_in_stderr", [
    (["script", "run", "hello.py"], ["hello world"], []),
    (["script", "list"], ["hello.py"], []),
    (["script", "show", "hello.py"], ["print('hello world')"], []),
    (["profile", "list"], ["slurm"], []),
    (["profile", "show", "slurm"], ["cluster"], []),
    (["env", "list"], ["python"], []),
    (["env", "show", "python"], ["python"], []),
    (["env", "create"], ["All conda environments created!"], []),
    (["env", "create", "python"], ["Created environment python!"], []),
    (["env", "run", "-v", "python", "which python"], [".snakemake"], []),
    (["env", "activate", "python"], [], ["Activating python environment...", "Exiting python environment..."]),
    (["env", "remove", "-f"], ["Deleted"], []),
])
def test_snk_cli_command(local_runner, cmd, expected_in_stdout, expected_in_stderr):
    res = local_runner(cmd)
    assert res.code == 0, res.stderr
    for expected in expected_in_stdout:
        assert expected in res.stdout, res.stderr
    for expected in expected_in_stderr:
        assert expected in res.stderr, res.stderr