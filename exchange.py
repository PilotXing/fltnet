from exchangelib import Credentials, Account, Configuration, CalendarItem, Contact
from exchangelib.indexed_properties import EmailAddress, PhoneNumber
from exchangelib.errors import DoesNotExist
from checkcode import Configure
import datetime
from test import get_schedule, login_browser, get_crew_info, cvt_timedate

browser, session = login_browser()
my_schedules = get_schedule(session=session).json().get('records')

credentials = Credentials(
    username='hna.net\\{username}'.format(username=Configure.USERNAME),
    password=Configure.PASSWORD)

my_account = Account(
    credentials=credentials,
    autodiscover=True,
    primary_smtp_address='{username}@hnair.com'.format(username=Configure.USERNAME))


class Staff():
    def __init__(self,data) -> None:
        for key,value in data.items():
            setattr(self,key,value)
        self.email = self.loginId + '@hnair.com'

    def to_contact(self):
        if self.staffName != Configure.USERNAME_CN:
            try:
                res = my_account.contacts.get( given_name=self.staffName)
                print('contact found')
                body = res.body
                new_body = body+'\n' + \
                    self.flightDate+ self.flightNo
                res.body = new_body
                # res.save(update_fields=['body'])
            except DoesNotExist:
                print('not in contact')
                join_group_date = self.enterGroupDate[:-2]
                jgd = datetime.datetime.strptime(
                    join_group_date, '%Y-%m-%d %H:%M:%S').date()
                # create new
                contact = Contact(
                    folder=my_account.contacts,
                    account=my_account,
                    given_name=self.staffName,
                    display_name=self.staffName,
                    phone_numbers=[PhoneNumber(
                        label='MobilePhone',
                        phone_number=self.mobile
                    )],
                    job_title=self.techLevelName,
                    company_name='HNA',
                    body=self.flightDate + ' ' +
                    self.flightNo,
                    birthday=jgd
                )
                # contact.save()
                print(contact)


class Schedule():
    def __init__(self,data) -> None:
        for key,value in data.items():
            setattr(self,key,value)
        self.crews = self.__get_crews()

    def to_calendar(self):
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
        print(flight)
    
    def __get_crews(self):
        for crew_type in (1,2):
            crews = get_crew_info(session=session,
            fltInfo=self.__dict__,
            crewTypeId=crew_type)
        return crews.json().get('records')

    def save_crews(self):
        for data in self.crews:
            crew = Staff(data)
            print(crew.loginId)
            crew.to_contact()

if __name__ == '__main__':


    s = Schedule(my_schedules[0])
    # s.to_calendar()
    s.save_crews()
'''
for sch in my_schedules:
    # add schedule to calendar
    sign_up_time = sch.get('signUpEndTime')
    if sign_up_time:
        start = cvt_timedate(sign_up_time)
    else:
        start = cvt_timedate(sch.get('std'))
    end = cvt_timedate(sch.get('sta'))
    subject = sch.get('fltNo')+sch.get('acNo')+sch.get('sector')
    body = 'STD:'+sch.get('std') + '\n' + 'STA:'+sch.get('sta')
    flight = CalendarItem(
        account=my_account,
        folder=my_account.calendar,
        start=start,
        end=end,
        subject=subject,
        body=body,
        reminder_minutes_before_start=55)
    # flight.save()
    print(flight)

    # add contact
    for crewTypeId in range(1, 3):
        crews = get_crew_info(
            session=session,
            fltInfo=sch,
            crewTypeId=crewTypeId
        ).json().get('records')
        for crew in crews:
            print(crew)
            if crew.get('staffName') != Configure.USERNAME_CN:

                # if exist, update body
                try:
                    res = my_account.contacts.get(
                        given_name=crew.get('staffName'))
                    print('contact found')
                    body = res.body
                    new_body = body+'\n' + \
                        crew.get('flightDate') + ' ' + crew.get('flightNo')
                    res.body = new_body
                    res.save(update_fields=['body'])

                # if not exist, create new
                except DoesNotExist:
                    print('not in contact')
                    join_group_date = crew.get('enterGroupDate')[:-2]
                    jgd = datetime.datetime.strptime(
                        join_group_date, '%Y-%m-%d %H:%M:%S').date()
                    # create new
                    contact = Contact(
                        folder=my_account.contacts,
                        account=my_account,
                        given_name=crew.get('staffName'),
                        display_name=crew.get('staffName'),
                        phone_numbers=[PhoneNumber(
                            label='MobilePhone',
                            phone_number=crew.get('mobile')
                        )],
                        job_title=crew.get('techLevelName'),
                        company_name='HNA',
                        body=crew.get('flightDate') + ' ' +
                        crew.get('flightNo'),
                        birthday=jgd
                    )
                #   contact.save()
'''