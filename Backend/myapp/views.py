from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import *
# from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
# Create your views here.
import os.path
from datetime import datetime, timedelta
from django.shortcuts import render

from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import TimeTable
from .api.serializers import TimeTableSerializer
from rest_framework import status

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# authenticates us to connect with google calendar api 
def calenderAccessAuth():
    print('Hello')
    SCOPES = ["https://www.googleapis.com/auth/calendar"]
    creds = None
    if os.path.exists("token.json"):
        print('exists')
    try:
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    except Exception as e:
        print("An error occurred while loading credentials:", e)
    print(creds)
    print('exe')
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        print('Why Here')
        if creds and creds.expired and creds.refresh_token:
            print("here2")
            creds.refresh(Request())
        else:
            print("here3")
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())
        print(1)
        print(creds)
        print(2)
    return creds

#connects to calendar
def connectToCalender(joining_yr, department):
    creds = calenderAccessAuth()
    yrs=['2021','2022','2023','2024']
    calenders=['20d93d2fe1b0ecd1544f1a2b2b108da8e96af9ff12241d7492c3d65b24238790@group.calendar.google.com','42d1535640fbdeb2c505ba9b52315343dc907a3b2f91d4b9645b9b3805804828@group.calendar.google.com','aa4783b76409e5b9f2557220593a81e47854cb1f8692abe0a10754a7fde96202@group.calendar.google.com','a925c86f766b09ffa88d867653cafe9d55aaece2843c7f23657823807b2de584@group.calendar.google.com','41071f57b3a292eaa22f30e3f138487c6629af8d4504e280ea66ae2e4b99e65b@group.calendar.google.com','b4f926456995f1ce8e90e4038597f600fec71ca73c0745a0e56098dfacddc4c4@group.calendar.google.com','343a067515a7b486410df769c83cc58ec72b3b27bfeb68399c197b9ff448c09b@group.calendar.google.com','cefe6f3824e000eed77be01be2f930e92038c80b0a0e62bd56063e976aa85721@group.calendar.google.com']
    dept_mapping={'cse': 0,'ece':4}
    idx=dept_mapping[department.lower()]+yrs.index(joining_yr)
    print(idx)
    calender_id=calenders[idx]
#     calender_id = '5cc47411b973f0be87683f090d88df0dbd791532b2990b02c89153f1e9b5e2bc@group.calendar.google.com'
    service = build("calendar", "v3", credentials=creds)
    return service, calender_id


# when time table is being added first time in database calendar event gets created  
def calenderMainTableAdd(joining_yr,department, day, s1, s2, s3, s4, s5, s6, s7):
    # inputs from frontend``
    # summary_list = ['ES101', None, None, None, None, None, None]
    # day = 'tuesday'
    summary_list = [s1, s2, s3, s4, s5, s6, s7]

    slot_to_time = [['09:20', '10:10'], ['10:10', '11:00'], ['11:20', '12:10'], [
        '12:10', '13:00'], ['14:00', '14:50'], ['14:50', '15:40'], ['16:00', '16:50']]
    # byday_list=['MO','TU','WE','TH','FR']
    byday_dict = {'monday': 'MO', 'tuesday': 'TU',
                  'wednesday': 'WE', 'thursday': 'TH', 'friday': 'FR'}
    today = start_day = datetime.now().date()
    while start_day.strftime('%A').lower() != day:
        start_day += timedelta(days=1)
    end_date = today + timedelta(days=130)

    try:
        service, calender_id = connectToCalender(joining_yr=joining_yr, department=department)
        for i in range(7):
            if len(summary_list[i]) != 0:
                timezone_offset = timedelta(hours=-7)
                start_datetime = str(datetime.combine(start_day, datetime.strptime(
                    slot_to_time[i][0], '%H:%M').time()).isoformat())
                end_datetime = str(datetime.combine(start_day, datetime.strptime(
                    slot_to_time[i][1], '%H:%M').time()).isoformat())
                print(start_datetime)
                print(end_datetime)
                recurrence_rule = f'RRULE:FREQ=WEEKLY;BYDAY={byday_dict[day]};UNTIL={end_date.strftime("%Y%m%d")}'
                event = {
                    'summary': summary_list[i],
                    'start': {'dateTime': start_datetime, 'timeZone': 'Asia/Kolkata', },
                    'end': {'dateTime': end_datetime, 'timeZone': 'Asia/Kolkata', },
                    'recurrence': [recurrence_rule],
                }
                event = service.events().insert(calendarId=calender_id, body=event).execute()
                print('Event created: %s' % (event.get('htmlLink')))
    except HttpError as error:
        print(f"An error occurred: {error}")

def getAllEvents():
    # THIS FUNCTION IS NOT NEEDED ANYMORE
    # need to think of a starting datetime sa that only that sem events are loaded..

    # input
    joining_yr='2021'
    department = 'cse'

    service, calender_id = connectToCalender(joining_yr, department)
    page_token = None
    while True:
        events = service.events().list(calendarId=calender_id,
                                       pageToken=page_token).execute()
        for event in events['items']:
            print(event['id'], event['summary'])
        page_token = events.get('nextPageToken')
        if not page_token:
            break


#this function has no followup written
def getEventsOnCond(date,course_code,joining_yr,department):
    #Function is to get the slots(starting time) for given date and course_code
    #inputs include date, course_code
    #output is list

#     sem = 0
#     department = 'cse'
    
#     date = datetime.strptime(date, '%Y-%m-%d').date()
    print('date1')
    print(date)
    date = datetime.strptime(date, '%d-%m-%Y').date()
    print(date)
    service, calender_id = connectToCalender(joining_yr, department)
    page_token = None
    slots_today=[]
    print('inside get event on cond')
    
    while True:
        events = service.events().list(calendarId=calender_id,
                                       pageToken=page_token, singleEvents=True).execute()
        for event in events['items']:
            if date != None:
                if event['start']['dateTime'][:10] == str(date)[:10] and event['summary']==course_code:
                            print(event['start']['dateTime'])
                            slots_today.append(event['start']['dateTime'][11:16])
        page_token = events.get('nextPageToken')
        slots_today.sort()
        print(slots_today)
        if not page_token:
            break
    return slots_today



def deleteAllEvents(joining_yr, department):
    # NOT NEEDED ANYMORE
    service, calender_id = connectToCalender(joining_yr=joining_yr, department=department)
    page_token = None
    while True:
        events = service.events().list(calendarId=calender_id,
                                       pageToken=page_token).execute()
        for event in events['items']:
            service.events().delete(calendarId=calender_id,
                                    eventId=event['id']).execute()
        page_token = events.get('nextPageToken')
        if not page_token:
            break


# def AddOrChangeEvent(date, time_slot, new_summary):

#     # input
#     # date = datetime.today()
#     semester = 0
#     department = 'cse'
#     # time_slot = '09:20-10:10'
#     # new_summary = 'NEW SUMMARY'

#     # change time from '09:20-10:10' format to '<date>T09:20:00'
#     start_datetime = date+'T'+time_slot[:5]
#     print(start_datetime)

