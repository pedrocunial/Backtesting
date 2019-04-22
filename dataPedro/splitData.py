import sys


step = 7 if len(sys.argv) < 2 else sys.argv[1]
input_file = '../^BVSP.csv' if len(sys.argv) < 3 else sys.argv[2]
train_file = 'train_data.csv'
test_file = 'test_data.csv'


with open(input_file, 'r') as fin:
    lines = fin.readlines()
    line_count = len(lines)
    i = 0
    train_data = []
    test_data = []
    for data in lines:
        if i < step:
            train_data.append(data)
            i += 1
        else:
            test_data.append(data)
            i = 0

with open(train_file, 'w') as fout:
    fout.writelines(train_data)

with open(test_file, 'w') as fout:
    fout.writelines(test_data)
