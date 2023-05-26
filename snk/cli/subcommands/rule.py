import typer
from ..cli import CLI
from ..config import get_config_from_pipeline_dir
from ..workflow import create_workflow
from ..utils import add_dynamic_options
from snakemake.io import Namedlist

def job_args_and_prepare(job):
    job.prepare()

    conda_env = (
        job.conda_env.address if self.workflow.use_conda and job.conda_env else None
    )
    container_img = (
        job.container_img_path if self.workflow.use_singularity else None
    )
    env_modules = job.env_modules if self.workflow.use_env_modules else None

    benchmark = None
    benchmark_repeats = job.benchmark_repeats or 1
    if job.benchmark is not None:
        benchmark = str(job.benchmark)
    return (
        job.rule,
        job.input._plainstrings(),
        job.output._plainstrings(),
        job.params,
        job.wildcards,
        job.threads,
        job.resources,
        job.log._plainstrings(),
        benchmark,
        benchmark_repeats,
        conda_env,
        container_img,
        self.workflow.singularity_args,
        env_modules,
        self.workflow.use_singularity,
        self.workflow.linemaps,
        self.workflow.debug,
        self.workflow.cleanup_scripts,
        job.shadow_dir,
        job.jobid,
        self.workflow.edit_notebook if self.dag.is_edit_notebook_job(job) else None,
        self.workflow.conda_base_path,
        job.rule.basedir,
        self.workflow.sourcecache.runtime_cache_path,
    )

def create_rule_cli_options(namedList: Namedlist, grp = 'INPUT') -> list:
    options = []
    c = 1
    for option_name, item in namedList._allitems():
        _type = 'List[Path]' if type(item) == Namedlist else 'Path'
        arg = False
        if not option_name:
            arg = True 
            option_name = f"{grp}_{c}" if c != 1 else f"{grp}"
            c += 1
        options.append(
            {
                'name': option_name, 
                'type': _type, 
                'required': True, 
                'help': f'e.g. {item}', 
                'meta': grp,
                'arg': arg},
        )
    return options

def create_rule_subcommand(cli: CLI):
    app = typer.Typer()

    workflow = create_workflow(
        cli.snakefile,
        config=cli.snakemake_config,
        configfiles=[get_config_from_pipeline_dir(cli.pipeline.path)],
        use_conda = True,
    )

    for name in workflow._rules:
        if name == 'all':
            continue
        rule = workflow.get_rule(name)
        options = []
        # wildcards_dict = rule.get_wildcards(cli.snakefile, wildcards_dict={})
        # (
        #     input,
        #     input_mapping,
        #     dependencies,
        #     incomplete_input_expand,
        # ) = rule.expand_input(wildcards_dict)
        # output, _ = rule.expand_output(wildcards_dict)
        options.extend(create_rule_cli_options(rule.params, grp='PARAM'))
        options.extend(create_rule_cli_options(rule.output, grp= 'OUTPUT'))
        options.extend(create_rule_cli_options(rule.input, grp= 'INPUT'))
        print(rule.input._plainstrings())
        # options.append({
        #     'name'
        # })
        @add_dynamic_options(options)
        @app.command(
            name=name, 
            help='', 
            context_settings={
                "allow_extra_args": True,
                "ignore_unknown_options": True,
                "help_option_names": ["-h", "--help"],
            })
        def command(ctx: typer.Context):
            # rule.run_func(
            #     input,
            #     output,
            #     params,
            #     wildcards,
            #     threads,
            #     resources,
            #     log,
            #     version,
            #     rule,
            #     conda_env,
            #     container_img,
            #     singularity_args,
            #     use_singularity,
            #     env_modules,
            #     bench_record,
            #     jobid,
            #     is_shell,
            #     bench_iteration,
            #     cleanup_scripts,
            #     passed_shadow_dir,
            #     edit_notebook,
            #     conda_base_path,
            #     basedir,
            #     runtime_sourcecache_path,
            # )
            print(ctx.args)
        # need to figure out how to load rules without exicuting the snakefile
        # don't think it's possible or needed?

    return app