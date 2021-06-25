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

json_data = {
    '1': 'МИС Архимед',
    'data': {'1': {}}
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


end1 = datetime.datetime.now()


def time_conv(time):
    conv_to_hours = float(time) * 24
    unrounded_minutes, hours = modf(conv_to_hours)
    minutes = round(unrounded_minutes * 60, 0)
    return datetime.timedelta(hours=int(hours), minutes=int(minutes))


end2 = datetime.datetime.now()


def get_timestamp(timestamp):
    if not timestamp.isdigit() or timestamp == '0' or timestamp == '1':
        return datetime.timedelta(minutes=30)
    return datetime.timedelta(minutes=int(timestamp))


def get_formated_time(timedelta):
    return (datetime.datetime.min + timedelta).strftime('%H:%M')


def stamp_compare(busy_start_unconv, busy_end_unconv, free_start, free_end):
    busy_start = time_conv(busy_start_unconv)
    busy_end = time_conv(busy_end_unconv)
    #cond1 = busy_start >= free_start and busy_start < free_end and busy_end >= free_end
    #cond2 = busy_start <= free_start and busy_end > free_start and busy_end <= free_end
    #cond3 = busy_start >= free_start and busy_start < free_end and busy_end > free_start and busy_end <= free_end
    #cond4 = busy_start <= free_start and busy_end >= free_end
    #cond5 = busy_start == busy_end and busy_start == free_start
    #return cond1 or cond2 or cond3 or cond4 or cond5
    cond = busy_end > free_start and busy_start < free_end
    return cond


end3 = datetime.datetime.now()

doctors_reader = csv_read(DOCTORS, 8)
schedule_reader = csv_read(SCHEDULE, 9)
talons_reader = csv_read(TALONS, 6)

cells = []

for doctor in doctors_reader:
    if doctor['ID'] == '':
        continue
    entry = {
        doctor['ID']: {
            'efio': doctor['FULLNAME'],
            'espec': '',
            'cells': []
        }
    }
    timestamp = get_timestamp(doctor['TIMESCALE'])
    for schedule in schedule_reader:
        if schedule['DOCID'] != doctor['ID']:
            continue
        time = time_conv(schedule['BEGINTIME'])
        while time < time_conv(schedule['ENDTIME']):
            end_time = time + timestamp
            cell = {
                'docid': doctor['ID'],
                'dt_raw': schedule['SHIFTDATE'],
                'start_raw': time,
                'end_raw': end_time,
                'dt': str(datetime.date(1899, 12, 30) + datetime.timedelta(int(schedule['SHIFTDATE']))),
                'time_start': get_formated_time(time),
                'time_end': get_formated_time(end_time),
                'free': True,
            }
            cells.append(cell)
            time += timestamp
    json_data['data']['1'].update(entry)

end4 = datetime.datetime.now()

for cell in cells:
    for busy_talon in talons_reader:
        if busy_talon['DOCID'] == cell['docid'] and cell['dt_raw'] == busy_talon['SHIFTDATE'] and \
                stamp_compare(busy_talon['BEGINTIME'], busy_talon['ENDTIME'], cell['start_raw'], cell['end_raw']):
            cell['free'] = False

end5 = datetime.datetime.now()

for doctor_id, doctor_data in json_data['data']['1'].items():
    for cell in cells:
        if doctor_id == cell['docid']:
            fin_cell = {
                'dt': cell['dt'],
                'time_start': cell['time_start'],
                'time_end': cell['time_end'],
                'free': cell['free'],
                'room': ''
            }
            doctor_data['cells'].append(fin_cell)

end6 = datetime.datetime.now()

res = json.dumps(json_data, sort_keys=True, indent=4)
with open(CELLS, 'w') as json_file:
    json_file.write(res)

end7 = datetime.datetime.now()

urllib3.disable_warnings()

check = requests.post(
    'https://api.prodoctorov.ru/mis/send_cells/',
    data={
        'login': 'test-irhin-sergey',
        'password': 'skk42g6ufe5h94pkttxab5rj1cvdb7rc',
        'cells': res
    },
    verify=False
)

if check.status_code // 10 == 20:
    print('Request successful')
    print('Message: %s' % check.text)
else:
    print('Request unsuccessful')
    print('Error: %s' % check.text)

end = datetime.datetime.now()

print('Csv_read time ' + str(end1 - start))
print('Time_conv time ' + str(end2 - end1))
print('Get_timestamp and get_time_h_m ' + str(end3 - end2))
print('Cells parser ' + str(end4 - end3))
print('Busy cells parser ' + str(end5 - end4))
print('Cells filler ' + str(end6 - end5))
print('Creating json ' + str(end7 - end6))
print('Sending request ' + str(end - end7))
print('Whole without request ' + str(end7 - start))
