from exchangelib import Credentials, Account, Configuration, CalendarItem, Contact
from exchangelib.indexed_properties import EmailAddress, PhoneNumber
from exchangelib.errors import DoesNotExist
from checkcode import PASSWORD, Configure
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
