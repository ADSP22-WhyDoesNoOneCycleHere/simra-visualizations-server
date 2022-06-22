- [Setup on Ubuntu18.04.5](#setup-on-ubuntu18.04)
  - [Python](#python)
  - [PostgreSQL Database](#postgresql-database)
  - [Django](#django)
  - [Graphhopper](#graphhopper)
  - [Initial database population](#initial-database-population)
  - [Run the importer](#run-the-importer)

# Setup on Ubuntu Linux

1. Generally execute all commands from inside the main directory unless stated otherwise

2. Make sure all your packages are up to date.

```
sudo apt update -y && sudo apt upgrade -y
```

## Python

1. Install Python 3.8 and python development headers: 
```
sudo apt install -y python3.8 python3.8-dev
```


2. Change the python command to point towards Python 3.8 instead of Python 2:
```
sudo update-alternatives --remove python /usr/bin/python2
```
```
sudo update-alternatives --install /usr/bin/python python /usr/bin/python3.8 10 # sets Python3.8 as default Python
```


3. Install pip for python 3.8
```
sudo apt remove python-pip  # removes existing pip version
```
```
pip --version # returns module not installed
```
```
sudo apt install -y python3-pip  # installs pip for Python 3.6
```
```
python -m pip install pip # installs pip for Python 3.8
```


4. After that, set your `~/.local/bin/` directory in the `PATH` variable. To do so, open `~./bashrc` (or your respective shell configuration file) and paste the following at the end of the file:
```
# set PATH so it includes user's private bin if it exists
if [ -d "$HOME/.local/bin" ] ; then
    PATH="$HOME/.local/bin:$PATH"
fi
```

5. Now restart the terminal or execute `source ~/.bashrc` and check whether the installation was successful with `pip --version` which should return some pip version.

(Steps taken from [this](https://stackoverflow.com/questions/63207385/how-do-i-install-pip-for-python-3-8-on-ubuntu-without-changing-any-defaults) tutorial.)


## PostgreSQL Database

1. Install Postgres && Postgis
```
sudo apt install -y postgresql postgresql-contrib
```
```
sudo apt install -y postgis
```


2. Start the server (**Different on WSL**) and setup the user and database
```
sudo systemctl start postgresql.service # (When on WSL use "sudo service postgresql start" instead)
```
```
sudo -u postgres createuser simra
```
```
sudo -u postgres createdb simra
```
```
sudo -u postgres psql # enters psql as user postgres
```

3. Execute the following commands in psql:
```
alter user simra with encrypted password 'simra12345simra';
```
```
grant all privileges on database simra to simra;
```
```
alter role simra superuser;
```
```
create extension postgis;
```
```
select PostGIS_full_version();
```	

4. To quit the CLI, type `\q` and press enter. (2x)

(The steps above where taken from [this](https://medium.com/coding-blocks/creating-user-database-and-adding-access-on-postgresql-8bfcd2f4a91e) tutorial.)

We recommend the tool pgAdmin4 for managing the PostgreSQL database because it allows for geo data visualization. It can be installed, following [this tutorial](https://www.pgadmin.org/download/pgadmin-4-apt/).



## Django
_Notice: At this point the Postgres server should be running._ 

Now that the database is set up, we will create database models which will define the form of the database tables which will be filled later. For that, the project uses the django framework.

1. Install django
```
pip install django
```

2. Install some packages needed to install the other required packages
```
sudo apt install -y libgpgme-dev python-apt python3-testresources
```
```
sudo apt-get install -y libpq-dev python-dev pkg-config libcairo2-dev
```
```
sudo apt-get install -y libffi6 libffi-dev swig
```

3. Install all packages of requirement.txt
```
pip install -r requirements.txt # installs other needed packages
```

4. Run `api/manage.py` (if necessary, remove `api/SimRaAPI/migrations/`):

```
python api/manage.py makemigrations SimRaAPI
```
```
python api/manage.py migrate
```
```
python api/manage.py runserver
```


## Graphhopper

This component is used to determine the shortest routes between two GPS coordinates as well as to map match the raw GPS data onto a map

1. Download the Graphhopper web server

```
sudo wget https://github.com/graphhopper/graphhopper/releases/download/5.3/graphhopper-web-5.3.jar -P ./graphhopper/
```

2. Download street map data for Berlin and DACH-Region (we really only use Berlin but the DACH data is used in graphhopper.conf atm)
```
sudo mkdir -p /var/simra/pbf
```
```
sudo wget https://download.geofabrik.de/europe/germany/berlin-latest.osm.pbf -P /var/simra/pbf/
```
```
sudo wget https://download.geofabrik.de/europe/dach-latest.osm.pbf -P /var/simra/pbf/
```

3. Install java and start the web server (Error handling in Step 5):
```
sudo apt install -y default-jdk
```
```
sudo java -jar ./graphhopper/graphhopper-web-5.3.jar server ./graphhopper/config.yml
```

4. **Make sure the server has completely started before populating the db. This may take a while as it will create a graph inside `graph-cache/`.**

5. If you encounter a Java heap exception, you need to give java more RAM to start the server
```
export JAVA_OPTS="-Xmx10g -Xms10g"  # This gives java a minimum and maximum of 10gigs ram.
```
5.1. Delete the graph-cache/ directory and start the server again.


## Initial database population
_Notice: At this point the Postgres server, the Django server and the Graphhopper server should be running._ 

We use the tool [Imposm](https://imposm.org/docs/imposm3/latest/) to fill our database with basic map data from the OSM database.

1. Install Imposm
```
sudo wget "https://github.com/omniscale/imposm3/releases/download/v0.10.0/imposm-0.10.0-linux-x86-64.tar.gz"
```
```
tar -xf imposm-0.10.0-linux-x86-64.tar.gz # unpack
```

2. Execute Imposm
```
sudo ./imposm-0.10.0-linux-x86-64/imposm import -mapping mapping.yml -read "/var/simra/pbf/berlin-latest.osm.pbf" -overwritecache -write -connection postgis://simra:simra12345simra@localhost/simra
```

This created the schema `import` with the table `osm_ways` which is used in the next step by the `create_legs.py` script. Then we import the csv data into our database.


## Run the importer
_Notice: At this point the Postgres server, the Django server and the Graphhopper server should be running._ 

Next, the existing map data is separated into legs which represent single street segments of the street network. 

1. Execute importer/importer/create_legs.py to fill the database tables `OsmWaysLegs`, `OsmWaysJunctions` and `OsmWaysLargeJunctions` inside the schema `public` of the `simra` database.
```
python importer/importer/create_legs.py
```

2. Execute importer/importer/import.py to import the CSV data into the database. This will import all files that are in subdirectories of importer/resources
**Attention, depending on the amount of data which is imported, this process can take a while. To test if your setup is working we highly recommend to test with a small amount of CSV files.**
```
python importer/importer/import.py
```



### Everything after this has not been updated!

## Setup apache2

Install the web server by executing `sudo apt install apache2 apache2-dev`. Checking the status of the server with `systemctl status apache2` should yield `active (running)`. If not, start the web server manually via `sudo systemctl start apache2`.

Now copy `simra-ubuntu.conf` into `/etc/apache2/mods-available`: `sudo cp ./tileserver/config/simra-ubuntu.conf /etc/apache2/mods-available`. Next we system link the config file to `/etc/apache2/mods-enabled`: `sudo ln -s /etc/apache2/mods-available/simra-ubuntu.conf /etc/apache2/mods-enabled`. Apache2 will automatically look into these directories and read those configurations. Lastly restart the service via `sudo systemctl restart apache2`.

## Setup mod_tile

This package is a module for the Apache web server. If not done yet, add the OSM PPA to the OS: `sudo add-apt-repository -y ppa:osmadmins/ppa`. Now the installation is possible straight forward by executing `sudo apt-get install -y libapache2-mod-tile`. Lastly execute `sudo ln -s /var/lib/tirex/tiles /var/lib/mod_tile` to create a system link.

## Setup Mapnik and tirex

Clone the mapnik repository via `git clone https://github.com/mapnik/mapnik` and enter the `mapnik/` directory.

```
# you might have to update your outdated clang
sudo add-apt-repository -y ppa:ubuntu-toolchain-r/test
sudo apt-get update -y

# https://askubuntu.com/questions/509218/how-to-install-clang
# Grab the key that LLVM use to GPG-sign binary distributions
wget -O - https://apt.llvm.org/llvm-snapshot.gpg.key | sudo apt-key add -
sudo apt-add-repository "deb http://apt.llvm.org/bionic/ llvm-toolchain-bionic-6.0 main"
sudo apt-get install -y gcc-6 g++-6 clang-6.0 lld-6.0
export CXX="clang++-6.0" && export CC="clang-6.0"


# Install mapnik
git clone https://github.com/mapnik/mapnik mapnik
cd mapnik
git checkout v3.0.x
git submodule update --init
sudo apt-get install zlib1g-dev clang make pkg-config curl
source bootstrap.sh
./configure CUSTOM_CXXFLAGS="-D_GLIBCXX_USE_CXX11_ABI=0" CXX=${CXX} CC=${CC}
make -j 3 # Uses 3 CPU cores
make test # This yields 6 errors if your OS username is not 'simra' but you can ignore them.
sudo make install
```

Install `python-mapnik` by using apt: `sudo apt install python-mapnik`. _Attention!_ This could yield errors, as this is probably not meant for mapnik 3.0.x!

For tirex we first need a new user:

```
sudo useradd -M tirex
sudo usermod -L tirex
```

Install Tirex by executing the following lines:

```
# Meet missing dependencies
sudo apt install devscripts

# Install Perl modules
sudo cpan IPC::ShareLite JSON GD LWP
sudo cpan CPAN # Updates to newer cpan

# Install, build and install Tirex
git clone git@github.com:openstreetmap/tirex.git
make
sudo make install
```

Check whether `/etc/tirex/` and `/usr/lib/tirex/` exist. If not, something went wrong and you should restart the Tirex setup.

Tirex needs some additional directories to run, so create them now: `sudo mkdir /var/lib/tirex/ /var/run/tirex/ /var/log/tirex/`

Next, run `chown tirex:tirex -R /var/lib/tirex/ /var/run/tirex/ /usr/lib/tirex/ /var/log/tirex/ /etx/tirex/` to allocated respective rights for the user `tirex`.

Now, remove the initial Mapnik directory of Tirex via `sudo rmdir /etc/tirex/renderer/mapnik`. Create a symlink to this repositories folder `tileserver/mapnik_config/` instead, e.g. `sudo ln -s /home/sfuehr/Documents/TUB-WI/S7_BA_SimRa/simra-visualizations-server/tileserver/mapnik_config /etc/tirex/renderer/mapnik`. **Be sure that the path to `mapnik_config/` does not contain spaces!**

Next, remove all content from the `openseamap/` directory via `sudo rm -r /etc/tirex/renderer/openseamap/*`.

Execute `sudo mkdir /var/lib/tirex/tiles` to create the Tirex tiles folder and for each config file in `tileserver/mapnik_config/` create a folder of the same name in `/var/lib/tirex/tiles/`: `sudo mkdir incident-combined popularity-combined relative-speed-aggregated relative-speed-single rides-density_all rides-density_rushhourevening rides-density_rushhourmorning rides-density_weekend rides-original stoptimes surface-quality-aggregated surface-quality-single popularity-score popularity-combined popularity-original_avoided popularity-original_chosen popularity_w-incidents_combined popularity_w-incidents_score popularity-original_w-incidents_avoided popularity-original_w-incidents_chosen`. Grant permission via `sudo chown tirex:tirex -R /var/lib/tirex`.

Then copy the service files `tirex-backend-manager.service` and `tirex-master.service` into the systems service folder. Both service files can be found inside the directory `tileserver/config/` inside this repository.

```
sudo cp ./tileserver/config/tirex-master.service /etc/systemd/system
sudo cp ./tileserver/config/tirex-backend-manager.service /etc/systemd/system
```

Grant this permission: `sudo chown tirex:tirex -R /var/run/tirex`.

Finally, update `/etc/tirex/renderer/mapnik.conf`: `plugindir` should be `/usr/local/lib/mapnik/input` and `fontdir` should be `/usr/local/lib/mapnik/fonts`.

In your `mapnik_config/` directory change the `mapfile` variable to point towards the map files inside `mapnik_maps/`.

Now you can start the Tirex services: `sudo systemctl start tirex-master` and `sudo systemctl start tirex-backend-manager`.



## Rendering Map Tiles

Now that everything is set up, the data in the database can be rendered into PNG images which are used by the Tirex tile server. To do so execute `tirex-batch map=rides-original bbox=11.642761,51.894292,15.135040,53.006521 z=0-10`. You can monitor this process by calling `tirex-status` in another terminal instance.

Attention, depending on the amount of data which is imported, this process can take a while.

# List of known issues

For detailed feedback, the following commands may be useful:

- `tirex-status`
- `tirex-status --once --extended`
- `journalctl -xe`
- For development and easier use of Tirex related task, check out the `tirex` bash script in `util/`. To view available commands and options execute `./util/tirex.sh -h`.

For some of the components mentioned above, detailed setup instructions can be found [here](https://ircama.github.io/osm-carto-tutorials/tile-server-ubuntu/).

The directory `/var/run/tirex/` is deleted on every shutdown of the machine. Thus, `sudo mkdir /var/run/tirex/` and `chown tirex:tirex -R /var/run/tirex/` have to be repeated. You can provide a shell script to do so in your autostart directory.
