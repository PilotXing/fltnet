#!usr/local/bin/python3
import cv2
import pytesseract
import time
import pytz
from exchangelib.errors import DoesNotExist
import datetime
from exchangelib import Credentials, Account, CalendarItem, Contact
from exchangelib.indexed_properties import EmailAddress, PhoneNumber
from curses import KEY_ENTER
import requests
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from config import USERNAME,PASSWORD,USERNAME_CN


class Configure:
    USERNAME = USERNAME
    PASSWORD = PASSWORD
    USERNAME_CN = USERNAME_CN
    screenshot = 'img/screenshot.png'


def time_mark():
    return str(int(time.time()*1000))


class Urls:
    login = 'https://sso.hnair.net/login?appid=fltnet-crew&service=https%3A%2F%2Ffltnet.hnair.net%2Fcrew%2Fj_spring_cas_security_check'
    duty = 'https://fltnet.hnair.net/crew/rest/pilot/home/tasks.json?_dc=' + \
        str(int(time.time()*1000))
    schedule = 'https://fltnet.hnair.net/crew/rest/assistant/flightPlan/dutyRoster.json?_dc=' + \
        str(int(time.time()*1000))
    crew = 'https://fltnet.hnair.net/crew/rest/pre/flightplan/query.json?_dc=' + \
        str(int(time.time()*1000)) + \
        '&flightDate={fltDate}&flightNo={fltNo}&sector={sector}&std={std}&crewTypeId={crewTypeId}&page=1&start=0&limit=10'
    # crew = 'https://fltnet.hnair.net/crew/rest/pre/flightplan/query.json'
    cfp = 'https://fltnet.hnair.net/opm/rest/flight-info/getDownloadUrl.json?_dc=' + \
        str(int(time.time()*1000))
    staff_info = 'https://fltnet.hnair.net/crew/rest/pilot/pcenter/pbaseinfo/querypersoninfo.json?_dc=' + \
        time_mark()+'&staffNo={staffId}&companyNodeId=9'
    hours = 'https://fltnet.hnair.net/crew/rest/pilot/pcenter/flyHistory/queryPilotTotalFlyTimes.json?_dc=' +\
        time_mark()+'&staffNo={staffId}&page=1&start=0&limit=10'


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
        # 'showday': '2022-11-17',
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
        "startDate": "2022-10-25",
        "endDate": "2022-11-23",
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


class Xpaths:
    fligths = '/html/body/div[4]/div[1]/div[2]/div[2]/div[1]/div[2]/div/div[2]/div/table/tbody/tr'
    popup = '//*[@id="close-popup-image-window"]'


credentials = Credentials(
    username='hna.net\\{username}'.format(username=Configure.USERNAME),
    password=Configure.PASSWORD)

my_account = Account(
    credentials=credentials,
    autodiscover=True,
    primary_smtp_address='{username}@hnair.com'.format(username=Configure.USERNAME))


def cvt_timedate(str):

    tz_cn = pytz.timezone('Asia/Shanghai')
    if str:
        nontz_timedate = datetime.datetime.strptime(str, '%Y-%m-%d %H:%M:%S')
        tz_timedate = tz_cn.localize(nontz_timedate)
        return tz_timedate


def get_schedule(session,show_day=None):
    print(show_day)
    Data.duty['showday'] = show_day if show_day else Data.duty['showday']
    print(Data.duty['showday'])
    res = session.post(url=Urls.duty, headers=Headers.headers, data=Data.duty)
    return res.json().get('records')


# def get_crew_info(session, fltInfo, crewTypeId):
#     params = {
#         # '_dc' :str(int(time.time()*1000)),
#         'fltDate': fltInfo.get('fltDate'),
#         'fltNo': fltInfo.get('fltNo'),
#         'sector': fltInfo.get('sector'),
#         'std': fltInfo.get('std'),
#         'crewTypeId':crewTypeId,
#         # 'page':1,
#         # 'start':0,
#         # 'limit':10
#     }
#     crews = session.get(url=Urls.crew, headers=Headers.headers, params=params)
#     return crews
def get_crew_info(session, fltInfo, crewTypeId):
    fltDate = fltInfo.get('fltDate')
    fltNo = fltInfo.get('fltNo')
    sector = fltInfo.get('sector')
    std = fltInfo.get('std')
    crew_url = Urls.crew.format(
        fltDate=fltDate,
        fltNo=fltNo,
        sector=sector,
        std=std,
        crewTypeId=crewTypeId)
    crews = session.get(url=crew_url, headers=Headers.headers)
    return crews


def login_browser():

    browser = webdriver.Chrome(executable_path="./chromedriver")
    browser.set_window_size(1280, 720)

    # login
    browser.get(Urls.login)
    browser.save_screenshot('img/screenshot.png')
    cc = Checkcode('img/screenshot.png').to_text()
    browser.find_element(By.ID, value='username').send_keys(Configure.USERNAME)
    browser.find_element(By.ID, value='password').send_keys(Configure.PASSWORD)
    browser.find_element(By.ID, value='rand').send_keys(cc, KEY_ENTER)
    time.sleep(5)  # wait page load
    browser.find_element(
        By.XPATH, value='//*[@id="close-popup-image-window"]').click()

    # set cookies
    cookies = browser.get_cookies()
    session = requests.session()
    for cookie in cookies:
        session.cookies.set(cookie['name'], cookie['value'])
    return browser, session


def get_pdf(url, session, file):
    res = session.get(url)
    with open(file, 'wb') as f:
        for data in res.iter_content():
            f.write(data)


