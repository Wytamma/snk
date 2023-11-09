def test_script_list(local_runner):
    res = local_runner(["script", "list"])
    assert res.code == 0, res.stderr
    assert "Found 1 script" in res.stdout, res.stderr
    assert "hello.py" in res.stdout, res.stderr

def test_script_show(local_runner):
    res = local_runner(["script", "show", "hello.py"])
    assert res.code == 0, res.stderr
    assert "print('hello world')" in res.stdout, res.stderr

def test_script_run(local_runner):
    res = local_runner(["script", "run", "hello.py"])
    assert res.code == 0, res.stderr
    assert "hello world" in res.stdout, res.stderr