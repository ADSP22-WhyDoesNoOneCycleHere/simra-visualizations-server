# SimRa Visualization

## Project Architecture

This project consists of three components:

- **importer:** Import csv files, generated by the SimRa smartphone applications into an postgreSQL database.
- **api:** Provide RESTful functionality.
- **simra-frontend:** A Vue.js application to allow for interaction with the data.

The following components are also needed:

- **Tirex:** A tileserver which renders tiles as PNGs which then can be served to the frontend.
- **postgreSQL:** The database.
- **Graphhopper:** Provides functionality to map match GPS data and to find the shortest route between two paths.

## Setup

A detailed setup guide can be found [here](SETUP_ARCH.md).