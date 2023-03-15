import typer
from typing import Optional
import sys
import logging

import snakemake

from snk.cli.config import get_config_from_pipeline_dir

def launch_gui(
        snakefile,
        conda_prefix_dir,
        pipeline_dir_path,
        config,
        host: Optional[str] = "127.0.0.1",
        port: Optional[int] = 8000,
        cluster: Optional[str] = None,
    ):
    try:
        import snakemake.gui as gui
        from functools import partial
        import webbrowser
        from threading import Timer
    except ImportError:
        typer.secho(
            "Error: GUI needs Flask to be installed. Install "
            "with easy_install or contact your administrator.",
            err=True)
        raise typer.Exit(1)
    logging.getLogger("werkzeug").setLevel(logging.ERROR)
    _snakemake = partial(snakemake.snakemake, snakefile)

    gui.app.extensions["run_snakemake"] = _snakemake
    gui.app.extensions["args"] = dict(
        cluster=cluster,
        configfiles=[get_config_from_pipeline_dir(pipeline_dir_path)],
        targets=[],
        use_conda=True,
        conda_frontend="mamba",
        conda_prefix=conda_prefix_dir,
        config=config
    )
    gui.app.extensions["snakefilepath"] = snakefile
    target_rules = []
    def log_handler(msg):
        if msg["level"] == "rule_info":
            target_rules.append(msg["name"])
    gui.run_snakemake(list_target_rules=True, log_handler=[log_handler], config=config)
    gui.app.extensions["targets"] = target_rules

    resources = []
    def log_handler(msg):
        if msg["level"] == "info":
            resources.append(msg["msg"])

    gui.app.extensions["resources"] = resources
    gui.run_snakemake(list_resources=True, log_handler=[log_handler], config=config)
    url = "http://{}:{}".format(host, port)
    print("Listening on {}.".format(url), file=sys.stderr)

    def open_browser():
        try:
            webbrowser.open(url)
        except:
            pass

    print("Open this address in your browser to access the GUI.", file=sys.stderr)
    Timer(0.5, open_browser).start()
    success = True

    try:
        gui.app.run(debug=False, threaded=True, port=int(port), host=host)

    except (KeyboardInterrupt, SystemExit):
        # silently close
        pass



