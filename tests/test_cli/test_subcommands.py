import pytest

@pytest.mark.parametrize("cmd,expected", [
    (["script", "run", "hello.py"], ["hello world"]),
    (["script", "list"], ["hello.py"]),
    (["script", "show", "hello.py"], ["print('hello world')"]),
    (["env", "list"], ["pandas"]),
    (["env", "show", "pandas"], ["pandas"]),
    (["env", "prune"], ["Deleting all conda environments..."]),
    (["env", "create"], ["Creating all conda environments..."]),
    (["env", "run", "-v", "pandas", "which python"], [".snakemake"]),
    (["env", "activate", "pandas"], ["Activating pandas environment...", "Exiting pandas environment..."]),
])
def test_snk_cli_command(local_runner, cmd, expected):
    res = local_runner(cmd)
    assert res.code == 0, res.stderr
    for e in expected:
        assert e in res.stdout, res.stderr