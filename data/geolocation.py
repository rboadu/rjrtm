from abc import ABC, abstractmethod
import re


class GeoLocation(ABC):
    @abstractmethod
    def __init__(self, *args):
        print("Can't init this class!")

    def __str__(self):
        return self.location


LAT_MIN = -90
LAT_MAX = 90
LON_MIN = -180
LON_MAX = 180

MAX_DMS_LAT_DEG = 90
MAX_DMS_LON_DEG = 180
MIN_MINUTES = 0
MAX_MINUTES = 59
MIN_SECONDS = 0.0
MAX_SECONDS = 60.0  # exclusive

DMS_LAT_PATTERN = re.compile(r"^(\d+)°(\d+)'(\d+(?:\.\d+)?)\"([NS])$")
DMS_LON_PATTERN = re.compile(r"^(\d+)°(\d+)'(\d+(?:\.\d+)?)\"([EW])$")

TEST_LAT = 40.7128
TEST_LON = -74.0060
TEST_DMS_LAT = "40°42'46\"N"
TEST_DMS_LON = "74°0'22\"W"


class DecimalDegrees(GeoLocation):
    def __init__(self, lat: float, lon: float):
        if not isinstance(lat, (int, float)):
            raise TypeError(f'Bad type for lat: {type(lat)}')
        if not isinstance(lon, (int, float)):
            raise TypeError(f'Bad type for lon: {type(lon)}')
        if not (LAT_MIN <= lat <= LAT_MAX):
            raise ValueError(f'Latitude out of range: {lat=}')
        if not (LON_MIN <= lon <= LON_MAX):
            raise ValueError(f'Longitude out of range: {lon=}')
        self.lat = float(lat)
        self.lon = float(lon)
        self.location = f'{self.lat}, {self.lon}'


class DMSLocation(GeoLocation):
    def __init__(self, lat_dms: str, lon_dms: str):
        if not isinstance(lat_dms, str):
            raise TypeError(f'Bad type for lat_dms: {type(lat_dms)}')
        if not isinstance(lon_dms, str):
            raise TypeError(f'Bad type for lon_dms: {type(lon_dms)}')

        lat_match = DMS_LAT_PATTERN.match(lat_dms)
        if not lat_match:
            raise ValueError(f'Invalid DMS latitude format: {lat_dms=}')

        lon_match = DMS_LON_PATTERN.match(lon_dms)
        if not lon_match:
            raise ValueError(f'Invalid DMS longitude format: {lon_dms=}')

        lat_deg, lat_min, lat_sec, _ = lat_match.groups()
        lon_deg, lon_min, lon_sec, _ = lon_match.groups()

        lat_deg, lat_min, lat_sec = int(lat_deg), int(lat_min), float(lat_sec)
        lon_deg, lon_min, lon_sec = int(lon_deg), int(lon_min), float(lon_sec)

        if lat_deg > MAX_DMS_LAT_DEG:
            raise ValueError(f'DMS latitude degrees out of range: {lat_deg=}')
        if lon_deg > MAX_DMS_LON_DEG:
            raise ValueError(f'DMS longitude degrees out of range: {lon_deg=}')
        if not (MIN_MINUTES <= lat_min <= MAX_MINUTES):
            raise ValueError(f'DMS latitude minutes out of range: {lat_min=}')
        if not (MIN_MINUTES <= lon_min <= MAX_MINUTES):
            raise ValueError(f'DMS longitude minutes out of range: {lon_min=}')
        if not (MIN_SECONDS <= lat_sec < MAX_SECONDS):
            raise ValueError(f'DMS latitude seconds out of range: {lat_sec=}')
        if not (MIN_SECONDS <= lon_sec < MAX_SECONDS):
            raise ValueError(f'DMS longitude seconds out of range: {lon_sec=}')

        self.lat_dms = lat_dms
        self.lon_dms = lon_dms
        self.location = f'{lat_dms}, {lon_dms}'


def main():
    loc = DecimalDegrees(TEST_LAT, TEST_LON)
    print(loc)
    dms = DMSLocation(TEST_DMS_LAT, TEST_DMS_LON)
    print(dms)


if __name__ == '__main__':
    main()
