import typer
import snakemake
from snakemake import Workflow, update_config, load_configfile, dict_to_key_value_args
from typing import Optional
from .cli import CLI
from .config import get_config_from_pipeline_dir
import os

def create_workflow( 
        snakefile,
        batch=None,
        cache=None,
        report=None,
        report_stylesheet=None,
        containerize=False,
        lint=None,
        generate_unit_tests=None,
        listrules=False,
        list_target_rules=False,
        cores=1,
        nodes=None,
        local_cores=1,
        max_threads=None,
        resources=dict(),
        overwrite_threads=None,
        overwrite_scatter=None,
        overwrite_resource_scopes=None,
        default_resources=None,
        overwrite_resources=None,
        config=dict(),
        configfiles=None,
        config_args=None,
        workdir=None,
        targets=None,
        target_jobs=None,
        dryrun=False,
        touch=False,
        forcetargets=False,
        forceall=False,
        forcerun=[],
        until=[],
        omit_from=[],
        prioritytargets=[],
        stats=None,
        printreason=True,
        printshellcmds=False,
        debug_dag=False,
        printdag=False,
        printrulegraph=False,
        printfilegraph=False,
        printd3dag=False,
        nocolor=False,
        quiet=False,
        keepgoing=False,
        slurm=None,
        slurm_jobstep=None,
        rerun_triggers=["mtime", "params", "input", "software-env", "code"],
        cluster=None,
        cluster_config=None,
        cluster_sync=None,
        drmaa=None,
        drmaa_log_dir=None,
        jobname="snakejob.{rulename}.{jobid}.sh",
        immediate_submit=False,
        standalone=False,
        ignore_ambiguity=False,
        snakemakepath=None,
        lock=True,
        unlock=False,
        cleanup_metadata=None,
        conda_cleanup_envs=False,
        cleanup_shadow=False,
        cleanup_scripts=True,
        cleanup_containers=False,
        force_incomplete=False,
        ignore_incomplete=False,
        list_version_changes=False,
        list_code_changes=False,
        list_input_changes=False,
        list_params_changes=False,
        list_untracked=False,
        list_resources=False,
        summary=False,
        archive=None,
        delete_all_output=False,
        delete_temp_output=False,
        detailed_summary=False,
        latency_wait=3,
        wait_for_files=None,
        print_compilation=False,
        debug=False,
        notemp=False,
        all_temp=False,
        keep_remote_local=False,
        nodeps=False,
        keep_target_files=False,
        allowed_rules=None,
        jobscript=None,
        greediness=None,
        no_hooks=False,
        overwrite_shellcmd=None,
        updated_files=None,
        log_handler=[],
        keep_logger=False,
        max_jobs_per_second=None,
        max_status_checks_per_second=100,
        restart_times=0,
        attempt=1,
        verbose=False,
        force_use_threads=False,
        use_conda=False,
        use_singularity=False,
        use_env_modules=False,
        singularity_args="",
        conda_frontend="conda",
        conda_prefix=None,
        conda_cleanup_pkgs=None,
        list_conda_envs=False,
        singularity_prefix=None,
        shadow_prefix=None,
        scheduler="ilp",
        scheduler_ilp_solver=None,
        conda_create_envs_only=False,
        mode=snakemake.common.Mode.default,
        wrapper_prefix=None,
        kubernetes=None,
        container_image=None,
        k8s_cpu_scalar=1.0,
        flux=False,
        tibanna=False,
        tibanna_sfn=None,
        google_lifesciences=False,
        google_lifesciences_regions=None,
        google_lifesciences_location=None,
        google_lifesciences_cache=False,
        tes=None,
        preemption_default=None,
        preemptible_rules=None,
        precommand="",
        default_remote_provider=None,
        default_remote_prefix="",
        tibanna_config=False,
        assume_shared_fs=True,
        cluster_status=None,
        cluster_cancel=None,
        cluster_cancel_nargs=None,
        cluster_sidecar=None,
        export_cwl=None,
        show_failed_logs=False,
        keep_incomplete=False,
        keep_metadata=True,
        messaging=None,
        edit_notebook=None,
        envvars=None,
        overwrite_groups=None,
        group_components=None,
        max_inventory_wait_time=20,
        execute_subworkflows=True,
        conda_not_block_search_path_envvars=False,
        scheduler_solver_path=None,
        conda_base_path=None,
        local_groupid="local"
    ):    
        cluster_config_content = dict()

        run_local = True

        overwrite_config = dict()
        if configfiles is None:
            configfiles = []
        for f in configfiles:
            # get values to override. Later configfiles override earlier ones.
            update_config(overwrite_config, load_configfile(f))
        # convert provided paths to absolute paths
        configfiles = list(map(os.path.abspath, configfiles))

        # directly specified elements override any configfiles
        if config:
            update_config(overwrite_config, config)
            if config_args is None:
                config_args = dict_to_key_value_args(config)

        if workdir:
            if not os.path.exists(workdir):
                os.makedirs(workdir)
            workdir = os.path.abspath(workdir)
            os.chdir(workdir)
            
        workflow = Workflow(
            snakefile=snakefile,
            rerun_triggers=rerun_triggers,
            jobscript=jobscript,
            overwrite_shellcmd=overwrite_shellcmd,
            overwrite_config=overwrite_config,
            overwrite_workdir=workdir,
            overwrite_configfiles=configfiles,
            overwrite_clusterconfig=cluster_config_content,
            overwrite_threads=overwrite_threads,
            max_threads=max_threads,
            overwrite_scatter=overwrite_scatter,
            overwrite_groups=overwrite_groups,
            overwrite_resources=overwrite_resources,
            overwrite_resource_scopes=overwrite_resource_scopes,
            group_components=group_components,
            config_args=config_args,
            debug=debug,
            verbose=verbose,
            use_conda=use_conda or list_conda_envs or conda_cleanup_envs,
            use_singularity=use_singularity,
            use_env_modules=use_env_modules,
            conda_frontend=conda_frontend,
            conda_prefix=conda_prefix,
            conda_cleanup_pkgs=conda_cleanup_pkgs,
            singularity_prefix=singularity_prefix,
            shadow_prefix=shadow_prefix,
            singularity_args=singularity_args,
            scheduler_type=scheduler,
            scheduler_ilp_solver=scheduler_ilp_solver,
            mode=mode,
            wrapper_prefix=wrapper_prefix,
            printshellcmds=printshellcmds,
            restart_times=restart_times,
            attempt=attempt,
            default_remote_provider=None,
            default_remote_prefix=default_remote_prefix,
            run_local=run_local,
            assume_shared_fs=assume_shared_fs,
            default_resources=default_resources,
            cache=cache,
            cores=cores,
            nodes=nodes,
            resources=resources,
            edit_notebook=edit_notebook,
            envvars=envvars,
            max_inventory_wait_time=max_inventory_wait_time,
            conda_not_block_search_path_envvars=conda_not_block_search_path_envvars,
            execute_subworkflows=execute_subworkflows,
            scheduler_solver_path=scheduler_solver_path,
            conda_base_path=conda_base_path,
            check_envvars=not lint,  # for linting, we do not need to check whether requested envvars exist
            all_temp=all_temp,
            local_groupid=local_groupid,
            keep_metadata=keep_metadata,
            latency_wait=latency_wait,
        )

        workflow.include(
            snakefile,
            overwrite_default_target=True,
            print_compilation=print_compilation,
        )
        workflow.check()
        return workflow


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

def create_rule_subcommand(cli: CLI):
    app = typer.Typer()

    workflow = create_workflow(
        cli.snakefile, 
        config=cli.snakemake_config, 
        configfiles=[get_config_from_pipeline_dir(cli.pipeline.path)]
    )
    workflow.check()

    for name in workflow._rules:
        rule = workflow.get_rule(name)
        wildcards_dict = rule.get_wildcards(None, wildcards_dict=None)
        (
            input,
            input_mapping,
            dependencies,
            incomplete_input_expand,
        ) = rule.expand_input(wildcards_dict)
        output, _ = rule.expand_output(wildcards_dict)
        # print(input.keys(), dependencies, input_mapping, wildcards_dict)
        print(rule.input.keys(), rule.params.keys(), output)
        def command():
            rule.run_func

        app.command(name=name)(command)


    return app