#     service, calender_id = connectToCalender(semester, department)
#     # get event_id
#     page_token = None
#     event_id = None
#     print('outside while')
#     while True:
#         print('inside while')
#         events = service.events().list(calendarId=calender_id,
#                                        pageToken=page_token, singleEvents=True).execute()
#         for event in events['items']:
#             # print(event['id'],event['summary'])
#             # print(event['start'])
#             print('inside for')
#             if date != None:
#                 # print('P',event['start']['dateTime'][:10],'P',str(date)[:10],'P')
#                 if event['start']['dateTime'][:16] == start_datetime:
#                     print(event['start'])
#                     event_id = event['id']
#                     print(event_id)
#                     break
#         if event_id != None:
#             break
#         page_token = events.get('nextPageToken')
#         if not page_token:
#             break

#     # update event from event_id

#     event = service.events().get(calendarId=calender_id, eventId=event_id).execute()
#     event['summary'] = new_summary
#     updated_event = service.events().update(
#         calendarId=calender_id, eventId=event_id, body=event).execute()
#     print(updated_event['updated'])

# to get the event id of individual slot in a day 
def getEventID(date, time_slot, joining_yr, department):

    # input
    # joining_yr='2021'
    # department = 'cse'
    date = str(date)[:10]

    print(time_slot)
    # change time from '09:20-10:10' format to '<date>T09:20:00'
    start_datetime = date+'T'+time_slot[:5]
    end_datetime = date+'T'+time_slot[6:]
    print(start_datetime, end_datetime)

    service, calender_id = connectToCalender(joining_yr, department)
    # get event_id
    page_token = None
    event_id = None
    while True:
        print("123")
        print(service)
        events = service.events().list(calendarId=calender_id,
                                       pageToken=page_token, singleEvents=True).execute()
        for event in events['items']:
            # print(event['id'],event['summary'])
            # print(event['start'])
            # print(1)
            print(event['start']['dateTime'][:16])
            # print('P',event['start']['dateTime'][:10],'P',str(date)[:10],'P')
            if event['start']['dateTime'][:16] == start_datetime:
                # print(event['start'])
                event_id = event['id']
                # print(event_id)
                break
        if event_id != None:
            break
        page_token = events.get('nextPageToken')
        if not page_token:
            break
    return event_id

# cancel class
def cancelEvent(date, time_slot, joining_yr, department):
    # input
    # date = datetime.today()
    # joining_yr='2021'
    # department = 'cse'
    # time_slot='10:10-11:00'
    # time_slot = '09:20-10:10'
    date = datetime.strptime(date, '%Y-%m-%d').date()
    service, calender_id = connectToCalender(joining_yr, department)
    event_id = getEventID(date, time_slot, joining_yr, department)
    print(event_id)
    service.events().delete(calendarId=calender_id, eventId=event_id).execute()

# add new class or change existing class 
def addOrChangeEvent(date, time_slot, new_summary, joining_yr, department):
    # input
    # date = datetime.today()
    # joining_yr='2021'
    # department = 'cse'
    # # time_slot='09:20-10:10'
    # time_slot = '10:10-11:00'
    # new_summary = 'Trail4: ADD/CHANGE EVENT AT WORK'
#     getEventsOnCond(date)

    date = datetime.strptime(date, '%Y-%m-%d').date()
    times = []
    times.append(time_slot[:5])
    times.append(time_slot[6:])

    service, calender_id = connectToCalender(joining_yr, department)
    event_id = getEventID(date, time_slot, joining_yr, department)
    # print(type(date))
    if event_id:
        # update event from event_id
        event = service.events().get(calendarId=calender_id, eventId=event_id).execute()
        event['summary'] = new_summary
        updated_event = service.events().update(
            calendarId=calender_id, eventId=event_id, body=event).execute()
        print(updated_event['updated'])
    else:
        # create event
        print("no event_id")
        print(type(date))
        try:
            print('inside try')
            timezone_offset = timedelta(hours=-7)
            print('before event')
            # print(str(datetime.combine(date, datetime.strptime(
            # times[0], '%H:%M:%S').time()).isoformat()))
            # print(date,times[0],times[1])
            # print(datetime.strptime(times[0], '%H:%M'))
            # print(datetime.strptime(times[0], '%H:%M').time())
            # print(str(datetime.combine(date, datetime.strptime(times[0], '%H:%M').time())))
            # print(datetime.combine(date, datetime.strptime(times[0], '%H:%M').time()).isoformat())
            start_datetime = str(datetime.combine(
                date, datetime.strptime(times[0], '%H:%M').time()).isoformat())
            end_datetime = str(datetime.combine(
                date, datetime.strptime(times[1], '%H:%M').time()).isoformat())
            print(start_datetime)
            print(end_datetime)

            event = {
                'summary': new_summary,
                'start': {'dateTime': start_datetime, 'timeZone': 'Asia/Kolkata', },
                'end': {'dateTime': end_datetime, 'timeZone': 'Asia/Kolkata', },
            }
            print("works till here")
            print(event)
            print(service)
            event = service.events().insert(calendarId=calender_id, body=event).execute()
            print('Event created: %s' % (event.get('htmlLink')))


            # getEventsOnCond(date)
            
        except HttpError as error:
            print(f"An error occurred: {error}")

# reschedule class from _ to _
def rescheduleEvent(date, time_slot, new_date, new_time_slot, joining_yr, department):
    # input
    # date = datetime.today()
    # joining_yr='2021'
    # department = 'cse'
    # # time_slot='09:20-10:10'
    # time_slot = '10:10-11:00'
    # new_date = datetime.today()+timedelta(days=1)
    # new_time_slot = '09:20-10:10'
    # print(new_date)
    print(1234)
    date = datetime.strptime(date, '%Y-%m-%d').date()
    new_date = datetime.strptime(new_date, '%Y-%m-%d').date()

    service, calender_id = connectToCalender(joining_yr, department)
    event_id = getEventID(date, time_slot, joining_yr, department)
    print(1, event_id)
    event = service.events().get(calendarId=calender_id, eventId=event_id).execute()

    new_slot_event_id = getEventID(new_date, new_time_slot, joining_yr, department)
    print(2, new_slot_event_id)

    if new_slot_event_id != None:
        #  the new slot is not empty
        # update new slot
        new_event = service.events().get(calendarId=calender_id,
                                         eventId=new_slot_event_id).execute()
        new_event['summary'] = event['summary']
        print(new_event['summary'], event['summary'])
        new_event = service.events().update(calendarId=calender_id,
                                            eventId=new_slot_event_id, body=new_event).execute()
        print(new_event['updated'])
    else:
        # the new_slot is empty
        # create event
        print("no event_id")
        try:
            timezone_offset = timedelta(hours=-7)
            event = {
                'summary': event['summary'],
                'start': {'dateTime': str(datetime.combine(new_date, datetime.strptime(new_time_slot[:5], '%H:%M').time()).isoformat()), 'timeZone': 'Asia/Kolkata', },
                'end': {'dateTime': str(datetime.combine(new_date, datetime.strptime(new_time_slot[6:], '%H:%M').time()).isoformat()), 'timeZone': 'Asia/Kolkata', },
            }
            print("works till here")
            print(event)
            print(service)
            event = service.events().insert(calendarId=calender_id, body=event).execute()
            print('Event created: %s' % (event.get('htmlLink')))
        except HttpError as error:
            print(f"An error occurred: {error}")

    # delete old slot
    service.events().delete(calendarId=calender_id, eventId=event_id).execute()

