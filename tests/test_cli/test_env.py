def test_env_run(local_runner):
    res = local_runner(["env", "run", "pandas", "which python"])
    assert res.code == 0, res.stderr
    assert ".snakemake" in res.stdout, res.stderr

def test_env_activate(local_runner):
    res = local_runner(["env", "activate", "pandas"])
    assert res.code == 0, res.stderr
    assert "Activating pandas environment..." in res.stdout, res.stderr
    assert "Exiting pandas environment..." in res.stdout, res.stderr