class Staff():
    def __init__(self, data, session) -> None:
        for key, value in data.items():
            setattr(self, key, value)
        self.session = session
        self.email = self.loginId + '@hnair.com'
        self.experiance_hours = None
        self.total_hours = None
        self.contact, self.is_new_contact = None, None

    def get_contact(self):
        # exclude myself
        # if self.staffName != Configure.USERNAME_CN:
            # if exists, update body, append flight No. & date to body
            # if does not exist, create new contact
        try:
            contact = my_account.contacts.get(given_name=self.staffName)
            print('contact found')
            body = contact.body or ''
            new_body = body+'\n'+'{flightDate}/{flightNo}/{sector}/{experiance_hours}'.format(
                flightDate=self.flightDate, flightNo=self.flightNo[2:], sector=self.sector, experiance_hours=self.experiance_hours)
            contact.body = new_body
            print(new_body)
            # self.contact.save(update_fields=['body'])

            self.contact, self.is_new_contact = contact, 0
            return 0

        except DoesNotExist:
            print('not in contact')
            join_group_date = self.enterGroupDate[:-2]
            jgd = datetime.datetime.strptime(
                join_group_date, '%Y-%m-%d %H:%M:%S').date()
            # create new
            # TODO get photo of staff
            contact = Contact(
                folder=my_account.contacts,
                account=my_account,
                given_name=self.staffName,
                display_name=self.staffName,
                phone_numbers=[PhoneNumber(
                    label='MobilePhone',
                    phone_number=self.mobile
                )],
                department=self.deptName,
                nickname=self.staffId,
                job_title=self.rankSd,
                company_name='HNA',
                body='{flightDate}/{flightNo}/{sector}/{experiance_hours}'.format(
                    flightDate=self.flightDate, flightNo=self.flightNo[2:], sector=self.sector, experiance_hours=self.experiance_hours),
                birthday=jgd,
                email_addresses=[EmailAddress(
                    label='EmailAddress1', email=self.email)]
            )
            self.contact, self.is_new_contact = contact, 1
            return 1 

    def to_contact(self):
        self.get_contact()
        if self.is_new_contact:
            self.contact.save()
            print('new')
        else:
            self.contact.save(update_fields=['body'])
            print('updated')

    def remove(self):
        try:
            res = my_account.contacts.get(given_name=self.staffName)
            res.delete()
        except:
            pass


class Flight_crew(Staff):
    def __init__(self, data, session) -> None:
        super().__init__(data, session)
        self.experiance_hours = self.get_hours().get('totalThroughTime')
        self.total_hours = self.get_hours().get('totalFlyTime')
        print(self.total_hours,self.experiance_hours)

    def get_hours(self):
        return self.session.get(url=Urls.hours.format(staffId=self.staffId), headers=Headers.headers).json()[0].get('commonTotalFlyTime')


class Cabin_crew(Staff):
    def __init__(self, data, session) -> None:
        super().__init__(data, session)
        self.experiance_hours = None
        self.total_hours = None


class Schedule():
    def __init__(self, fligth_info, session) -> None:
        for key, value in fligth_info.items():
            setattr(self, key, value)
        self.session = session
        self.flight_crews = []
        self.cabin_crews = []
        for crew in  self.get_crews().get('flight_crews'):
            self.flight_crews.append(Flight_crew(crew,session=session))
        for crew in self.get_crews().get('cabin_crews'):
            self.cabin_crews.append(Cabin_crew(crew,session=session))
        self.calendar = self.get_calendar()

    def get_calendar(self):
        sign_up_time = self.signUpEndTime
        if sign_up_time:
            start = cvt_timedate(sign_up_time)
        else:
            start = cvt_timedate(self.std)
        end = cvt_timedate(self.sta)
        subject = self.fltNo+self.acNo+self.sector
        body = 'STD:'+self.std + '\n' + 'STA:'+self.sta
        flight = CalendarItem(
            account=my_account,
            folder=my_account.calendar,
            start=start,
            end=end,
            subject=subject,
            body=body,
            reminder_minutes_before_start=55)
        # flight.save()
        return flight

    def to_calendar(self):
        self.calendar.save()

    def is_in_calendar(self):
        return 0

    def get_crews(self):
        cabin_crews = get_crew_info(
            session=self.session, fltInfo=self.__dict__, crewTypeId=2).json().get('records')
        fligth_crews = get_crew_info(
            session=self.session, fltInfo=self.__dict__, crewTypeId=1).json().get('records')
        # crews = cabin_crews+fligth_crews
        # for crew_type in (1, 2):
        #     crews = get_crew_info(session=self.session,
        #                           fltInfo=self.__dict__,
        #                           crewTypeId=crew_type)
        # return crews.json().get('records')
        return {
            'cabin_crews': cabin_crews,
            'flight_crews': fligth_crews}

    def save_flight_crews(self):
        for crew in self.flight_crews:
            # crew = Flight_crew(data=crew_info, session=self.session)
            crew.to_contact()

    def save_cabin_crews(self):
        for crew in self.cabin_crews:
            # crew = Cabin_crew(data=crew_info, session=self.session)
            crew.to_contact()

    def save_crews(self):
        if not self.is_in_calendar():
            self.save_cabin_crews()
            self.save_flight_crews()

    def remove_crews(self):
        for crew in self.flight_crews+self.cabin_crews:
            print('{} removed'.format(crew.staffName))
            crew.remove()


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