#get day schedule for faculty from given course list
def getDaySchedule():
    #input
    courses=['cs102','cs103']
    joining_yr,department='2021','cse'

#     date=datetime.today()
#     date=date.strftime('%d-%m-%Y')
    date='15-04-2024'
    print(date)
    print(type(date))
    yrs=['2021','2022','2023','2024']
    departments=['cse','ece']
    course_slots={}
    for course_code in courses:
            slots=[]
            for joining_yr in yrs:
                        for department in departments:
                                    print(course_code,joining_yr,department)
                                    x=getEventsOnCond(date,course_code,joining_yr,department)
                                    if x!=None:
                                         print('not none')
                                         slots.extend(x)
                                    else:
                                         print('none here')
            course_slots[course_code]=slots
    print(course_slots)

    

def changeRecurrenceTotal():
    # function not need anymore
    # Function not complete yet:
    # for furthur ref: https://developers.google.com/calendar/api/quickstart/python

    # input
    day = 'monday'
    joining_yr='2021'
    department = 'CSE'
    slot_no = 2  # 0-indexed
    slot_to_time = [['09:20', '10:10'], ['10:10', '11:00'], ['11:20', '12:10'], [
        '12:10', '13:00'], ['14:00', '14:50'], ['14:50', '15:40'], ['16:00', '16:50']]
    today = start_day = datetime.now().date()
    while start_day.strftime('%A').lower() != day:
        start_day += timedelta(days=1)
    end_date = today + timedelta(days=130)

    # 2parts - event.update() to change UNTILL Tag & event.insert() to insert the new recurrence from start_date
# //////////

# calenderMainTableAdd()


# @api_view(['POST'])
# def add_timetable(request):
#     serializer = TimeTableSerializer(data=request.data)
#     if serializer.is_valid():
#         semester = serializer.validated_data.get('semester')
#         joining_yr = serializer.validated_data.get('joining_yr')
#         department = serializer.validated_data.get('department')
#         day = serializer.validated_data.get('day')

#         # Check if the combination of semester, department, and day already exists
#         if TimeTable.objects.filter(semester=semester, department=department, day=day).exists():
#             return Response({'error': 'Timetable already exists for this semester, department, and day.'}, status=status.HTTP_400_BAD_REQUEST)

#         serializer.save()
#         # day = serializer.data.get('slot_4')
#         # print(len(day))
#         # validated_data = serializer.validated_data
#         # ###
#         calenderMainTableAdd(serializer.data.get('joining_yr'), serializer.data.get('department'), serializer.data.get('day'), serializer.data.get('slot_1'), serializer.data.get('slot_2'), serializer.data.get('slot_3'),
#                              serializer.data.get('slot_4'), serializer.data.get('slot_5'), serializer.data.get('slot_6'), serializer.data.get('slot_7'))

#         return Response(serializer.data, status=201)
#     else:
#         print(serializer.errors)
#         return Response(serializer.errors, status=400)


# @api_view(['PUT'])
# def update_timetable(request):
#     update_data = request.data
#     semester = update_data.get('updateSemester')
#     department = update_data.get('updateDepartment')
#     day = update_data.get('updateDay')
#     slot = update_data.get('updateSlot')
#     course_code = update_data.get('courseCode')

#     try:
#         timetable_entry = TimeTable.objects.get(
#             semester=semester, department=department, day=day)
#     except TimeTable.DoesNotExist:
#         return Response({'error': 'Timetable entry not found for the specified day'}, status=404)

#     slot_field_name = f"slot_{slot}"
#     setattr(timetable_entry, slot_field_name, course_code)
#     timetable_entry.save()

#     serializer = TimeTableSerializer(timetable_entry)
#     return Response(serializer.data, status=200)


@api_view(['POST'])
def reschedule_class(request):
    # serializer = TimeTableSerializer(data=request.data)
    # semester = serializer.data.get('semester')
    # department = serializer.data.get('department')
    # print(semester)
    # print(department)
    try:
        from_date = request.data['from_date']
        from_time_slot = request.data['from_time_slot']
        to_date = request.data['to_date']
        to_time_slot = request.data['to_time_slot']
        joining_yr = request.data['joining_yr']
        department = request.data['department']
        # semester = request.data.get('semester')
#         joining_yr = '2021'
#         department = 'cse'
#           semester=0
        print('Reschedule from', from_date,
              from_time_slot, 'to', to_date, to_time_slot)

        rescheduleEvent(from_date, from_time_slot, to_date,
                        to_time_slot, joining_yr, department)

        return Response({'message': 'Class rescheduled successfully'}, status=201)
    except Exception as e:
        return Response({'error': str(e)}, status=400)


@api_view(['POST'])
def add_or_change_class(request):
    # serializer = TimeTableSerializer(data=request.data)
    # semester = serializer.data.get('semester')
    # department = serializer.data.get('department')
    # print(semester)
    # print(department)



    date = request.data.get('addorchange_date')
    time_slot = request.data.get('addorchange_time_slot')
    course_code = request.data.get('addorchange_course_code')
    joining_yr = request.data.get('joining_yr')
    department = request.data.get('department')
#     semester = 0
#     department = 'cse'
    try:
        print('added_or_changed', date, time_slot, course_code)
        addOrChangeEvent(date, time_slot, course_code, joining_yr, department)
        return Response({'message': 'Class added or changed successfully'}, status=201)
    except Exception as e:
        return Response({'error': str(e)}, status=400)


@api_view(['POST'])
def cancel_class(request):
    # serializer = TimeTableSerializer(data=request.data)
    # semester = serializer.data.get('semester')
    # department = serializer.data.get('department')
    # print(semester)
    # print(department)
    date = request.data.get('cancel_date')
    time_slot = request.data.get('cancel_time_slot')
    joining_yr = request.data.get('joining_yr')
    department = request.data.get('department')  
#     semester = 0
#     department = 'cse'
    try:
        print('cancelled', date, time_slot)
        cancelEvent(date, time_slot, joining_yr, department)
        return Response({'message': 'Class cancelled successfully'}, status=201)
    except Exception as e:
        return Response({'error': str(e)}, status=400)

@api_view(['POST'])
def insertAttendance(request):
    print("insert insert attendance")
    print(request.data)
    date = request.data["date"]
    course_id = request.data["course_id"]
    absentees_list = request.data["absentees_list"] # the date and course_id are same and absentees list contains all the roll numbers of students that are absent 
    time_slot = request.data["time_slot"]
    department = request.data["department"]
    print("department and course id is ",department,course_id)
    if request.data["count"] == 0:
        total_classes = CurrentCourses.objects.filter(department=department,course_code=course_id)[0].total_classes
        CurrentCourses.objects.filter(department=department,course_code=course_id).update(total_classes=total_classes+1)
        
    existing_entry = Absentees.objects.filter(course_code=course_id,date=date,time_slot=time_slot)
    if existing_entry and  len(existing_entry)!=len(request.data["absentees_list"]):

        for entry in existing_entry:
            entry.delete()
    elif existing_entry and  len(existing_entry)==len(request.data["absentees_list"]):
        return Response({})
    for roll_no in absentees_list:
        new_entry = Absentees(course_code=course_id,date=date,roll_no=roll_no,time_slot=time_slot)
        new_entry.save()
    return Response({})
    


