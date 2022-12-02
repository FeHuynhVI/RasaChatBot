from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import random

import requests
import csv
from cachetools import cached, TTLCache
from dateutil.parser import parse
from dateutil import tz
from rasa_sdk.events import SlotSet
import wikipedia

# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/core/actions/#custom-actions/


# This is a simple example for a custom action which utters "Hello World!"
from bs4 import BeautifulSoup
import urllib.request
import ssl
import json
import os
import html
import random
import pathlib

from rasa_sdk.events import FollowupAction

import warnings

warnings.filterwarnings('ignore', message='Unverified HTTPS request')

"""
Base URL for fetching data.
"""
base_url = 'https://raw.githubusercontent.com/CSSEGISandData/2019-nCoV/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_%s.csv';

def is_date(string, fuzzy=False):
    try:
        parse(string, fuzzy=fuzzy)
        return True
    except ValueError:
        return False

def to_date(string, fuzzy=False):
    try:
        VN_TZ = tz.gettz('Asia/Ho_Chi_Minh')
        UTC = tz.gettz('UTC')
        date = parse(string, fuzzy=fuzzy).replace(tzinfo=UTC)
        return date.astimezone(VN_TZ)
    except ValueError:
        return ""

@cached(cache=TTLCache(maxsize=1024, ttl=3600))
def get_data(category):
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
        history = dict(filter(lambda element: is_date(element[0]), item.items()))

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
            'latest_date': to_date(list(history.keys())[-1]).strftime("%d/%m/%Y"),
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


DATABASE = ["bún đậu mắm tôm",
            "bún đậu nước mắm",
            "bún cá",
            "bún hải sản",
            "cơm văn phòng",
            "cơm sườn",
            "xôi",
            "bún ốc",
            "mì vằn thắn",
            "hủ tiếu",
            "bún chả",
            "bún ngan",
            "ngan xào tỏi",
            "bún bò huế",
            "mì tôm hải sản",
            "bánh mì trứng xúc xích rắc thêm ít ngải cứu",
            "bánh mì trứng",
            "bánh mì xúc xích",
            "bánh mì pate"]

class ActionHelloLoc(Action):

    def name(self) -> Text:
        return "action_get_loc"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        slot_name = tracker.get_slot("state")

        print("slotname", slot_name)

        dispatcher.utter_message(
            text="So You Live In " + slot_name.title() + " , Here Are Your Location's Corona Stats: \n")

        return []

class ActionRecommend(Action):

    def name(self) -> Text:
        return "action_recommend"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        food = []
        for i in range(2):
            food_number = random.randrange(len(DATABASE))
            food.append(DATABASE[food_number])

        dispatcher.utter_message(
            text="Em nghĩ hôm nay anh chị có thể thử món '{}' hoặc bên cạnh đó cũng có thể là món '{}' ạ".format(food[0], food[1]))

        return []
        
        
class ActionRedeath(Action):

    def name(self) -> Text:
        return "action_redeath"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        dataD = get_data('deaths_global')
        
        dispatcher.utter_message(
            text="Tổng sô người mất: '{}' \nNgày ghi nhận '{}'".format(dataD['vn_latest'], dataD['latest_date']))

        return []

class ActionReconfirm(Action):

    def name(self) -> Text:
        return "action_reconfirm"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        dataC = get_data('confirmed_global')
        
        dispatcher.utter_message(
            text="Tổng sô ca nhiễm bệnh: '{}' \nNgày ghi nhận '{}'".format(dataC['vn_latest'], dataC['latest_date']))

        return []
        
        
class ActionRerecovered(Action):

    def name(self) -> Text:
        return "action_rerecovered"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        dataR = get_data('recovered_global')
        
        dispatcher.utter_message(
            text="Tổng sô ca khỏi bênh: '{}' \nNgày ghi nhận '{}'".format(dataR['vn_latest'], dataR['latest_date']))

        return []
        
