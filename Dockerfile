FROM snakemake/snakemake:stable

RUN apt-get update && \
    apt-get -y install gcc