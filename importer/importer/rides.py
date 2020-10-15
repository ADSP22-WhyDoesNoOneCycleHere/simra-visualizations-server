import incidents
import csv
from postgis import LineString
from datetime import datetime, timedelta
from db_connection import DatabaseConnection
import filters
import map_match_service
import leg_service
import stop_service
import math

def handle_ride_file(filename, cur):
    with open(filename, 'r') as f:
        incident_list = []
        ride = []
        split_found = False
        for line in f.readlines():
            if "======" in line:
                split_found = True
                continue
            if not split_found:
                incident_list.append(line)
            else:
                ride.append(line)
        incidents.handle_incidents(incident_list, filename, cur)
        handle_ride(ride, filename, cur)


def handle_ride(data, filename, cur):
    data = csv.DictReader(data[1:], delimiter=",")

    raw_coords = []
    accuracies = []
    timestamps = []
    accelerations = []

    for row in data:
        if row["lat"]:
            raw_coords.append([float(row["lon"]), float(row["lat"])])
            try:
                if row["acc"]:
                    accuracies.append(float(row["acc"]))
            except KeyError:
                return
            timestamps.append(datetime.utcfromtimestamp(int(row["timeStamp"]) / 1000))  # timeStamp is in Java TS Format
        if row["X"]:
            accelerations.append((float(row["X"]), float(row["Y"]), float(row["Z"]), datetime.utcfromtimestamp(int(row["timeStamp"])/1000), raw_coords[-1]))
    ride = Ride(raw_coords, accuracies, timestamps)

    first_five_seconds = []
    for X, Y, Z, ts, coords in accelerations:
        if ts - accelerations[0][3] > timedelta(seconds = 5):
            break
        first_five_seconds.append((X, Y, Z))

    A5 = [sum(y) / len(y) for y in zip(*first_five_seconds)]  # get average of accelerations in first 5 seconds of ride

    sliding_window_size = 15  # seconds per direction
    every_x_seconds = 5
    current_max_idx = 0
    IRI = []
    in_window = []
    for i in range(len(accelerations)):
        current = accelerations[i]
        ts = current[3]
        if IRI and (ts - IRI[-1][1]).total_seconds() < every_x_seconds:
            continue
        while in_window and ts - in_window[0][3] > timedelta(seconds = sliding_window_size):
            in_window.remove(in_window[0])
        while current_max_idx < len(accelerations) and accelerations[current_max_idx][3] - ts < timedelta(seconds=sliding_window_size):
            A = accelerations[current_max_idx][:-2]
            avs = (A[0] * A5[0] + A[1] * A5[1] + A[2] * A5[2]) / math.sqrt(A5[0]**2 + A5[1]**2 + A5[2]**2)
            if len(in_window) > 1:
                dt = (in_window[-1][3] - in_window[-2][3]).total_seconds()
            else:
                dt = 0.1
            in_window.append(accelerations[current_max_idx] + (abs(avs * dt**2 / 2),))
            current_max_idx += 1
        lon1, lat1 = in_window[0][4]
        lon2, lat2 = in_window[-1][4]
        Sh = get_distance(in_window[0][4], in_window[-1][4])
        true_timedelta = in_window[-1][3] - in_window[0][3]
        true_timedelta = true_timedelta.total_seconds()
        if Sh > 0:
            iri = sum(list(zip(*in_window))[5]) / Sh
            IRI.append((iri, ts, current[4], Sh))

    if len(ride.raw_coords) == 0:
        return

    ride = filters.apply_smoothing_filters(ride)
    if filters.apply_removal_filters(ride):
        return

    map_matched = map_match_service.map_match(ride)

    legs = leg_service.determine_legs(map_matched, cur)
    leg_service.update_legs(ride, legs, cur, IRI)

    stop_service.process_stops(ride, cur)

    ls = LineString(ride.raw_coords_filtered, srid=4326)
    filename = filename.split("/")[-1]

    try:
        cur.execute("""
            INSERT INTO public."SimRaAPI_ride" (geom, timestamps, legs, filename) VALUES (%s, %s, %s, %s)
        """, [ls, timestamps, [i[0] for i in legs], filename])
    except:
        print(f"Problem parsing {filename}")
        raise Exception("Can not parse ride!")


def get_distance(p1, p2):
    lon1, lat1 = p1[0] * math.pi / 180, p1[1] * math.pi / 180
    lon2, lat2 = p2[0] * math.pi / 180, p2[1] * math.pi / 180
    Sh = 2 * 6371000 * math.asin(math.sqrt(math.sin((lon2 - lon1)/2)**2 + math.cos(lon1) * math.cos(lon2) * math.sin((lat2 - lat1)/2)**2))
    return Sh

if __name__ == '__main__':
    filepath = "../csvdata/Berlin/Rides/VM2_-351907452"
    with DatabaseConnection() as cur:
        handle_ride_file(filepath, cur)


class Ride:
    def __init__(self, raw_coords, accuracies, timestamps):
        self.raw_coords = raw_coords
        self.raw_coords_filtered = None
        self.accuracies = accuracies
        self.timestamps = timestamps
        self.timestamps_filtered = None
