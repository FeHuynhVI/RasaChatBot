import random
import logging
import requests
import warnings
import wikipedia
from .utils import Utils
from bs4 import BeautifulSoup
from .constants import Constant
from rasa_sdk.events import SlotSet
from rasa_sdk import Action, Tracker
from typing import Any, Text, Dict, List
from rasa_sdk.executor import CollectingDispatcher
warnings.filterwarnings('ignore', message='Unverified HTTPS request')


logging.basicConfig(format='%(asctime)s - %(message)s',
                    datefmt='%d-%b-%y %H:%M:%S')

actionFormat = "Bạn phải yêu quê hương, tên tỉnh, thành phố, địa danh nên viết bông"

utils = Utils()
constants = Constant()
FOOD = constants.getFood()
PROVINCE = constants.getProvince()

reresolveProvinceOutput = "{}\nNgày {} có thêm {} ca hồi phục"
reDeathOutput = "Tổng sô ca tử vong: '{}' \nNgày ghi nhận '{}'"
numberOutPutException = "Bạn quay vào ô mất lượt. Xin cảm ơn!"
reconfirmOutput = "Tổng sô ca nhiễm bệnh: '{}' \nNgày ghi nhận '{}'"
redeathVietnameseProvinceDateOutput = "Tại Việt Nam\nTổng sô ca tử vong là: '{}' \nNgày ghi nhận '{}'"
reresolveVietnameseProvinceOutput = "Tại Việt Nam\nTổng sô ca hồi phục là: '{}' \nNgày ghi nhận '{}'"
reallProvinceLOutput_2 = "Ngày {}\n\tcó {} ca tử vong\n\tCó {} ca nhiễm mới\n\tCó thêm {} ca hồi phục"
reconfirmVietnameseProvinceOutput = "Tại Việt Nam\nTổng số ca nhiễm bệnh là: '{}' \nNgày ghi nhận '{}'"
redeathProvinceDateOutput = "{}\nĐến ngày '{}', Tổng số ca tử vong được ghi nhận là {}\nNgày {} có thêm {} ca tử vong"
reconfirmProvinceOutput = "{}\nĐến ngày '{}', Tổng số ca nhiễm bệnh được ghi nhận là {}\n Ngày {} có thêm {} ca nhiễm mới"
reallProvinceLOutput_1 = "{}\nĐến ngày '{}'\n\tTổng số ca tử vong được ghi nhận là {}\n\tTổng số ca nhiễm mới được ghi nhận là {}"
summaryOutput = "Ngày '{}' có tổng sô ca nhiễm bệnh: '{}' \nNgày '{}' có tổng số ca tử vong: '{}' \nNgày '{}' có tổng số ca hồi phục: '{}'"
reallVietnameseProvinceLOutput_2 = "Tại Việt Nam\nNgày '{}' có tổng số ca nhiễm bệnh: '{}' \nNgày '{}' có tổng số ca tử vong: '{}' \nNgày '{}' có tổng số ca hồi phục: '{}'"


class ActionHelloLoc(Action):

    def name(self) -> Text:
        return "action_get_loc"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        logging.info('Call action_get_loc')

        slot_name = tracker.get_slot("state")

        dispatcher.utter_message(
            text="So You Live In " + slot_name.title() + " , Here Are Your Location's Corona Stats: \n")

        return []


class ActionRecommend(Action):

    def name(self) -> Text:
        return "action_recommend_food"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        food = []

        logging.info('Call recommend food')

        for i in range(2):
            food_number = random.randrange(len(FOOD))
            food.append(FOOD[food_number])

        dispatcher.utter_message(
            text="Em nghĩ hôm nay anh chị có thể thử món '{}' hoặc bên cạnh đó cũng có thể là món '{}' ạ".format(food[0], food[1]))

        return []


class ActionRedeath(Action):

    def name(self) -> Text:
        return "action_redeath"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        logging.info('Call action_redeath')

        dataD = utils.get_data('deaths_global')

        dispatcher.utter_message(text=reDeathOutput.format(
            dataD['vn_latest'], dataD['latest_date']))

        return []


class ActionReconfirm(Action):

    def name(self) -> Text:
        return "action_reconfirm"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        logging.info('Call action_reconfirm')

        dataC = utils.get_data('confirmed_global')

        dispatcher.utter_message(text=reconfirmOutput.format(
            dataC['vn_latest'], dataC['latest_date']))

        return []


