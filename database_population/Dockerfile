FROM ubuntu:18.04

RUN sudo wget "https://github.com/omniscale/imposm3/releases/download/v0.10.0/imposm-0.10.0-linux-x86-64.tar.gz" && \
    tar -xf imposm-0.10.0-linux-x86-64.tar.gz

CMD sudo ./imposm-0.10.0-linux-x86-64/imposm import -mapping mapping.yml -read "/var/simra/pbf/berlin-latest.osm.pbf" -overwritecache -write -connection postgis://simra:simra12345simra@localhost/simra