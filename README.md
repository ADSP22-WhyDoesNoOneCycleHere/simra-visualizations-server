# SimRa Visualization

This project is part of the SimRa research project which includes the following subprojects:

- [simra-android](https://github.com/simra-project/simra-android/): The SimRa app for Android.
- [simra-ios](https://github.com/simra-project/simra-ios): The SimRa app for iOS.
- [backend](https://github.com/simra-project/backend): The SimRa backend software.
- [dataset](https://github.com/simra-project/dataset): Result data from the SimRa project.
- [screenshots](https://github.com/simra-project/SimRa-Visualization): Screenshots of both the iOS and Android app.
- SimRa-Visualization: Web application for visualizing the dataset([frontend](https://github.com/simra-project/simra-visualization-web), [backend](https://github.com/simra-project/simra-visualizations-server)).

In this project, we collect – with a strong focus on data protection and privacy – data on such near crashes to identify when and where bicyclists are especially at risk. We also aim to identify the main routes of bicycle traffic in Berlin. To obtain such data, we have developed a smartphone app that uses GPS information to track routes of bicyclists and the built-in acceleration sensors to pre-categorize near crashes. After their trip, users are asked to annotate and upload the collected data, pseudonymized per trip. For more information see [our website](https://www.digital-future.berlin/en/research/projects/simra/).

## Project Architecture

This project consists of three components:

- [**importer:**](https://github.com/KrokodileDandy/simra-visualizations-server/tree/develop/importer) Import csv files, generated by the SimRa smartphone applications into an postgreSQL database.
- [**api:**](https://github.com/KrokodileDandy/simra-visualizations-server/tree/develop/api) Provide RESTful functionality.

The following components are also needed:

- [**Tirex:**](https://github.com/openstreetmap/tirex) A tileserver which renders tiles as PNGs which then can be served to the frontend.
- **postgreSQL:** The database.
- [**Graphhopper:**](https://github.com/graphhopper/map-matching) Provides functionality to map match GPS data and to find the shortest route between two paths.

## Setup

A detailed setup guide for Arch linux systems can be found [here](SETUP_ARCH.md).
