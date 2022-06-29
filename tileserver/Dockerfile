FROM ubuntu:18.04
ENV DEBIAN_FRONTEND noninteractive

# Get all necessary packages
RUN apt-get update && apt-get install -y \
    git wget build-essential ca-certificates sudo vim \
    python3.8 python3.8-dev \
    gcc g++ clang zlib1g-dev make pkg-config curl \
    libboost-dev libboost-filesystem-dev libboost-program-options-dev libboost-python-dev libboost-regex-dev libboost-system-dev libboost-thread-dev libharfbuzz-dev libicu-dev libcairo-dev libgdal-dev \
    libtiff5-dev libfreetype6-dev libxml2-dev libproj-dev libsqlite3-dev libgdal-dev libcairo-dev python-cairo-dev \
    python-setuptools libboost-python-dev libboost-thread-dev \
    libboost-all-dev git-core tar unzip wget bzip2 build-essential autoconf libtool libxml2-dev libgeos-dev libgeos++-dev libpq-dev libbz2-dev libproj-dev munin-node munin libprotobuf-c0-dev protobuf-c-compiler libfreetype6-dev libtiff5-dev libicu-dev libgdal-dev libcairo-dev libcairomm-1.0-dev apache2 apache2-dev libagg-dev liblua5.2-dev ttf-unifont lua5.1 liblua5.1-dev libgeotiff-epsg \
    apache2 apache2-dev \
    build-essential autoconf libcairo2-dev libcurl4-gnutls-dev libglib2.0-dev libiniparser-dev libmapnik-dev libmemcached-dev librados-dev

RUN curl -LO https://github.com/BurntSushi/ripgrep/releases/download/13.0.0/ripgrep_13.0.0_amd64.deb \
    && dpkg -i ripgrep_13.0.0_amd64.deb
RUN rm /usr/bin/python && ln -s /usr/bin/python3.8 /usr/bin/python
RUN wget https://bootstrap.pypa.io/get-pip.py && python3.8 get-pip.py

# Fetch & install Mapnik
RUN git clone --depth 1 --branch v3.0.23 https://github.com/mapnik/mapnik.git \
    && cd mapnik \
    && git submodule update --init
RUN /bin/bash -c 'cd mapnik && source bootstrap.sh && ./configure'
RUN cd mapnik && JOBS=4 make
RUN cd mapnik && make install

# Fetch & install Mapnik Python Bindings
# RUN git clone --depth 1 --branch v3.0.x https://github.com/mapnik/python-mapnik.git
# RUN cd python-mapnik && python setup.py install

# Fetch & install Tirex
RUN cpan JSON && cpan IPC::ShareLite
RUN git clone --depth 1 --branch v0.6.3 https://github.com/openstreetmap/tirex.git
RUN cd tirex && make
RUN cd tirex && make install

# Fetch & install mod_tile
RUN git clone -b switch2osm https://github.com/SomeoneElseOSM/mod_tile.git
# Symlink the mason packages path because mod_tile ""assumes"" only the travis CI wants to build from source...
RUN /bin/bash -c 'mkdir -p /home/travis/build/mapbox/mason/ && ln -s /mapnik/mason_packages /home/travis/build/mapbox/mason/mason_packages'
RUN cd mod_tile && ./autogen.sh
RUN cd mod_tile && ./configure
RUN cd mod_tile && make
RUN cd mod_tile && make install
RUN cd mod_tile && make install-mod_tile

# Configure Tirex: create user and copy configs/maps
RUN useradd -M tirex && usermod -L tirex
RUN rm -rf /etc/tirex/renderer/mapnik && rm -rf /etc/tirex/renderer/openseamap/ && mkdir -p /etc/tirex/maps/
COPY ./mapnik_config /etc/tirex/renderer/mapnik
COPY ./mapnik_maps /etc/tirex/maps/mapnik
RUN echo "plugindir=/usr/local/lib/mapnik/input" >> /etc/tirex/renderer/mapnik.conf
RUN echo "fontdir=/usr/local/lib/mapnik/fonts" >> /etc/tirex/renderer/mapnik.conf

# Configure Tirex: create directories for each map config and update directory permissions
RUN cat /etc/tirex/renderer/mapnik/*.conf | rg -o "tiledir=(.+)" -r '$1' | xargs mkdir -p
RUN mkdir -p /var/run/tirex /var/log/tirex
RUN chown tirex:tirex -R /etc/tirex /var/lib/tirex /var/run/tirex /var/log/tirex

# Configure mod_tile
RUN ln -s /var/lib/tirex/tiles /var/lib/mod_tile
COPY ./config/simra-ubuntu.conf /etc/apache2/conf-enabled/

EXPOSE 80

COPY ./start.sh /usr/local/bin/
CMD /usr/local/bin/start.sh
