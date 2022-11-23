import cv2
import pytesseract
import time
import datetime

class Schedule():
    def save_to_calendar():
        pass

class Configure:
    USERNAME = 'zih.xing'
    PASSWORD = 'xing314.'
    USERNAME_CN = '邢子辉2'
    screenshot = 'img/screenshot.png'


class Headers:
    headers = {
        'Uesr-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36'}


class Data:
    manual = {
        'companyCode': 'HNA',
        'manualCategory': None,
        'manualLevel': None,
        'firstTypeIds': None,
        'secondTypeIds': None,
        'thirdTypeIds': None,
        'subject': '737',
        'status': None,
        'statuses': 0,
        'statuses': 1,
        'page': 1,
        'start': 0,
        'limit': 10,
        'sort': [{"property": "publishDate", "direction": "DESC"}]
    }

    duty = {
        'viewtype': 'today',
        'showday': datetime.datetime.now().date().isoformat(),
        'planType': 0,
        'page': 1,
        'start': 0,
        'limit': 10,
        'sort': [{"property": "startTime", "direction": "ASC"}],
    }

    schedule = {
        "companyCode": " HNA",
        "lang": "zh",
        "planRange": "2",
        "planRange": "3",
        "planRange": "4",
        "planRange": "5",
        "planRange": "6",
        "psonType": "10",
        "psonType": "13",
        "psonType": "15",
        "psonType": "14",
        "planType": "1",
        "planTypeCheckbox": "1",
        "startDate": "2022-09-20",
        "endDate": "2022-10-11",
        "username": "1000804239",
        "returnNatResult": "1",
        "planRange1": "1",
        "companySites": "",
        "depAirportName": "",
        "arrAirportName": "",
        "acTypes": "",
        "acCode": "",
        "flightNo": "",
        "natResults": "",
        "parentTopicId": "",
        "rootTopicId": "",
        "flightType": "航班",
        "flightType": "航班坐车",
        "flightType": "坐飞机",
        "flightType": "应急备",
        "remark": "",
        "page": "1",
        "start": "0",
        "limit": "50",
    }


class Urls:
    login = 'https://sso.hnair.net/login?appid=fltnet-crew&service=https%3A%2F%2Ffltnet.hnair.net%2Fcrew%2Fj_spring_cas_security_check'
    duty = 'https://fltnet.hnair.net/crew/rest/pilot/home/tasks.json?_dc=' + \
        str(int(time.time()*1000))
    schedule = 'https://fltnet.hnair.net/crew/rest/assistant/flightPlan/dutyRoster.json?_dc=' + \
        str(int(time.time()*1000))

    crew = 'https://fltnet.hnair.net/crew/rest/pre/flightplan/query.json?_dc=' + \
        str(int(time.time()*1000)) + \
        '&flightDate={fltDate}&flightNo={fltNo}&sector={sector}&std={std}&crewTypeId={crewTypeId}&page=1&start=0&limit=10'

class Xpaths:
    fligths = '/html/body/div[4]/div[1]/div[2]/div[2]/div[1]/div[2]/div/div[2]/div/table/tbody/tr'
    popup = '//*[@id="close-popup-image-window"]'


def get_pdf(url, session, file):
    res = session.get(url)
    with open(file, 'wb') as f:
        for data in res.iter_content():
            f.write(data)


class Checkcode:
    def __init__(self, img):
        self.im = cv2.imread(img)

    def _preprocess(self):
        im = self.im[632:697, 1393:1547]
        # cv2.imshow('',im)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()
        im = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
        ret, im_bin = cv2.threshold(im, 127, 255, cv2.THRESH_BINARY)
        return im_bin

    def to_text(self):
        im_bin = self._preprocess()
        tesseract_config = "--psm 7 --oem 3 -c tessedit_char_whitelist=0123456789"
        res = pytesseract.image_to_string(
            im_bin, lang='eng', config=tesseract_config)
        return res



if __name__ == "__main__":
    cc = Checkcode('img/screenshot.png')
    text = cc.to_text()
    print(text)
    # print(Data.duty)
