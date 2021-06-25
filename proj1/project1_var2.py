import csv
import datetime
import json
import requests
import urllib3
from math import modf

start = datetime.datetime.now()

DOCTORS = 'archimed_doctors.csv'
SCHEDULE = 'archimed_doctorsshedule.csv'
TALONS = 'archimed_talons.csv'
CELLS = 'cells.json'

CLINIC_ID = '1'
DATE_TO_SUM = datetime.date(1899, 12, 30)

json_data = {
    CLINIC_ID: 'МИС Архимед',
    'data': {CLINIC_ID: {}}
}


def csv_read(file, column_number):
    with open(file, encoding='PT154', newline='') as csv_res:
        reader = csv.reader(csv_res, delimiter=';')
        output = []
        for row in reader:
            if len(row) != 0 and not row[0].isdigit():
                headers = row
                continue
            if len(row) == column_number:
                output.append(dict(zip(headers, row)))
        return output


def time_conv(time):
    conv_to_hours = float(time) * 24
    unrounded_minutes, hours = modf(conv_to_hours)
    minutes = round(unrounded_minutes * 60, 0)
    return datetime.timedelta(hours=int(hours), minutes=int(minutes))


def get_timestamp(timestamp):
    if not timestamp.isdigit() or timestamp == '0' or timestamp == '1':
        return datetime.timedelta(minutes=30)
    return datetime.timedelta(minutes=int(timestamp))


def get_formated_time(timedelta):
    return (datetime.datetime.min + timedelta).strftime('%H:%M')


def stamp_compare(busy_start, busy_end_, free_start_unconv, free_end_unconv):
    free_start = datetime.timedelta(hours=int(free_start_unconv[0]), minutes=int(free_start_unconv[1]))
    free_end = datetime.timedelta(hours=int(free_end_unconv[0]), minutes=int(free_end_unconv[1]))
    cond = busy_end > free_start and busy_start < free_end
    return cond


end1 = datetime.datetime.now()

doctors_reader = csv_read(DOCTORS, 8)
schedule_reader = csv_read(SCHEDULE, 9)
talons_reader = csv_read(TALONS, 6)

for doctor in doctors_reader:
    id = doctor['ID']
    if id == '':
        continue
    entry = {
        'efio': doctor['FULLNAME'],
        'espec': '',
        'cells': []
    }
    timestamp = get_timestamp(doctor['TIMESCALE'])
    for schedule in schedule_reader:
        if schedule['DOCID'] != id:
            continue
        time = time_conv(schedule['BEGINTIME'])
        while time < time_conv(schedule['ENDTIME']):
            end_time = time + timestamp
            cell = {
                'dt': str(DATE_TO_SUM + datetime.timedelta(int(schedule['SHIFTDATE']))),
                'time_start': get_formated_time(time),
                'time_end': get_formated_time(end_time),
                'free': True,
            }
            entry['cells'].append(cell)
            time += timestamp
    json_data['data'][CLINIC_ID][id] = entry

end2 = datetime.datetime.now()

for busy_talon in talons_reader:
    busy_start = time_conv(busy_talon['BEGINTIME'])
    busy_end = time_conv(busy_talon['ENDTIME'])
    busy_date = str(DATE_TO_SUM + datetime.timedelta(int(busy_talon['SHIFTDATE'])))
    doctor = json_data['data']['1'][busy_talon['DOCID']]
    for cell in doctor['cells']:
        free_start = cell['time_start'].split(':')
        free_end = cell['time_end'].split(':')
        if cell['dt'] == busy_date and stamp_compare(busy_start, busy_end, free_start, free_end):
            cell['free'] = False

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

print('Cells parser and filler {}'.format(str(end2 - end1)))
print('Busy cells parser {}'.format(str(end3 - end2)))
print('Creating json {}'.format(str(end4 - end3)))
print('Sending request {}'.format(str(end - end4)))
print('Whole without request {}'.format(str(end4 - start)))
