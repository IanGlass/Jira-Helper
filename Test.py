from datetime import datetime
from dateutil import parser

test = datetime

#a = datetime.datetime.now()
dt = '2018-07-17 12:01:57.783129'
#b = datetime.strptime(dt, '%Y-%m-%d %H:M:S.%f')
b = parser.parse(dt)
a = datetime.now() #get current date
diff = (a - b).total_seconds()

print(diff)
