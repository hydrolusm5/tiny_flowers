from datetime import datetime
from datetime import timedelta


current_time = datetime.now()
mins = 2
time_limit = current_time + timedelta(minutes=1)
print(f' future time: {time_limit}')
print(f'current time: {current_time}')

while True:
    current_time = datetime.now()
    if current_time >= time_limit:
        print('yo') # Perform action
        break