@api_view(['GET'])
def  getCoursesForFaculty(request):
    # print('inside getcoursed')
    # print(request.GET.get('faculty_name'))
    faculty_name = request.GET.get("faculty_name")

    corresponding_courses = CurrentCourses.objects.filter(faculty_name=faculty_name)
    course_list=[]
    for obj in corresponding_courses:
        course_code = obj.course_code
        course_name = CourseList.objects.filter(course_code=course_code)[0].course_name
        course_list.append([course_code,course_name,obj.department])
    
    print("&&&",course_list)

    return Response({"course_list":course_list})


@api_view(['GET'])
def getStudentsFromCourseCode(request):
    
    course_code = request.GET.get('course_code')
    department=request.GET.get('department')
    print(course_code,department)
    # semester=CurrentCourses.objects.filter(course_code=course_code,department=department)
    semester=CurrentCourses.objects.filter(course_code=course_code,department=department)[0].semester


    student_objects=StudentInfo.objects.filter(semester=semester)
    student_list=[]
    for student_obj in student_objects :
        # student_list.append([student_obj.roll_no,student_obj.name,0,0])
        student_list.append({'name':student_obj.name,'roll_no':student_obj.roll_no,'present':0, 'absent':0})
    
    return Response({'student_list':student_list})

@api_view(['GET'])
def getStudentsFromCourseCodeForResult(request):
    course_code = request.GET.get('course_code')
    department=request.GET.get('department')
    semester=CurrentCourses.objects.filter(course_code=course_code,department=department)[0].semester
    student_objects=StudentInfo.objects.filter(semester=semester)
    student_list=[]
    for student_obj in student_objects :
        student_list.append({'name':student_obj.name,'roll_no':student_obj.roll_no,'ct_1':0, 'ct_2':0,
                             'assignments':0,'end_sem':0,'grade':'NA'})
    
    return Response({'student_list':student_list})


@api_view(['GET'])
def getCoursesForStudents(request) :    
    semester=request.GET.get('semester')
    department=request.GET.get('department')
    print(semester,department)
    courses_objects=CourseList.objects.filter(semester=semester,department=department)
    courses_list=[]
    for course_obj in courses_objects :
        courses_list.append([course_obj.course_code,course_obj.course_name,course_obj.department])
    
    return   Response({'course_list': courses_list})

 
@api_view(['GET'])
def getAttendanceDetailsForStudent(request):
    roll_no=request.GET.get("roll_no")
    course_code=request.GET.get("course_code")
    department=request.GET.get("department")

    print('department',department)

    dates_of_absent_objects=Absentees.objects.filter(roll_no=roll_no,course_code=course_code)
    dates_of_absent=[]
    for  date_object in dates_of_absent_objects:
         dates_of_absent.append([date_object.date,date_object.time_slot])
    print('dates of abseonts',dates_of_absent)
    print('coirse',course_code)
    no_of_total_classes=CurrentCourses.objects.filter(course_code=course_code,department=department)[0].total_classes

    return Response({'dates_of_absent':dates_of_absent,'total_classes':no_of_total_classes})



@api_view(['POST'])
def loginUser(request):
    username = request.data['username']
    password = request.data['password']
    if username and password:
        user = authenticate(username = username, password = password)
        authenticated=False
        if user is not None:
            login(request,user)
            authenticated=True
        return Response({'authenticated':authenticated})
        


def logoutUser(request):
    logout(request)
    return Response({'authenticated':False})

@api_view(['GET'])
def getUserDetails(request):
    email = request.GET.get('username')
    print("email is",email)
    type_of_user = Login.objects.filter(email = request.GET.get('username'))[0].type_of_user
    if type_of_user=='student' or type_of_user=='student_cr':
        student = StudentInfo.objects.filter(email=email)[0]
        roll_no = student.roll_no
        name = student.name
        department = student.department.lower()
        semester = student.semester
        joining_year = student.joining_year


        return Response({'type_of_user':type_of_user,'roll_no':roll_no,'student_name':name,'department':department,'semester':semester,'joining_year':joining_year, 'email': email, 'username': email})
    elif type_of_user=='faculty':
        teacher = FacultyInfo.objects.filter(email=email)[0]
        name = teacher.name
        return Response({'type_of_user':type_of_user,'faculty_name':name,'faculty_id':teacher.faculty_id, 'email': email, 'username': email})
    elif type_of_user == 'admin':
        staff = AdministrationInfo.objects.filter(email=email)[0]
        name = staff.name
        position = staff.position
        staff_id = staff.staff_id
        return Response({'type_of_user': type_of_user, 'staff_name': name, 'position': position, 'staff_id': staff_id, 'email': email, 'username': email})

# snigdha
@api_view(['GET'])
def getUserAllDetails(request):
    email = request.GET.get('username')
    print("email is", email)
    type_of_user = Login.objects.filter(
        email=request.GET.get('username'))[0].type_of_user
    if type_of_user == 'student' or type_of_user == 'student_cr':
        student = StudentInfo.objects.filter(email=email)[0]
        name = student.name
        roll_no = student.roll_no
        joining_year = student.joining_year
        semester = student.semester
        department = student.department
        gender = student.gender
        blood_group = student.blood_group
        contact_number = student.contact_number
        # email=
        address = student.address
        return Response({'type_of_user': type_of_user, 'student_name': name, 'roll_no': roll_no, 'joining_year': joining_year, 'department': department, 'semester': semester, 'gender': gender, 'blood_group': blood_group, 'contact_number': contact_number, 'email': email, 'address': address})
    elif type_of_user == 'faculty':
        print("faculty email sent: ", email)
        teacher = FacultyInfo.objects.filter(email=email)[0]
        name = teacher.name
        return Response({'type_of_user': type_of_user, 'faculty_id': teacher.faculty_id, 'faculty_name': teacher.name, 'position': teacher.position, 'designation': teacher.designation, 'email': teacher.email, 'description': teacher.description})
    elif type_of_user == 'admin':
        print("admin email sent: ", email)
        staff = AdministrationInfo.objects.filter(email=email)[0]
        name = staff.name
        position = staff.position
        staff_id = staff.staff_id
        return Response({'type_of_user': type_of_user, 'admin_name': name, 'position': position, 'admin_id': staff_id, 'email': email, 'username': email})

@api_view(['POST'])
def addResult(request) :
    records=request.data
    course_code=records[0]['course_code']
    Result.objects.filter(course_code=course_code).delete()

    for record in records :
        print(record)
        course_code=record['course_code']
        faculty=record['faculty']
        ct_1=record['ct_1']
        ct_2=record['ct_2']
        assignments=record['assignments']
        end_sem=record['end_sem']
        grade=record['grade']
        roll_no=record['roll_no']
        obj=Result(course_code=course_code,faculty=faculty,ct_1=ct_1,ct_2=ct_2,assignments=assignments,end_sem=end_sem,grade=grade,roll_no=roll_no)
        obj.save()
    return Response({})