class ActionRerecovered(Action):

    def name(self) -> Text:
        return "action_rerecovered"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        logging.info('Call action_rerecovered')

        dataR = utils.get_data('recovered_global')

        dispatcher.utter_message(text="Tổng sô ca khỏi bênh: '{}' \nNgày ghi nhận '{}'".format(
            dataR['vn_latest'], dataR['latest_date']))

        return []


class ActionSummaryCovid(Action):
    def name(self) -> Text:
        return "action_summary_covid"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        logging.info('Call action_summary_covid')

        dataD = utils.get_data('deaths_global')
        dataC = utils.get_data('confirmed_global')
        dataR = utils.get_data('recovered_global')
        dispatcher.utter_message(text=summaryOutput.format(
            dataC['latest_date'], dataC['vn_latest'], dataD['latest_date'], dataD['vn_latest'], dataR['latest_date'], dataR['vn_latest']))

        return []


class act_number_domestic(Action):

    def name(self) -> Text:
        return "actions_corona_state_stat"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        logging.info('Call actions_corona_state_state')

        url = 'https://ncov.moh.gov.vn/web/guest/trang-chu'

        print('[%s] <- %s' % (self.name(), tracker.latest_message['text']))

        page = requests.get(url, verify=False)

        soup = BeautifulSoup(page.text, 'html.parser')

        try:

            domestic = soup.find_all("table", id='sailorTable')[
                                     0].find_all("tr")

            all_of_it = "CHI TIẾT TÌNH HÌNH COVID-19 TRONG NƯỚC"

            data = None
            for d_row in domestic:
                d_col = d_row.find_all("td")
                data = []
                for el in d_col:
                    data.append(str(el.text))

                if len(data) >= 5:
                    all_of_it += ("\n▪ %s - Nhiễm: %s - Điều trị: %s - Khỏi: %s - Tử vong: %s" % (
                        data[0], data[1], data[2], data[3], data[4]))  # test

            all_of_it += "\nNguồn tin: Bộ Y Tế(https://moh.gov.vn/)"

            del domestic, data

        except Exception as err:
            logging.error('Call actions_corona_state_state error: {0}'.format(err))
            all_of_it = numberOutPutException

        del url, page, soup

        dispatcher.utter_message(text=all_of_it)

        return []


