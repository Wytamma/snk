import pytest
from typer.testing import CliRunner
from snk.cli.dynamic_typer import DynamicTyper, Option
from snk.cli.options import Option
from typing import Callable
from inspect import signature, Parameter
import typer


@pytest.fixture
def dynamic_typer():
    return DynamicTyper()

@pytest.fixture
def dynamic_app():
    class App(DynamicTyper):
        pass
    return App()

@pytest.fixture
def cli_runner():
    return CliRunner()


def test_dynamic_typer_init(dynamic_app):
    assert isinstance(dynamic_app.app, typer.Typer)


def test_register_default_command(dynamic_app: DynamicTyper, cli_runner):
    
    class App(DynamicTyper):
        def __init__(self):
            self.register_default_command(self.hello)
        def hello(self):
            self.echo("Hello World")

    result = cli_runner.invoke(App().app)
    assert result.exit_code == 0, result.stdout
    assert result.stdout.strip() == "Hello World"


def test_register_command(dynamic_app: DynamicTyper, cli_runner):
    def command(name: str):
        print(f"Hello {name}")

    dynamic_app.register_command(command)
    result = cli_runner.invoke(dynamic_app.app, ["John"])
    assert result.exit_code == 0
    assert result.stdout.strip() == "Hello John"


def test_register_callback(dynamic_app: DynamicTyper, cli_runner):
    
    def callback(name: str):
        print(f"Hello {name}")

    dynamic_app.register_callback(callback, invoke_without_command=True)
    result = cli_runner.invoke(dynamic_app.app, ["John"])
    assert result.exit_code == 0, result.stdout
    assert result.stdout.strip() == "Hello John"


def test_register_group(dynamic_app: DynamicTyper, cli_runner):
    
    class SubApp(DynamicTyper):
        def __init__(self):
            self.register_command(self.hello)
        def hello(self):
            self.echo("Hello World")

    dynamic_app.register_group(SubApp(), name="subapp", help="A subapp")

    result = cli_runner.invoke(dynamic_app.app, ["subapp", "hello"])
    assert result.exit_code == 0, result.stdout
    assert result.stdout.strip() == "Hello World"


def test_create_cli_parameter(dynamic_typer):
    option = Option(
        name="foo",
        type=int,
        required=True,
        default=0,
        help="A number",
        short="f",
        updated=True,
        original_key="foo",
        flag="--foo",
        short_flag="-f",
    )
    param = dynamic_typer._create_cli_parameter(option)
    assert isinstance(param, Parameter)
    assert param.name == "foo"
    assert param.annotation == int
    assert isinstance(param.default, typer.models.OptionInfo)
    assert param.kind == Parameter.POSITIONAL_OR_KEYWORD



def test_add_dynamic_options(dynamic_typer):
    def func(name: str):
        return f"Hello {name}"

    options = [
        Option(
            name="foo",
            type=int,
            required=True,
            default=0,
            help="A number",
            short="f",
            updated=True,
            original_key="foo",
            flag="--foo",
            short_flag="-f",
        )
    ]
    func_wrapper = dynamic_typer.add_dynamic_options(func, options)
    assert callable(func_wrapper)
    assert "foo" in signature(func_wrapper).parameters


def test_error(dynamic_typer, cli_runner):
    with pytest.raises(typer.Exit):
        dynamic_typer.error("Error message")


def test_log(dynamic_typer, cli_runner, capsys):
    dynamic_typer.log("Log message", stderr=False)
    captured = capsys.readouterr()
    assert "Log message" in captured.out
