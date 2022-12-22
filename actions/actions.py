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
reDeathOutput = "Ở Việt Nam:\nTổng sô ca tử vong: '{}' \nNgày ghi nhận '{}'"
numberOutPutException = "Bạn quay vào ô mất lượt. Xin cảm ơn!"
reconfirmOutput = "Ở Việt Nam:\nTổng sô ca nhiễm bệnh: '{}' \nNgày ghi nhận '{}'"
redeathVietnameseProvinceDateOutput = "Tại Việt Nam\nTổng sô ca tử vong là: '{}' \nNgày ghi nhận '{}'"
reresolveVietnameseProvinceOutput = "Tại Việt Nam\nTổng sô ca hồi phục là: '{}' \nNgày ghi nhận '{}'"
reallProvinceLOutput_2 = "Ngày {}\n\tcó {} ca tử vong\n\tCó {} ca nhiễm mới\n\tCó thêm {} ca hồi phục"
reconfirmVietnameseProvinceOutput = "Tại Việt Nam\nTổng số ca nhiễm bệnh là: '{}' \nNgày ghi nhận '{}'"
redeathProvinceDateOutput = "{}\nĐến ngày '{}', Tổng số ca tử vong được ghi nhận là {}\nNgày {} có thêm {} ca tử vong"
reconfirmProvinceOutput = "{}\nĐến ngày '{}', Tổng số ca nhiễm bệnh được ghi nhận là {}\n Ngày {} có thêm {} ca nhiễm mới"
reallProvinceLOutput_1 = "{}\nĐến ngày '{}'\n\tTổng số ca tử vong được ghi nhận là {}\n\tTổng số ca nhiễm được ghi nhận là {}"
summaryOutput = "Ở Việt Nam:\nNgày '{}' có tổng sô ca nhiễm bệnh: '{}' \nNgày '{}' có tổng số ca tử vong: '{}' \nNgày '{}' có tổng số ca hồi phục: '{}'"
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

        dispatcher.utter_message(text="Ở Việt Nam:\nTổng sô ca khỏi bênh: '{}' \nNgày ghi nhận '{}'".format(
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
        loc = tracker.get_slot('location')
        logging.info("{}{}".format('Call action_redeath_province: ', loc))

        try:
            if (loc):
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
        loc = tracker.get_slot('location')
        logging.info("{}{}".format('Call action_reconfirm_province: ', loc))

        try:
            if (loc):
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
        loc = tracker.get_slot('location')
        logging.info("{}{}".format('Call action_reresolve_province: ', loc))

        try:
            if (loc):
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
        loc = tracker.get_slot('location')
        logging.info("{}{}".format('Call action_reall_province: ', loc))

        try:

            if (loc):
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
            logging.error('Call action_reall_province error: {0}'.format(err))

            dispatcher.utter_message(text=numberOutPutException)
        return []

class ActionGgSearch(Action):

    def name(self) -> Text:
        return "action_gg_search"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        logging.info('action_gg_search')

        try:
            message = tracker.latest_message["text"]
            print(message)
            text = utils.get_search(message)
            dispatcher.utter_message(text)
        except Exception as err:
            logging.error('Call action_gg_search error: {0}'.format(err))
            dispatcher.utter_message(text=numberOutPutException)
        return []

class ActionCoronaSymptoms(Action):
    def name(self) -> Text:
        return "action_corona_symptoms"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        logging.info('action_corona_symptoms')

        try:
            message = """
Tùy theo thể trạng và sức đề kháng, triệu chứng nhiễm corona qua từng ngày của mỗi cá thể là khác nhau, tuy nhiên những triệu chứng này đều biểu hiện rõ từ 2-14 ngày. Do đó, ngay khi có các dấu hiệu nghi ngờ, người bệnh cần đến ngay các cơ sở y tế gần nhất để được chẩn đoán kịp thời.

Ngày 1 đến ngày 3:

Dấu hiệu giống bệnh cảm thông thường.
Viêm họng nhẹ, không sốt, không mệt mỏi.
Ăn uống và hoạt động bình thường.
Ngày 4:

Cổ họng bắt đầu đau nhẹ, người lờ đờ.
Bắt đầu khan tiếng.
Nhiệt độ cơ thể tăng nhẹ.
Đau đầu nhẹ, tiêu chảy nhẹ.
Bắt đầu chán ăn.
Ngày 5:

Đau họng nhiều hơn, khan tiếng nhiều hơn.
Nhiệt độ cơ thể tăng nhẹ
Cơ thể mệt mỏi, đau nhức các khớp xương.
Ngày 6:

Triệu chứng của virus Corona 2019 là bắt đầu sốt nhẹ.
Ho có đàm hoặc ho khan không đàm.
Đau họng nhiều hơn, đau khi nuốt nước bọt, khi ăn hoặc nói.
Cơ thể mệt mỏi, buồn nôn.
Tiêu chảy, có thể nôn ói.
Lưng hoặc ngón tay đau nhức.
Ngày 7:

Sốt cao dưới 38o.
Ho nhiều hơn, đàm nhiều hơn.
Toàn thân đau nhức.
Khó thở.
Tiêu chảy và nôn ói nhiều hơn.
Ngày 8:

Sốt khoảng trên dưới 38o.
Khó thở, hơi thở khò khè, nặng lồng ngực.
Ho liên tục, đàm nhiều, tắt tiếng.
Đau khớp xương, đau đầu, đau lưng.
Ngày 9:

Các tình trạng như sốt, ho, khó thở, nặng lồng ngực… trở nên nặng nề hơn.
"""

            dispatcher.utter_message(message)
            dispatcher.utter_message("https://vnvc.vn/virus-corona-2019/")
        except Exception as err:
            logging.error('Call action_corona_symptoms error: {0}'.format(err))
            dispatcher.utter_message(text=numberOutPutException)
        return []

class ActionCoronaDangerous(Action):

    def name(self) -> Text:
        return "action_corona_dangerous"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        logging.info('action_corona_dangerous')

        try:
            message = """
Người nhiễm COVID-19 nhiều tuần đến nhiều tháng sau khi khỏi bệnh vẫn còn đối mặt với hàng loạt triệu chứng và di chứng kéo dài như sốt nhẹ, khó thở, ho kéo dài, mệt mỏi, đau cơ, khớp, rụng tóc, xơ phổi, tim đập nhanh hoặc đánh trống ngực, rối loạn nội tiết, huyết học bị huyết khối… Có trường hợp xuất hiện rối loạn tiêu hóa (ăn không ngon miệng, chán ăn, đau dạ dày, tiêu chảy…), rối loạn vị giác hoặc khứu giác, phát ban…
Người bệnh trong giai đoạn hậu COVID-19 cũng có thể gặp các triệu chứng về tâm thần kinh như rối loạn tâm lý, giảm sự tập trung, lo âu, trầm cảm, bồn chồn, rối loạn giấc ngủ, mau quên, không tập trung. Thường xuất hiện tình trạng não sương mù, nhận thức kém, đọc chậm, giảm trí nhớ ngắn hạn, thay đổi tâm trạng.
Với người có sẵn bệnh nền như bệnh tim mạch, tiểu đường, đặc biệt là hô hấp, viêm phổi tắc nghẽn mạn tính COPD, viêm phế quản mạn… khi COVID-19 xảy ra trên nền bệnh đó có thể khiến tổn thương vốn có của họ trở nên nặng hơn.
"""
            dispatcher.utter_message(message)
            text = utils.get_search("tác hại của covid đối với con người")
            dispatcher.utter_message(text)
        except Exception as err:
            logging.error('Call action_corona_dangerous error: {0}'.format(err))
            dispatcher.utter_message(text=numberOutPutException)
        return []

class ActionCoronaDetermined(Action):

    def name(self) -> Text:
        return "action_corona_determined"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        logging.info('action_corona_determined')

        try:
            message = """Một số dấu hiệu giúp bạn nhận ra bản thân có thể đã mắc Covid là:
        Cơ thể có biểu hiện ngạt mũi, nghẹn ở họng và lồng ngực dẫn đến khó thở.
        Ho khan hoặc ho có đờm, đau rát cổ họng khả năng cao là triệu chứng sau khi virus tấn công vào phổi. Đối với tình trạng ho do Covid, các loại thuốc điều trị thông thường sẽ không có tác dụng.
        Sốt, mệt mỏi là dấu hiệu sớm và xuất hiện ở rất nhiều bệnh nhân Covid, đây cũng là triệu chứng được sử dụng để sàng lọc các ca nhiễm Covid trong cộng đồng.
        Ngoài ra, những trường hợp mắc Covid hiện nay còn có thể có triệu chứng tức ngực, đau đầu, mệt mỏi, chóng mặt, tim đập nhanh, chán ăn, tiêu chảy,…
"""
            dispatcher.utter_message(message)
            text = utils.get_search("Dấu hiệu nhận biết bản thân bị nhiễm Covid")
            dispatcher.utter_message(text)
        except Exception as err:
            logging.error('Call action_corona_determined error: {0}'.format(err))
            dispatcher.utter_message(text=numberOutPutException)
        return []

class ActionCoronaService(Action):

    def name(self) -> Text:
        return "action_corona_service"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        logging.info('action_corona_service')

        try:
            message = "Bạn có thể liên hệ đường dây nóng hỗ trợ covid để hỗ trợ"
            dispatcher.utter_message(message)
            text = utils.get_search("tổng đài tư vấn covid việt nam")
            dispatcher.utter_message(text)
        except Exception as err:
            logging.error('Call action_corona_service error: {0}'.format(err))
            dispatcher.utter_message(text=numberOutPutException)
        return []