class ActionSummary(Action):
    def name(self) -> Text:
        return "action_summary"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
            
        dataD = get_data('deaths_global')
        dataC = get_data('confirmed_global')
        dataR = get_data('recovered_global')
        dispatcher.utter_message(
            text="Ngày '{}' có tổng sô ca nhiễm bệnh: '{}' \nNgày '{}' có tổng số ca tử vong: '{}' \nNgày '{}' có tổng số ca hồi phục: '{}'".format(dataC['latest_date'], dataC['vn_latest'], dataD['latest_date'], dataD['vn_latest'], dataR['latest_date'], dataR['vn_latest']))

        return []


class act_number_domestic(Action):

    def name(self) -> Text:
        return "actions_corona_state_stat"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        print('[%s] <- %s' % (self.name(), tracker.latest_message['text']))
        url = 'https://ncov.moh.gov.vn/web/guest/trang-chu'
        page = requests.get(url, verify=False)
        soup = BeautifulSoup(page.text, 'html.parser')
        #mydict = None

        try:

            domestic = soup.find_all("table", id='sailorTable')[0].find_all("tr")

            # print(domestic)
            all_of_it = "🇻🇳CHI TIẾT TÌNH HÌNH COVID-19 TRONG NƯỚC"

            data = None
            for d_row in domestic:
                print("--")
                d_col = d_row.find_all("td")
                data = []
                for el in d_col:
                    # print(el.text)
                    data.append(str(el.text))
                # print(data[0])
                if len(data) >= 5:
                    all_of_it += ("\n▪ %s - Nhiễm: %s - Điều trị: %s - Khỏi: %s - Tử vong: %s" % (
                        data[0], data[1], data[2], data[3], data[4]))  # test

            all_of_it += "\nNguồn tin: Bộ Y Tế(https://moh.gov.vn/)"

            del domestic, data

        except:
            all_of_it = "Dịch vụ xin tạm ngưng để bảo trì. Xin cảm ơn!"

        del url, page, soup

        dispatcher.utter_message(
            text=all_of_it
        )

        return []


class ActionWeatherTracker(Action):

     def name(self) -> Text:
        return "action_weather_tracker"

     def run(self, dispatcher: CollectingDispatcher,
             tracker: Tracker,
             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

         try:
            loc = tracker.get_slot('location')
            BASE_URL = "https://api.weatherapi.com/v1/current.json?"
            API_KEY = "7b8c2098b1f741169ea43408220112&aqi=no"
            URL = BASE_URL + "q=" + loc + "&key=" + API_KEY
            response = requests.get(URL)
            if response.status_code == 200:
                data = response.json()
                main = data['current']
                city = loc
                temperature = main['temp_f']
                temp_cel = main["temp_c"]
                humidity = main['humidity']
                pressure = main['pressure_mb']

                message = "Thời tiết " + city + ":" + "\n" "Nhiệt độ = " + str(temp_cel) + " Độ C" + "\n" "Áp suất không khí (in hPa unit) = " +str(pressure) + "\n""Humidity (in percentage) = " +str(humidity) + "\n"

            dispatcher.utter_message(text=message)

         except Exception as err:
            error = "Lỗi call action: " +  err
            dispatcher.utter_message(text=error)

         return [SlotSet('location',loc)]


class ActionWikipediaTracker(Action):
     wikipedia.set_lang("vi")
     def name(self) -> Text:
        return "action_wiki_pedia_tracker"

     def run(self, dispatcher: CollectingDispatcher,
             tracker: Tracker,
             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

         try:
            loc = tracker.get_slot('location')

            result = wikipedia.summary(loc, sentences = 3)

            if not result:
                resultSearch = wikipedia.search(loc, results = 1)
                if len(resultSearch):
                    result = wikipedia.summary(resultSearch[0], sentences = 3)


            dispatcher.utter_message(text=result)

         except Exception as err:
            error = "Lỗi call action: " +  err
            dispatcher.utter_message(text=error)

         return [SlotSet('location',loc)]