@api_view(['GET'])

def getResultForStudentForCourse(request) :
    course_code=request.GET.get('course_code')
    roll_no=request.GET.get('roll_no')

    result_object=Result.objects.filter(roll_no=roll_no,course_code=course_code)[0]

    return Response({'ct_1' : result_object.ct_1,'ct_2' : result_object.ct_2,'assignments':result_object.assignments,'end_sem' : result_object.end_sem,'grade' : result_object.grade})

@api_view(['GET'])

def getTodosForUser(request) :
    roll_no=request.GET.get('roll_no') 
    todos_objects=Todolist.objects.filter(roll_no=roll_no)
    data = [{'roll_no': item.roll_no, 'task': item.task, 'id': item.id,'is_completed':item.is_completed} for item in todos_objects]

    return Response({'todos_details' : data})



@api_view(['GET'])
def getCalendarId(request):
    joining_year = request.GET.get('joining_year')
    department=request.GET.get('department')
    # print(department)
    yrs=['2021','2022','2023','2024']
    calenders=['20d93d2fe1b0ecd1544f1a2b2b108da8e96af9ff12241d7492c3d65b24238790@group.calendar.google.com','42d1535640fbdeb2c505ba9b52315343dc907a3b2f91d4b9645b9b3805804828@group.calendar.google.com','aa4783b76409e5b9f2557220593a81e47854cb1f8692abe0a10754a7fde96202@group.calendar.google.com','a925c86f766b09ffa88d867653cafe9d55aaece2843c7f23657823807b2de584@group.calendar.google.com','41071f57b3a292eaa22f30e3f138487c6629af8d4504e280ea66ae2e4b99e65b@group.calendar.google.com','b4f926456995f1ce8e90e4038597f600fec71ca73c0745a0e56098dfacddc4c4@group.calendar.google.com','343a067515a7b486410df769c83cc58ec72b3b27bfeb68399c197b9ff448c09b@group.calendar.google.com','cefe6f3824e000eed77be01be2f930e92038c80b0a0e62bd56063e976aa85721@group.calendar.google.com']
    dept_mapping={'cse': 0,'ece':4}
    idx=dept_mapping[department.lower()]+yrs.index(joining_year)
    calendar_id=calenders[idx]
    print('calender 2021 cse: ',calendar_id)
    return Response({'calendar_id': calendar_id})


@api_view(['GET'])
def getTimetableForStudent(request):
    semester = request.GET.get('semester')
    department = request.GET.get('department')
    department=department.lower()
    print(semester + " " + department)
    timetable_objects = TimeTable.objects.filter(
        semester=semester, department=department)

    timetable_data = []
    for timetable_object in timetable_objects:
        timetable_data.append({
            'day': timetable_object.day,
            'slot_1': timetable_object.slot_1,
            'slot_2': timetable_object.slot_2,
            'slot_3': timetable_object.slot_3,
            'slot_4': timetable_object.slot_4,
            'slot_5': timetable_object.slot_5,
            'slot_6': timetable_object.slot_6,
            'slot_7': timetable_object.slot_7
        })
    print('timetable',timetable_data)

    timetable_data= sorted(timetable_data, key=lambda x: ["monday", "tuesday", "wednesday", "thursday", "friday"].index(x['day'].lower()))
    return Response({"timetable_data":timetable_data})

    # return Response({'day': timetable_object.day, 'slot_1': timetable_object.slot_1, 'slot_2': timetable_object.slot_2, 'slot_3': timetable_object.slot_3, 'slot_4': timetable_object.slot_4, 'slot_5': timetable_object.slot_5, 'slot_6': timetable_object.slot_6, 'slot_7': timetable_object.slot_7})



@api_view(['GET'])
def search(request):
    search_query = request.GET.get('searchText')
    if search_query and len(search_query) >= 5:
        print(search_query)
        student_results = StudentInfo.objects.filter(
            name__icontains=search_query)
        faculty_results = FacultyInfo.objects.filter(
            name__icontains=search_query)
        admin_results = AdministrationInfo.objects.filter(
            name__icontains=search_query)
        # Combine search results into a single list
        # search_results = list(student_results.values()) + list(faculty_results.values())
        search_list = []
        for search_obj in student_results:
            search_list.append({'name': search_obj.name, 'roll_no': search_obj.roll_no, 'department': search_obj.department,
                               'semester': search_obj.semester, 'joining_year': search_obj.joining_year, 'email': search_obj.email})
        for search_obj in faculty_results:
            search_list.append({'name': search_obj.name, 'faculty_id': search_obj.faculty_id, 'position': search_obj.position,
                               'description': search_obj.description, 'designation': search_obj.designation, 'email': search_obj.email})
        for search_obj in admin_results:
            search_list.append({'name': search_obj.name, 'position': search_obj.position,
                               'staff_id': search_obj.staff_id, 'email': search_obj.email})
        return Response({'search_list': search_list})
    else:
        return Response({'error': 'Please enter a search query with a minimum of 5 characters'}, status=400)

# i wrote this function to validate batch in fee defaulters
def validate_batch_format(batch):
    # Check the length and format of the batch
    return bool(re.match(r'^\d{4}-\d{4}$', batch)) 

@api_view(['GET'])
def getFeeDefaulters(request):
    department = request.GET.get('department')
    batch = request.GET.get('batch')
    # Validate the batch format
    if not validate_batch_format(batch):
        return Response({'error': 'Invalid batch format. Batch must be in the format XXXX-XXXX, where X is a digit and has exactly one hyphen.'}, status=400)
    
    student_list = []
    students = FeeDefaulters.objects.filter(department=department, batch=batch)
    print(students)
    for search_obj in students:
        # student_list.append({'roll_no':search_obj.roll_no})
        defaulter = StudentInfo.objects.filter(roll_no=search_obj.roll_no)[0]
        student_list.append({'roll_no': search_obj.roll_no, 'name': defaulter.name,
                            'email': defaulter.email, 'contact_number': defaulter.contact_number})
    return Response({'student_list': student_list})


# @api_view(['GET'])
# def getMessages(request):
#     messages = Message.objects.filter(
#         recipient='admin', message_type='Request for fee receipt')
#     student_list = []
#     for msg in messages:
#         student = StudentInfo.objects.get(email=msg.sender)
#         student_list.append({'sender': msg.sender, 'message_type': msg.message_type,
#                             'status': msg.status, 'roll_no': student.roll_no, 'name': student.name})
#     return Response({'student_list': student_list})


# @api_view(['POST'])
# def acceptMessage(request):
#     sender = request.data.get('messageSender')
#     message = Message.objects.get(
#         sender=sender, message_type='Request for fee receipt')
#     message.status = True
#     message.save()
#     print(message)
#     return Response({'status': 'Message accepted successfully'}, status=200)


# @api_view(['GET'])
# def getCertificates(request):
#     certificates = Message.objects.filter(
#         recipient='admin', message_type='Request for Bonafide Certificate')
#     student_list = []
#     for msg in certificates:
#         student = StudentInfo.objects.get(email=msg.sender)
#         student_list.append({'sender': msg.sender, 'message_type': msg.message_type,
#                             'status': msg.status, 'roll_no': student.roll_no, 'name': student.name})
#     return Response({'student_list': student_list})


