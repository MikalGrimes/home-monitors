import boto3
import os
import glob
import time
import datetime
 
os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')


def read_temp_raw():
    base_dir = '/sys/bus/w1/devices/'
    device_folder = glob.glob(base_dir + '28*')[0]
    device_file = device_folder + '/w1_slave'

    f = open(device_file, 'r')
    lines = f.readlines()
    f.close()
    return lines


def read_temp():
    lines = read_temp_raw()
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw()
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        temp_c = float(temp_string) / 1000.0
        temp_f = temp_c * 9.0 / 5.0 + 32.0
        return {'c': temp_c, 'f': temp_f}


def log_metric(location, metric_name, metric_value):
    session = boto3.Session(profile_name='bg')
    client = session.client('cloudwatch')
    
    response = client.put_metric_data(
        Namespace='bghouse',
        MetricData=[
            {
                'MetricName': metric_name,
                'Dimensions': [
                    {
                        'Name': 'location',
                        'Value': location
                    }
                ],
                'Timestamp': int(time.time()),
                'Value': metric_value,
                'Unit': 'None'
            },
        ]
    )


temp_f = read_temp()['f']
print(str(datetime.datetime.now()) + " Logging temperature: " + str(temp_f))
log_metric("garage/wine-fridge", "temperature", temp_f)
