FROM ubuntu:18.04

RUN sudo wget https://github.com/graphhopper/graphhopper/releases/download/5.3/graphhopper-web-5.3.jar -P ./graphhopper/

RUN sudo mkdir -p /var/simra/pbf && \
    sudo wget https://download.geofabrik.de/europe/germany/berlin-latest.osm.pbf -P /var/simra/pbf/ && \
    sudo wget https://download.geofabrik.de/europe/dach-latest.osm.pbf -P /var/simra/pbf/

RUN sudo apt install -y default-jdk

CMD sudo java -jar ./graphhopper/graphhopper-web-5.3.jar server ./graphhopper/config.yml