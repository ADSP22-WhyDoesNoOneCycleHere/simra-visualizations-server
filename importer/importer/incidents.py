import csv

from datetime import datetime
from postgis import Point


def handle_incidents(data, filename, cur):
    data = csv.DictReader(data[1:], delimiter=",")
    filename = filename.split("/")[-1]
    pLoc = -1
    incidents = []
    for row in data:
        rideTimestamp = datetime.utcfromtimestamp(int(row.get("ts", 0) or 0) / 1000)
        temp_bikeType = row.get("bike", -1)
        if isinstance(temp_bikeType, Integer):
            bikeType = temp_bikeType
        else:
            bikeType = 0

        childCheckbox = row.get("childCheckBox", 0) == "1"
        trailerCheckbox = row.get("trailerCheckBox", 0) == "1"
        temp_pLoc = row.get("pLoc", -1)
        if isinstance(temp_pLoc, Integer):
            pLoc = temp_pLoc
        else:
            pLoc = 0

        incident = row.get("incident", -1)
        if not incident:
            incident = -1
        iType = -1
        i = 1
        while f"i{i}" in row:
            if row[f"i{i}"] == "1":
                iType = i
                break
            i += 1
        scary = row.get("scary", 0) == "1"
        desc = row.get("desc", "")
        geom = Point(row.get("lon", 0) or 0, row.get("lat", 0) or 0, srid=4326)
        cur.execute("""
            INSERT INTO public."SimRaAPI_incident" ("rideTimestamp", "bikeType", "childCheckbox", "trailerCheckbox", "pLoc", "incident", "iType", "scary", "desc", "filename", "geom") VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id
        """, [rideTimestamp, bikeType, childCheckbox, trailerCheckbox, pLoc, incident, iType, scary, desc, filename, geom])
        incident_id = cur.fetchone()
        incidents.append((geom, scary, incident_id))
    return int(pLoc), incidents


def update_ride_ids(incident_ids, ride_id, cur):
    for incident_id in incident_ids:
        cur.execute("""
                    UPDATE public."SimRaAPI_incident" SET ride_id = %s WHERE id = %s
                """, [ride_id, incident_id])
