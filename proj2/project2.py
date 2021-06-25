import csv
import datetime
import json
from math import modf
import requests
import urllib3

start = datetime.datetime.now()

DOCTORS = 'infoclinic_doctors.csv'
SCHEDULE = 'infoclinic_doctschedule.csv'
TALONS = 'infoclinic_schedule.csv'
CLINICS = 'infoclinic_clinics.csv'
CELLS = 'cells.json'

json_data = {}


def csv_read(file, column_number):
    with open(file, encoding='utf-16', newline='') as csv_res:
        reader = csv.reader(csv_res, delimiter=';')
        output = []
        for row in reader:
            if len(row) != 0 and not row[0].isdigit() and row[0] != '-1':
                headers = row
                continue
            if len(row) == column_number and row[0] != '-1':
                output.append(dict(zip(headers, row)))
                #print(dict(zip(headers, row)))
        return output


end1 = datetime.datetime.now()


def time_conv(hours, minutes):
    return datetime.timedelta(hours=int(hours), minutes=int(minutes))


end2 = datetime.datetime.now()


def get_timestamp(timestamp):
    if not timestamp.isdigit():
        return datetime.timedelta(minutes=30)
    return datetime.timedelta(minutes=int(timestamp))


def get_formated_time(timedelta):
    return (datetime.datetime.min + timedelta).strftime('%H:%M')


def stamp_compare(busy_start_unconv, busy_end_unconv, free_start, free_end):
    cond1 = busy_start >= free_start and busy_start < free_end and busy_end >= free_end
    cond2 = busy_start <= free_start and busy_end > free_start and busy_end <= free_end
    cond3 = busy_start >= free_start and busy_start < free_end and busy_end > free_start and busy_end <= free_end
    cond4 = busy_start <= free_start and busy_end >= free_end
    cond5 = busy_start == busy_end and busy_start == free_start
    return cond1 or cond2 or cond3 or cond4 or cond5


def get_formated_date(date):
    return date.split()[0]


end3 = datetime.datetime.now()

doctors_reader = csv_read(DOCTORS, 9)
schedule_reader = csv_read(SCHEDULE, 9)
talons_reader = csv_read(TALONS, 6)
clinics_reader = csv_read(CLINICS, 4)

cells = []

for schedule in schedule_reader:
    timestamp = get_timestamp(schedule['SHINTERV'])
    time = time_conv(schedule['BEGHOUR'], schedule['BEGMIN'])
    while time < time_conv(schedule['ENDHOUR'], schedule['ENDMIN']):
        end_time = time + timestamp
        cell = {
            'DCODE': schedule['DCODE'],
            'dt': get_formated_date(schedule['WDATE']),
            'time_start': get_formated_time(time),
            'time_end': get_formated_time(end_time),
            'free': True,
            'room': ''
        }
        for busy_talon in talons_reader:
            busy_start = time_conv(busy_talon['BHOUR'], busy_talon['BMIN'])
            busy_end = time_conv(busy_talon['FHOUR'], busy_talon['FMIN'])
            if busy_talon['DCODE'] == cell['DCODE'] and schedule['WDATE'] == busy_talon['WORKDATE'] and \
                    stamp_compare(busy_start, busy_end, time, end_time):
                cell['free'] = False
        print(cell)
        cells.append(cell)
        time += timestamp

end4 = datetime.datetime.now()

doctors = []

for doctor in doctors_reader:
    entry = {
        'DCODE': doctor['DCODE'],
        'FILIAL': doctor['FILIAL'],
        'efio': doctor['FULLNAME'],
        'espec': doctor['DOCTPOST'],
        'cells': []
    }
    for cell in cells:
        if doctor['DCODE'] == cell['DCODE']:
            fin_cell = {
                'dt': cell['dt'],
                'time_start': cell['time_start'],
                'time_end': cell['time_end'],
                'free': cell['free'],
                'room': ''
            }
            entry[doctor['DCODE']]['cells'].append(fin_cell)
    doctors.update(entry)

end5 = datetime.datetime.now()

json_data = {'data': {}}

for clinic in clinics_reader:
    json_data['data'].update({clinic['FILID']: {}})
    for doctor in doctors:
        if clinic['FILID'] == doctor['FILIAL']:
            entry = {
                doctor['DCODE']: {
                    'FILIAL': doctor['FILIAL'],
                    'efio': doctor['efio'],
                    'espec': doctor['espec'],
                    'cells': doctor[cells]
                }
            }
            json_data['data'][clinic['FILID']].update(entry)
    json_data.update({clinic['FILID']: clinic['FULLNAME']})

end6 = datetime.datetime.now()

res = json.dumps(json_data, sort_keys=True, indent=4)
with open(CELLS, 'w') as json_file:
    json_file.write(res)

end7 = datetime.datetime.now()
exit()
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