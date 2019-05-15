import numpy as np

from datetime import datetime
from sklearn.linear_model import LinearRegression


PBR = 'dataPedro/ADR.csv'
USDBRL = 'USDBRL.csv'
PETR = 'PETR3.csv'


events = {}

with open(PBR, 'r') as fin:
    pbr_data = fin.readlines()
    for line in pbr_data[1:]:
        cols = line.split(',')
        date = datetime.strptime(cols[0], '%d/%m/%y %H:%M')
        price = float(cols[2].replace(',', '.'))
        if date not in events:
            events[date] = {PBR: price}
        else:
            events[date][PBR] = price
    print(f'Done with {fin}')

with open(USDBRL, 'r') as fin:
    usdbrl_data = fin.readlines()
    for line in usdbrl_data[1:]:
        cols = line.split(';')
        date = datetime.strptime(cols[0], '%d/%m/%Y %H:%M:%S')
        price = float(cols[2].replace(',', '.'))
        if date not in events:
            events[date] = {USDBRL: price}
        else:
            events[date][USDBRL] = price
    print(f'Done with {fin}')

with open(PETR, 'r') as fin:
    petr_data = fin.readlines()
    for line in petr_data[1:]:
        cols = line.split(';')
        date = datetime.strptime(cols[0], '%d/%m/%Y %H:%M:%S')
        price = float(cols[2].replace(',', '.'))
        if date not in events:
            events[date] = {PETR: price}
        else:
            events[date][PETR] = price
    print(f'Done with {fin}')

X = []
y = []
for date in sorted(events.keys()):
    event = events[date]
    if PBR in event and USDBRL in event and PETR in event:
        X.append(event[PETR] / event[USDBRL])
        y.append(event[PBR])

X = np.array(X).reshape(-1, 1)
model = LinearRegression(fit_intercept=True).fit(X, y)
print(model.coef_)
