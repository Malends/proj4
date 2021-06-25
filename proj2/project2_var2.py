import csv
import datetime
import json
import requests
import urllib3
from math import modf

start = datetime.datetime.now()

DOCTORS = 'infoclinic_doctors.csv'
SCHEDULE = 'infoclinic_doctschedule.csv'
TALONS = 'infoclinic_schedule.csv'
CLINICS = 'infoclinic_clinics.csv'
CELLS = 'cells.json'

json_data = {}


def csv_read(file, column_number):
    with open(file, encoding='PT154', newline='') as csv_res:
        reader = csv.reader(csv_res, delimiter=';')
        output = []
        for row in reader:
            if len(row) != 0 and not row[0].isdigit() and row[0] != '-1':
                headers = row
                continue
            if len(row) == column_number and row[0] != '-1':
                output.append(dict(zip(headers, row)))
        return output


def time_conv(hours, minutes):
    return datetime.timedelta(hours=int(hours), minutes=int(minutes))


def get_timestamp(timestamp):
    if not timestamp.isdigit():
        return datetime.timedelta(minutes=30)
    return datetime.timedelta(minutes=int(timestamp))


def get_formated_time(timedelta):
    return (datetime.datetime.min + timedelta).strftime('%H:%M')


def stamp_compare(busy_start_unconv, busy_end_unconv, free_start_unconv, free_end_unconv):
    free_start = time_conv(*free_start_unconv.split(':'))
    free_end = time_conv(*free_end_unconv.split(':'))
    cond = busy_end > free_start and busy_start < free_end
    return cond


def get_formated_date(date):
    return date.split()[0]


end1 = datetime.datetime.now()

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
        }
        cells.append(cell)
        time += timestamp

end2 = datetime.datetime.now()

doctors = {}

for doctor in doctors_reader:
    dcode = doctor['DCODE']
    entry = {
        'DCODE': dcode,
        'FILIAL': doctor['FILIAL'],
        'efio': doctor['FULLNAME'],
        'espec': doctor['DOCTPOST'],
        'cells': []
    }
    for cell in cells:
        if dcode == cell['DCODE']:
            fin_cell = {
                'dt': cell['dt'],
                'time_start': cell['time_start'],
                'time_end': cell['time_end'],
                'free': cell['free'],
                'room': ''
            }
            entry[dcode]['cells'].append(fin_cell)
    doctors[dcode] = entry

end3 = datetime.datetime.now()

for busy_talon in talons_reader:
    busy_start = time_conv(busy_talon['BHOUR'], busy_talon['BMIN'])
    busy_end = time_conv(busy_talon['FHOUR'], busy_talon['FMIN'])
    busy_date = get_formated_date(busy_talon['WORKDATE'])
    doctor = doctors[busy_talon['DCODE']]
    for cell in doctor['cells']:
        if cell['dt'] == busy_date and \
                stamp_compare(busy_start, busy_end, cell['time_start'], cell['time_end']):
            cell['free'] = False

end4 = datetime.datetime.now()

json_data = {'data': {}}

for clinic in clinics_reader:
    json_data['data'].update({clinic['FILID']: {}})
    for doctor in doctors.values():
        if clinic['FILID'] == doctor['FILIAL']:
            entry = {doctor['DCODE']: {
                    'efio': doctor['efio'],
                    'espec': doctor['espec'],
                    'cells': doctor['cells']
                }
            }
            json_data['data'][clinic['FILID']].update(entry)
    json_data.update({clinic['FILID']: clinic['FULLNAME']})

end5 = datetime.datetime.now()

result = json.dumps(json_data, sort_keys=True, indent=4)
with open(CELLS, 'w') as json_file:
    json_file.write(result)

end6 = datetime.datetime.now()

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

print('Csv_read time {}'.format(str(end1 - start)))
print('Cells finder {}'.format(str(end2 - end1)))
print('Cells filler for doctors {}'.format(str(end3 - end2)))
print('Busy cells parser {}'.format(str(end4 - end3)))
print('Clinics parser and filler {}'.format(str(end5 - end4)))
print('Creating json {}'.format(str(end6 - end5)))
print('Sending request {}'.format(str(end - end6)))
print('Whole without request {}'.format(str(end6 - start)))