# @api_view(['POST'])
# def acceptCertificate(request):
#     sender = request.data.get('messageSender')
#     message = Message.objects.get(
#         sender=sender, message_type='Request for Bonafide Certificate')
#     message.status = True
#     message.save()
#     print(message)
#     return Response({'status': 'Message accepted successfully'}, status=200)


# @api_view(['POST'])
# def sendMessage(request):
#     recipient = request.data.get('recipient')
#     message_type = request.data.get('message')
#     sender = request.data.get('sender')
#     obj = Message(sender=sender, message_type=message_type,
#                   recipient=recipient)
#     obj.save()
#     return Response({'status': 'Requested'})


# @api_view(['GET'])
# def checkMessageStatus(request):
#     sender = request.GET.get('sender')
#     if Message.objects.filter(sender=sender, message_type='Request for fee receipt').exists():
#         message = Message.objects.get(
#             sender=sender, message_type='Request for fee receipt')
#         return Response({'status': message.status}, status=200)
#     else:
#         return Response({'status': 'Request'}, status=200)


# @api_view(['POST'])
# def sendCertificate(request):
#     recipient = request.data.get('recipient')
#     message_type = request.data.get('message')
#     sender = request.data.get('sender')
#     obj = Message(sender=sender, message_type=message_type,
#                   recipient=recipient)
#     obj.save()
#     return Response({'status': 'Requested'})


# @api_view(['GET'])
# def checkCertificateStatus(request):
#     sender = request.GET.get('sender')
#     if Message.objects.filter(sender=sender, message_type='Request for Bonafide Certificate').exists():
#         message = Message.objects.get(
#             sender=sender, message_type='Request for Bonafide Certificate')
#         return Response({'status': message.status}, status=200)
#     else:
#         return Response({'status': 'Request'}, status=200)

@api_view(['GET'])
def getMessages(request):
    messages = Message.objects.filter(recipient='admin', message_type='Request for fee receipt')
    student_list = []
    for msg in messages:
        student = StudentInfo.objects.get(email=msg.sender)
        student_list.append({
            'sender': msg.sender,
            'message_type': msg.message_type,
            'status': msg.status,
            'roll_no': student.roll_no,
            'name': student.name
        })
    return Response({'student_list': student_list})

@api_view(['POST'])
def acceptMessage(request):
    sender = request.data.get('sender')
    message = Message.objects.get(sender=sender, message_type='Request for fee receipt')
    message.status = True
    # i commented this because i added pdf size constraint
    # if 'file' in request.FILES:
    #     message.file = request.FILES['file']
    #     message.save()
    #     return Response({'status': 'Message accepted and file uploaded successfully'}, status=200)
    # else:
    #     message.save()
    #     return Response({'status': 'Message accepted successfully'}, status=200)
    if 'file' in request.FILES:
        message.file = request.FILES['file']
        # Call full_clean to trigger the validation
        try:
            message.full_clean()
            message.save()
            return Response({'status': 'Message accepted and file uploaded successfully'}, status=200)
        except ValidationError as e:
            return Response({'status': 'File size too large', 'errors': str(e)}, status=400)
    else:
        message.save()
        return Response({'status': 'Message accepted successfully'}, status=200)

@api_view(['POST'])
def sendMessage(request):
    recipient = request.data.get('recipient')
    message_type = request.data.get('message')
    sender = request.data.get('sender')
    print("sender is : ",sender)
    obj = Message(sender=sender, message_type=message_type, recipient=recipient)
    obj.save()
    return Response({'status': 'Requested'})


@api_view(['GET'])
def checkMessageStatus(request):
    sender = request.GET.get('sender')
    if Message.objects.filter(sender=sender, message_type='Request for fee receipt').exists():
        message = Message.objects.get(sender=sender, message_type='Request for fee receipt')
        file_url = request.build_absolute_uri(message.file.url)  # Get the absolute URL of the file
        return Response({'status': message.status, 'file_url': file_url}, status=200)
    else:
        return Response({'status': 'Request'}, status=200)


@api_view(['GET'])
def getCertificates(request):
    messages = Message.objects.filter(recipient='admin', message_type='Request for Bonafide Certificate')
    student_list = []
    for msg in messages:
        student = StudentInfo.objects.get(email=msg.sender)
        student_list.append({
            'sender': msg.sender,
            'message_type': msg.message_type,
            'status': msg.status,
            'roll_no': student.roll_no,
            'name': student.name
        })
    return Response({'student_list': student_list})

@api_view(['POST'])
def acceptCertificate(request):
    sender = request.data.get('sender')
    message = Message.objects.get(sender=sender, message_type='Request for Bonafide Certificate')
    message.status = True
    # i commented this because i added pdf size constraint
    # if 'file' in request.FILES:
    #     message.file = request.FILES['file']
    #     message.save()
    #     return Response({'status': 'Message accepted and file uploaded successfully'}, status=200)
    # else:
    #     message.save()
    #     return Response({'status': 'Message accepted successfully'}, status=200)
    if 'file' in request.FILES:
        message.file = request.FILES['file']
        # Call full_clean to trigger the validation
        try:
            message.full_clean()
            message.save()
            return Response({'status': 'Message accepted and file uploaded successfully'}, status=200)
        except ValidationError as e:
            return Response({'status': 'File size too large', 'errors': str(e)}, status=400)
    else:
        message.save()
        return Response({'status': 'Message accepted successfully'}, status=200)


@api_view(['POST'])
def sendCertificate(request):
    recipient = request.data.get('recipient')
    message_type = request.data.get('message')
    sender = request.data.get('sender')
    print("sender is : ",sender)
    obj = Message(sender=sender, message_type=message_type, recipient=recipient)
    obj.save()
    return Response({'status': 'Requested'})


@api_view(['GET'])
def checkCertificateStatus(request):
    sender = request.GET.get('sender')
    if Message.objects.filter(sender=sender, message_type='Request for Bonafide Certificate').exists():
        message = Message.objects.get(sender=sender, message_type='Request for Bonafide Certificate')
        file_url = request.build_absolute_uri(message.file.url)  # Get the absolute URL of the file
        return Response({'status': message.status, 'file_url': file_url}, status=200)
    else:
        return Response({'status': 'Request'}, status=200)

@api_view(['GET'])
def getEachClassStudentsList(request):
    # i commented this because i applied some mappings to department field
    # department = request.GET.get('department')
    # joiningYear = request.GET.get('joiningYear')

    department = request.GET.get('department', '').lower()
    joiningYear = request.GET.get('joiningYear')
    department_mapping = {
        'computer science and engineering': 'cse',
        'electronics and communication engineering': 'ece'
    }
    if department in department_mapping:
        department = department_mapping[department]

    student_list = []
    students = StudentInfo.objects.filter(
        department=department, joining_year=joiningYear)
    print(students)
    for search_obj in students:
        # student_list.append({'roll_no':search_obj.roll_no})
        # defaulter = StudentInfo.objects.filter(roll_no=search_obj.roll_no)[0]
        student_list.append({'roll_no': search_obj.roll_no, 'name': search_obj.name,
                            'email': search_obj.email, 'contact_number': search_obj.contact_number})
    return Response({'student_list': student_list})