class ActionWeatherTracker(Action):

    def name(self) -> Text:
        return "action_weather_tracker"

    def run(self, dispatcher: CollectingDispatcher,
             tracker: Tracker,
             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        logging.info('Call action_weather_tracker')
        API_KEY = "7b8c2098b1f741169ea43408220112&aqi=no"
        BASE_URL = "https://api.weatherapi.com/v1/current.json?"

        try:
            loc = tracker.get_slot('location')

            if (loc is None):
                dispatcher.utter_message(text=actionFormat)

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

                message = "Thời tiết " + city + ":" + "\n" "Nhiệt độ = " + str(temp_cel) + " Độ C" + "\n" "Áp suất không khí (in hPa unit) = " + str(pressure) + "\n""Humidity (in percentage) = " + str(humidity) + "\n"

            dispatcher.utter_message(text=message)

        except Exception as err:

            logging.error('Call action_weather_tracker error: {0}'.format(err))

            dispatcher.utter_message(text=numberOutPutException)

        return [SlotSet('location', loc)]


class ActionWikipediaTracker(Action):
    wikipedia.set_lang("vi")

    def name(self) -> Text:
        return "action_wiki_pedia_tracker"

    def run(self, dispatcher: CollectingDispatcher,
             tracker: Tracker,
             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        logging.info('Call action_wiki_pedia_tracker')

        try:
            loc = tracker.get_slot('location')

            if (loc is None):
                dispatcher.utter_message(text=actionFormat)

            result = wikipedia.summary(loc, sentences= 3)

            if not result:
                resultSearch = wikipedia.search(loc, results= 1)
                if len(resultSearch):
                    result = wikipedia.summary(resultSearch[0], sentences= 3)

            dispatcher.utter_message(text=result)

        except Exception as err:
            logging.error('Call action_wiki_pedia_tracker error: {0}'.format(err))

            dispatcher.utter_message(text=numberOutPutException)

        return [SlotSet('location', loc)]


class ActionRedeathProvince(Action):

    def name(self) -> Text:
        return "action_redeath_province"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        logging.info('Call action_redeath_province')

        try:
            loc = tracker.get_slot('location')

            if (loc is None):
                dispatcher.utter_message(text=actionFormat)

            loc = loc.lower()

            if (loc in PROVINCE.keys()):
                dataLocD = utils.get_province_data(PROVINCE[loc])
                yesterday = utils.get_yesterday()
                text = redeathProvinceDateOutput.format(dataLocD['name'], utils.get_now(
                ), dataLocD['total_death'], yesterday, dataLocD['death_by_day'][yesterday])
            else:
                dataD = utils.get_data('deaths_global')
                text = redeathVietnameseProvinceDateOutput.format(
                    dataD['vn_latest'], dataD['latest_date'])

            dispatcher.utter_message(text)
        except Exception as err:
            logging.error('Call action_redeath_province error: {0}'.format(err))
            
            dispatcher.utter_message(text=numberOutPutException)
            
        return []


class ActionReconfirmProvince(Action):

    def name(self) -> Text:
        return "action_reconfirm_province"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        logging.info('Call action_reconfirm_province')

        try:
            loc = tracker.get_slot('location')

            if (loc is None):
                dispatcher.utter_message(text=actionFormat)

            loc = loc.lower()
            if (loc in PROVINCE.keys()):
                dataLocD = utils.get_province_data(PROVINCE[loc])
                yesterday = utils.get_yesterday()
                text = reconfirmProvinceOutput.format(dataLocD['name'], utils.get_now(
                ), dataLocD['total_case'], yesterday, dataLocD['case_by_day'][yesterday])
            else:
                dataD = utils.get_data('confirmed_global')
                text = reconfirmVietnameseProvinceOutput.format(
                    dataD['vn_latest'], dataD['latest_date'])

            dispatcher.utter_message(text)
        except Exception as err:
            logging.error('Call action_reconfirm_province error: {0}'.format(err))

            dispatcher.utter_message(text=numberOutPutException)
        return []


class ActionReresolveProvince(Action):

    def name(self) -> Text:
        return "action_reresolve_province"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        logging.info('Call action_reresolve_province')

        try:
            loc = tracker.get_slot('location')

            if (loc is None):
                dispatcher.utter_message(text=actionFormat)

            loc = loc.lower()

            if (loc in PROVINCE.keys()):
                dataLocD = utils.get_province_data(PROVINCE[loc])
                yesterday = utils.get_yesterday()
                text = reresolveProvinceOutput.format(
                    dataLocD['name'], yesterday, dataLocD['recovered_by_day'][yesterday])
            else:
                dataD = utils.get_data('recovered_global')
                text = reresolveVietnameseProvinceOutput.format(
                    dataD['vn_latest'], dataD['latest_date'])

            dispatcher.utter_message(text)
        except Exception as err:
            logging.error('Call action_reresolve_province error: {0}'.format(err))

            dispatcher.utter_message(text=numberOutPutException)
        return []


class ActionReallProvince(Action):

    def name(self) -> Text:
        return "action_reall_province"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        logging.info('Call action_reall_province')

        try:
            loc = tracker.get_slot('location')

            if (loc is None):
                dispatcher.utter_message(text=actionFormat)

            loc = loc.lower()
            if (loc in PROVINCE.keys()):
                dataLocD = utils.get_province_data(PROVINCE[loc])
                yesterday = utils.get_yesterday()
                text1 = reallProvinceLOutput_1.format(dataLocD['name'], utils.get_now(
                ), dataLocD['total_death'], dataLocD['total_case'])
                text2 = reallProvinceLOutput_2.format(
                    yesterday, dataLocD['death_by_day'][yesterday], dataLocD['case_by_day'][yesterday], dataLocD['recovered_by_day'][yesterday])
                text = "{}\n{}".format(text1, text2)
            else:
                dataD = utils.get_data('deaths_global')
                dataC = utils.get_data('confirmed_global')
                dataR = utils.get_data('recovered_global')
                text = reallVietnameseProvinceLOutput_2.format(
                    dataC['latest_date'], dataC['vn_latest'], dataD['latest_date'], dataD['vn_latest'], dataR['latest_date'], dataR['vn_latest'])

            dispatcher.utter_message(text)
        except Exception as err:
            logging.error('Call action_reresolve_province error: {0}'.format(err))

            dispatcher.utter_message(text=numberOutPutException)
        return []
