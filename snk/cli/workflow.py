from dataclasses import dataclass
from pathlib import Path
from snakemake import Workflow, update_config, load_configfile, dict_to_key_value_args, common
from snakemake.persistence import Persistence
import os

def create_workflow( 
        snakefile,
        cache=None,
        lint=None,
        cores=1,
        nodes=None,
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
        printshellcmds=False,
        rerun_triggers=["mtime", "params", "input", "software-env", "code"],
        conda_cleanup_envs=False,
        latency_wait=3,
        print_compilation=False,
        debug=False,
        all_temp=False,
        jobscript=None,
        overwrite_shellcmd=None,
        restart_times=0,
        attempt=1,
        verbose=False,
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
        mode=common.Mode.default,
        wrapper_prefix=None,
        default_remote_prefix="",
        assume_shared_fs=True,
        keep_metadata=True,
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
            overwrite_clusterconfig=dict(),
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
            run_local=True,
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
        @dataclass
        class PersistenceMock(Persistence):
            """
            Mock for workflow.persistence
            """
            conda_env_path: Path = None
            _metadata_path: Path = None
            _incomplete_path: Path = None
            shadow_path: Path = None
            conda_env_archive_path: Path = None
            container_img_path: Path = None
            aux_path: Path = None

        workflow.persistence = PersistenceMock(
            conda_env_path=Path(conda_prefix).resolve() if conda_prefix else None,
            conda_env_archive_path = os.path.join(Path(".snakemake"), "conda-archive")
        )
        return workflow