# @api_view(['POST'])
# def addNewStudent(request):
#     roll_no = request.data.get('roll_no')
#     name = request.data.get('name')
#     department = request.data.get('department')
#     joining_year = request.data.get('joining_year')
#     blood_group = request.data.get('blood_group')
#     semester = request.data.get('semester')
#     contact_number = request.data.get('contact_number')
#     address = request.data.get('address')
#     gender = request.data.get('gender')
#     email = request.data.get('email')
#     obj = StudentInfo(roll_no=roll_no, name=name, department=department, joining_year=joining_year, blood_group=blood_group,
#                       semester=semester, contact_number=contact_number, address=address, gender=gender, email=email)
#     obj.save()
#     return Response({'status': 'Saved Successfully'}, status=200)
from django.contrib.auth.models import User

@api_view(['POST'])
def addNewStudent(request):
    roll_no = request.data.get('roll_no')
    name = request.data.get('name')
    department = request.data.get('department')
    joining_year = request.data.get('joining_year')
    blood_group = request.data.get('blood_group')
    semester = request.data.get('semester')
    contact_number = request.data.get('contact_number')
    address = request.data.get('address')
    gender = request.data.get('gender')
    email = request.data.get('email')

    department=department.lower()
    
    obj = StudentInfo(roll_no=roll_no, name=name, department=department, joining_year=joining_year, blood_group=blood_group, semester=semester, contact_number=contact_number, address=address, gender=gender, email=email)
    obj.save()
    
    login_obj = Login(email=email, type_of_user='student')
    login_obj.save()
    
    username = email
    password = email[:6]
    
    if not User.objects.filter(username=username).exists():
        user = User.objects.create_user(username=username, password=password)
        user.save()
    
    return Response({'status': 'Saved Successfully'}, status=200)


from django.utils import timezone
from datetime import date, timedelta



@api_view(['POST'])
def updateSemester(request):
    print("hello i came inside")
    students = StudentInfo.objects.all()
    current_date = date.today()
    current_year = current_date.year
    current_month = current_date.month
    for student in students:        
        joining_year = student.joining_year

        years_since_joining = (int(current_year) - int(joining_year)) + (current_month - 6) / 12
        
        if years_since_joining >= 4:
            semester = 0
        else:
            semester = int(years_since_joining * 2) + 1

        student.semester = semester
        student.save()

    return Response(f"Semester updated successfully. Current semester: {semester}")


@api_view(['GET'])
def facultyTimetable(request):
    faculty_name = request.GET.get('faculty_name')  #as input
    # faculty_name = 'Anoop Jacob Thomas'  # input
    print(faculty_name)
    days_courses = {}
    corresponding_courses = CurrentCourses.objects.filter(
        faculty_name=faculty_name)
    course_codes = []
    for obj in corresponding_courses:
        course_codes.append(
            [obj.semester, obj.department.lower(), obj.course_code])

    print(">>", course_codes)
    abc = []
    # return Response({"course_list": course_list})
    for course in course_codes:
        student_semester = course[0]
        student_department = course[1].lower()
        course_code = course[2]
        # print(course_code, department)

        # Get student timetables for this course code and department
        student_timetables = TimeTable.objects.filter(slot_1=course_code) | \
            TimeTable.objects.filter(slot_2=course_code) | \
            TimeTable.objects.filter(slot_3=course_code) | \
            TimeTable.objects.filter(slot_4=course_code) | \
            TimeTable.objects.filter(slot_5=course_code) | \
            TimeTable.objects.filter(slot_6=course_code) | \
            TimeTable.objects.filter(slot_7=course_code)
        # print("->")
        # print(student_timetables)
        for timetable in student_timetables:
            for i in range(1, 8):  # Loop through slots
                slot_name = f"slot_{i}"
                if getattr(timetable, slot_name) == course_code:
                    course_code1 = course_code
                else:
                    course_code1 = ''
                if getattr(timetable, slot_name) == course_code:
                    print('1', timetable.day, slot_name, course_code)
                    l = [timetable.day, slot_name, course_code]
                    print(l)
                    abc.append(l)
                #     print(type(timetable.day))

    print(abc)

    for item in abc:
        day = item[0]
        slot_name = item[1]
        course_code1 = item[2]
        print(day)
        if day in list(days_courses.keys()):
            print('key there', item[0])
            days_courses[day][slot_name] = course_code1
        else:
            print('key not there', day)
            # days_courses[timetable.day] = [[slot_name, course_code1],]
            sl = {
                'slot_1': '',
                'slot_2': '',
                'slot_3': '',
                'slot_4': '',
                'slot_5': '',
                'slot_6': '',
                'slot_7': '',
            }
            days_courses[day] = sl
            print(days_courses[day])
            print(slot_name)
            days_courses[day][slot_name] = course_code1
            # print(days_courses[timetable.day])

        print(days_courses)
        print(list(days_courses.keys()))

        # Create or update faculty timetables
        cnt = 0
        for day in list(days_courses.keys()):
            # print(days_courses[day]['slot_1'])
            FacultyTimeTable.objects.update_or_create(
                name=faculty_name,
                day=day,
                defaults={
                    'slot_1': days_courses[day]['slot_1'],
                    'slot_2': days_courses[day]['slot_2'],
                    'slot_3': days_courses[day]['slot_3'],
                    'slot_4': days_courses[day]['slot_4'],
                    'slot_5': days_courses[day]['slot_5'],
                    'slot_6': days_courses[day]['slot_6'],
                    'slot_7': days_courses[day]['slot_7']}
            )
            cnt += 1
        print(cnt)

    faculty_timetable_objects = FacultyTimeTable.objects.filter(
        name=faculty_name)

    print(faculty_timetable_objects)

    faculty_timetable_data = []

    for i in faculty_timetable_objects:
        faculty_timetable_data.append({
            'day': i.day,
            'slot_1': i.slot_1,
            'slot_2': i.slot_2,
            'slot_3': i.slot_3,
            'slot_4': i.slot_4,
            'slot_5': i.slot_5,
            'slot_6': i.slot_6,
            'slot_7': i.slot_7
        })

    print("faculty_timetable_data", faculty_timetable_data)

    faculty_timetable_data= sorted(faculty_timetable_data, key=lambda x: ["monday", "tuesday", "wednesday", "thursday", "friday"].index(x['day'].lower()))

    return Response({"faculty_timetable_data": faculty_timetable_data})


