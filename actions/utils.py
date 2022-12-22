
import csv
import pytz
import json
import requests
from dateutil import tz
from dateutil.parser import parse
from cachetools import cached, TTLCache
from datetime import date, datetime, timedelta
from googlesearch import search

base_url = 'https://raw.githubusercontent.com/CSSEGISandData/2019-nCoV/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_%s.csv'

class Utils:
    def __init__(self):
        pass

    def is_date(self, string, fuzzy=False):
        try:
            parse(string, fuzzy=fuzzy)
            return True
        except ValueError:
            return False

    def to_date(self, string, fuzzy=False):
        try:
            VN_TZ = tz.gettz('Asia/Ho_Chi_Minh')
            UTC = tz.gettz('UTC')
            date = parse(string, fuzzy=fuzzy).replace(tzinfo=UTC)
            return date.astimezone(VN_TZ)
        except ValueError:
            return ""

    def get_now(self):
        now = datetime.now(pytz.timezone('Asia/Ho_Chi_Minh'))
        return '{}/{}/{}'.format( now.day, now.month, now.year)

    def get_yesterday(self):
        yesterday = datetime.now(pytz.timezone('Asia/Ho_Chi_Minh')) - timedelta(days=1)
        return '{}/{}/{}'.format( yesterday.day, yesterday.month, yesterday.year)

    @cached(cache=TTLCache(maxsize=1024, ttl=3600))
    def get_data(self, category):
        """
        Retrieves the data for the provided type.
        """

        # Request the data
        request = requests.get(base_url % category)

        text = request.text
        # Parse the CSV.
        data = list(csv.DictReader(text.splitlines()))

        locations = []
        for item in data:
            # Filter out all the dates.
            history = dict(filter(lambda element: self.is_date(element[0]), item.items()))

            # Normalize the item and append to locations.
            locations.append({
                # General info.
                'country': item['Country/Region'],
                'province': item['Province/State'],

                # Coordinates.
                'coordinates': {
                    'lat': item['Lat'],
                    'long': item['Long'],
                },

                # History.
                'history': history,

                # Latest statistic.
                'latest': int(list(history.values())[-1]),

                # Latest datetime.
                'latest_date': self.to_date(list(history.keys())[-1]).strftime("%d/%m/%Y"),
            })

        # Latest total.
        latest = sum(map(lambda location: location['latest'], locations))
        vn_latest = sum([location['latest'] for location in locations if location['country'] == 'Vietnam'])
        # Return the final data.

        return {
            'locations': locations,
            'latest': latest,
            'vn_latest': vn_latest,
            'global_latest': latest - vn_latest,
            'latest_date': locations[0]['latest_date']
        }

    def get_province_data(self, id):
        url = 'https://covid19.ncsc.gov.vn/api/v3/covid/province/%s'
        request = requests.get(url % id)
        data = json.loads(request.text)
        return data

    def get_search(seft, loc, numResults = 5):
        text = ""
        result = search(loc, num_results = numResults, lang = "vi")
        if not result:
            text = ""
        else:
            text = "Bạn có thể tham khảo tại các trang:"
        for link in list(result)[:numResults]:
            text = "{}\n{}".format(text, link)

        return text