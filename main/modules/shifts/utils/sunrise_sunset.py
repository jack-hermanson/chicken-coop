import dataclasses
from datetime import datetime, timedelta
import requests
from dateutil import parser



@dataclasses.dataclass(frozen=True)
class SunriseSunset:
    sunrise_utc: datetime
    sunset_utc: datetime


def get_sunrise_sunset(date: datetime = None) -> SunriseSunset:
    if date is None:
        date = datetime.now()

    response = requests.get("https://api.sunrise-sunset.org/json", params={
        "lat": "39.737854126996005",
        "lng": "-104.97742350804769",
        "formatted": "0",
        "date": date.strftime("%Y-%m-%d"),
        "timezone": "America/Denver",
    })
    results = response.json().get("results")

    return SunriseSunset(
        sunrise_utc=parser.parse(results.get("sunrise")),
        sunset_utc=parser.parse(results.get("sunset"))
    )