@api_view(['GET'])
def getFacultySchedule(request):
    faculty_name = request.GET.get('faculty_name')  # as input
    # input faculty_name
    # faculty_name = 'Anoop Jacob Thomas'

    # getDaySchedule()

    print('inside getFacultySchedule')

    date = datetime.today()
    date = date.strftime('%d-%m-%Y')
    print(date)
    # date='22-04-2024'
    yrs = ['2021', '2022', '2023', '2024']
    slot_to_time = [['09:20', '10:10'], ['10:10', '11:00'], ['11:20', '12:10'], [
        '12:10', '13:00'], ['14:00', '14:50'], ['14:50', '15:40'], ['16:00', '16:50']]

    # faculty_name = request.GET.get("faculty_name")
    corresponding_courses = CurrentCourses.objects.filter(
        faculty_name=faculty_name)
    course_list = []
    for obj in corresponding_courses:
        course_list.append((obj.course_code, obj.department))

    slots_today = {}
    for course_code, department in course_list:
        for joining_yr in yrs:
            res = getEventsOnCond(date, course_code, joining_yr, department)
            if res:
                if course_code not in slots_today:
                    slots_today[course_code] = res
                else:
                    slots_today[course_code].extend(res)

    print("slots of faculty", slots_today)

    for day in list(slots_today.keys()):
        for i in range(len(slots_today[day])):
            for j in range(len(slot_to_time)):
                if slot_to_time[j][0] == slots_today[day][i]:
                    slots_today[day][i] = f"slot_{j+1}"

    print("slots of faculty", slots_today)
    print("&&&", course_list)
    # return slots_today
    print("slots_today :", slots_today)

    print("sending to frontend")

    day_slots = {
        'slot_1': '',
        'slot_2': '',
        'slot_3': '',
        'slot_4': '',
        'slot_5': '',
        'slot_6': '',
        'slot_7': '',
    }

    for course in slots_today.keys():
        for slot in slots_today[course]:
            # print(d[course],slot)
            day_slots[slot] = course
    print(day_slots)


    return Response({"slots_today": day_slots})

@api_view(['GET'])
def getTimeSlotForFaculty(request):
    #get day schedule for faculty from given course list

    #input
    course_code = request.GET.get("course_code")
    date=request.GET.get("date") #need to remove this in actual code
    department = request.GET.get("department")
#     date=datetime.today()
#     date=date.strftime('%d-%m-%Y')

    
    print(date)
    print(type(date))
    yrs=['2021','2022','2023','2024']
    # departments=['cse','ece']
    course_slots={}
    slots=[]
    for joining_yr in yrs:
        print(course_code,joining_yr,department)
        x=getEventsOnCond(date,course_code,joining_yr,department)
        if x!=None:
            print('not none')
            slots.extend(x)
        else:
            print('none here')
    course_slots[course_code]=slots
    print(234)
    print(course_slots)
    return Response({"time_slots":course_slots[course_code]})


# @api_view(['POST'])
# def addTimetable(request):
#     serializer = TimeTableSerializer(data=request.data)
#     if serializer.is_valid():
#         semester = serializer.validated_data.get('semester')
#         joining_yr = serializer.validated_data.get('joining_yr')
#         department = serializer.validated_data.get('department')
#         day = serializer.validated_data.get('day')

#         # Check if the combination of semester, department, and day already exists
#         if TimeTable.objects.filter(semester=semester, department=department, day=day).exists():
#             return Response({'error': 'Timetable already exists for this semester, department, and day.'}, status=status.HTTP_400_BAD_REQUEST)

#         serializer.save()
#         # day = serializer.data.get('slot_4')
#         # print(len(day))
#         # validated_data = serializer.validated_data
#         # ###
#         calenderMainTableAdd(serializer.data.get('joining_yr'), serializer.data.get('department'), serializer.data.get('day'), serializer.data.get('slot_1'), serializer.data.get('slot_2'), serializer.data.get('slot_3'),
#                              serializer.data.get('slot_4'), serializer.data.get('slot_5'), serializer.data.get('slot_6'), serializer.data.get('slot_7'))

#         return Response(serializer.data, status=201)
#     else:
#         print(serializer.errors)
#         return Response(serializer.errors, status=400)

@api_view(['POST'])
def addTimetable(request):
    print("her1")
    serializer = TimeTableSerializer(data=request.data)
    if serializer.is_valid():
        print("here2")
        semester = serializer.validated_data.get('semester')
        # joining_yr = serializer.validated_data.get('joining_yr')
        department = serializer.validated_data.get('department')
        day = serializer.validated_data.get('day')

        
        # yrs = ['2021', '2022', '2023', '2024']
        yrs = ['2023', '2022', '2021', '2020']
        joining_yr=None
        if semester==1 or semester==2:
            joining_yr=yrs[0]
        elif semester==3 or semester==4:
            joining_yr=yrs[1]
        elif semester==5 or semester==6:
            joining_yr=yrs[2]
        elif semester==7 or semester==8:
            joining_yr=yrs[3]
        print("here3")
        # Check if the combination of semester, department, and day already exists
        if TimeTable.objects.filter(semester=semester, department=department, day=day).exists():
            return Response({'error': 'Timetable already exists for this semester, department, and day.'}, status=status.HTTP_400_BAD_REQUEST)
        print("here4")
        serializer.save()
        print("here7")
        # day = serializer.data.get('slot_4')
        # print(len(day))
        # validated_data = serializer.validated_data
        # ###
        calenderMainTableAdd(joining_yr, serializer.data.get('department'), serializer.data.get('day'), serializer.data.get('slot_1'), serializer.data.get('slot_2'), serializer.data.get('slot_3'),serializer.data.get('slot_4'), serializer.data.get('slot_5'), serializer.data.get('slot_6'), serializer.data.get('slot_7'))

        return Response(serializer.data, status=201)
    else:
        print("here5")
        print(serializer.errors)
        return Response(serializer.errors, status=400)
    
@api_view(['GET'])
def getStudentsWithAttendanceShortage(request):
    course_code = request.GET.get('course_code')
    department  = request.GET.get('department')
    total_classes = CurrentCourses.objects.filter(course_code=course_code,department=department)[0].total_classes
    semester = CourseList.objects.filter(course_code=course_code,department=department)[0].semester

    students_list = StudentInfo.objects.filter(semester = semester,department = department)
    shortage_list=[]
    for student in students_list:
        absent_days = len(Absentees.objects.filter(course_code=course_code,roll_no = student.roll_no))
        if 1-(absent_days/total_classes) <0.8:
            shortage_list.append([student.roll_no,student.name,(1-(absent_days/total_classes))*100])
    return Response({"shortage_list":shortage_list})

@api_view(['POST'])
def addResultLab(request) :
    records=request.data
    course_code=records[0]['course_code']
    LabResult.objects.filter(course_code=course_code).delete()

    for record in records :
        print(record)
        course_code=record['course_code']
        faculty=record['faculty']
        internal_marks=record['internal_marks']
        end_lab=record['internal_marks']
        grade=record['grade']
        roll_no=record['roll_no']
        obj=LabResult(course_code=course_code,faculty=faculty,internal_marks=internal_marks,end_lab=end_lab,grade=grade,roll_no=roll_no)
        obj.save()
    return Response({})


@api_view(['GET'])
def getCourseType(request) :
    course_code=request.GET.get('course_code')
    print('course_code',course_code)
    course_type=CourseList.objects.filter(course_code=course_code)[0].course_type

    return Response({'course_type':course_type})


@api_view(['GET'])
def getLabResultForStudentForCourse(request) :
    course_code=request.GET.get('course_code')
    roll_no=request.GET.get('roll_no')

    result_object=LabResult.objects.filter(roll_no=roll_no,course_code=course_code)[0]

    return Response({'internal_marks' : result_object.internal_marks,'end_lab' : result_object.end_lab,'grade' : result_object.grade})