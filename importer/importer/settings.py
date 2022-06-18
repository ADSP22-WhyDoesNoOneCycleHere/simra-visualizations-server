import logging

# Possible debug levels are CRITICAL, ERROR, WARNING, INFO and DEBUG.
logging.basicConfig(
    level=logging.WARNING, format="%(levelname)s - %(module)s - %(message)s"
)

# The directory to import the SimRa generated CSV files from.
IMPORT_DIRECTORY = "importer/resources"

# PostgreSQL database connection parameters.
DB_HOST = "127.0.0.1"
DB_NAME = "simra"
DB_USER = "simra"
DB_PASSWORD = "simra12345simra"
DB_PORT = 5432

MIN_ACCURACY = float("inf")
RDP_EPSILON = 0.000005

MIN_RIDE_DISTANCE = 200  # in meters
MIN_RIDE_DURATION = 3 * 60  # in seconds
MAX_RIDE_AVG_SPEED = 40  # in km/h
MIN_DISTANCE_TO_COVER_IN_5_MIN = 100  # in meters

COVERED_DISTANCE_INSIDE_STOP_THRESHOLD = 0.5  # in meters
DISTANCE_TO_JUNCTION_THRESHOLD = 30  # in meters

COVERED_DISTANCE_INSIDE_STOP_FOR_VELOCITY_THRESHOLD = (
    4.2  # in meters. ≈ 5km/h with a resolution of 1coord/3secs
)

GET_ALL_SURFACE_SCORES = False

# Percentage at which an alternate route is counted as a detour. E.g.
# 0.1 for when an alternative route can cover 10% more length before
# it is considered as a detour.
DETOUR_THRESHOLD_PERCENT = 0.1
DETOUR_THRESHOLD_METER = 10

logging.info("Loaded")
