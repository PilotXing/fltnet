from checkcode import login_browser, get_schedule, Schedule
browser, session = login_browser()
schedules = get_schedule(session=session, show_day='2022-12-15')
for schedule in schedules:
    flight = Schedule(schedule, session=session)
    flight.to_calendar()
    # flight.remove_crews()
    flight.save_crews()
