import datetime
import json
import requests
import urllib3
import xml.etree.ElementTree as ET
from math import modf

start = datetime.datetime.now()

DOCTORS = 'Employees.xml'
SCHEDULE = 'Schedule.xml'
CELLS = 'cells.json'


# Positions of rows
UID = 0
NAME1 = 2
NAME2 = 3
NAME3 = 4
SPEC = 5
EID = 2
DATE = 1
ST_TIME = 2
END_TIME = 3
TIMESTAMP = 5
CLINIC_ID = 6

json_data = {
    'data': {}
}

clin_id = ''


def get_timestamp(timestamp):
    splited = datetime.datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%S')
    if splited.hour == 0 and splited.minute == 0:
        return datetime.timedelta(minutes=30)
    return datetime.timedelta(hours=splited.hour, minutes=splited.minute)


def replace_none(string):
    return string if string else ''


def str_to_datetime(str_time):
    converted = datetime.datetime.strptime(str_time, '%Y-%m-%dT%H:%M:%S')
    return converted


def get_date_from_str(string):
    converted = datetime.datetime.strptime(string, '%Y-%m-%dT%H:%M:%S').strftime('%Y-%m-%d')
    return converted


def get_time_from_str(string):
    converted = datetime.datetime.strptime(string, '%Y-%m-%dT%H:%M:%S').strftime('%H:%M')
    return converted


def get_time_from_datetime(time):
    converted = time.strftime('%H:%M')
    return converted


end1 = datetime.datetime.now()

doctors_tree = ET.parse(DOCTORS)
doctors_root = doctors_tree.getroot()

for doctor in doctors_root:
    if doctor[CLINIC_ID].text == '00000000-0000-0000-0000-000000000000':
        continue
    clin_id = doctor[CLINIC_ID].text
    json_data.setdefault(clin_id, 'МИС 1С БИТ УМЦ')
    json_data['data'].setdefault(clin_id, {})
    name1 = replace_none(doctor[NAME1].text)
    name2 = replace_none(doctor[NAME2].text)
    name3 = replace_none(doctor[NAME3].text)
    spec = replace_none(doctor[SPEC].text)
    entry = {
        'efio': '{} {} {}'.format(name1, name2, name3).strip(),
        'espec': spec,
        'cells': []
    }
    json_data['data'][clin_id][doctor[UID].text] = entry

end2 = datetime.datetime.now()

schedule_tree = ET.parse(SCHEDULE)
schedule_root = schedule_tree.getroot()

for schedule in schedule_root:
    if schedule[2].text not in json_data['data'][clin_id]:
        continue
    doctor = json_data['data'][clin_id][schedule[2].text]
    timestamp = get_timestamp(schedule[TIMESTAMP].text)
    for free_cell in schedule[4][0]:
        time = str_to_datetime(free_cell[ST_TIME].text)
        end = str_to_datetime(free_cell[END_TIME].text)
        while time + timestamp <= end:
            end_time = time + timestamp
            cell = {
                'dt': get_date_from_str(free_cell[DATE].text),
                'time_start': get_time_from_datetime(time),
                'time_end': get_time_from_datetime(end_time),
                'free': True
            }
            doctor['cells'].append(cell)
            time = end_time
    for busy_cell in schedule[4][1]:
        cell = {
            'dt': get_date_from_str(busy_cell[DATE].text),
            'time_start': get_time_from_str(busy_cell[ST_TIME].text),
            'time_end': get_time_from_str(busy_cell[END_TIME].text),
            'free': False
        }
        doctor['cells'].append(cell)

end3 = datetime.datetime.now()

result = json.dumps(json_data, sort_keys=True, indent=4)
with open(CELLS, 'w') as json_file:
    json_file.write(result)

end4 = datetime.datetime.now()

urllib3.disable_warnings()
response = requests.post(
    'https://api.prodoctorov.ru/mis/send_cells/',
    data={
        'login': 'test-irhin-sergey',
        'password': 'skk42g6ufe5h94pkttxab5rj1cvdb7rc',
        'cells': result
    },
    verify=False
)

if response.status_code // 10 == 20:
    print('Request successful')
    print('Message: {}'.format(response.text))
else:
    print('Request unsuccessful')
    print('Error: {}'.format(response.text))
    print('Error code: {}'.format(response.status_code))

end = datetime.datetime.now()


print('Doctors parser and filler {}'.format(str(end2 - end1)))
print('Cells parser and filler {}'.format(str(end3 - end2)))
print('Creating json {}'.format(str(end4 - end3)))
print('Sending request {}'.format(str(end - end4)))
print('Whole without request {}'.format(str(end4 - start)))
