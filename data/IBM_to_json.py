import os
import re
import json

data_path = os.path.dirname(os.path.abspath(__file__))
data_name = '/IBM.txt'
data_output_name = '/IBM.json'

f = open(data_path + data_name, 'r')
raw_data = f.read()
f.close()

transactions = []
raw_data = raw_data.split('\n')
for single_data in raw_data:
    single_data = re.split(r'\s+', single_data)
    if str(len(transactions)) != single_data[0]:
        transactions.append([])
    transactions[int(single_data[0]) - 1].append(single_data[2])

transactions = json.dumps(transactions, indent=4)

f = open(data_path + data_output_name, 'w')
f.write(transactions)
f.close()
