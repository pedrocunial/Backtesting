import sys
import numpy as np

from keras.models import Sequential, model_from_json
from keras.layers import LSTM, Dense


N_STEPS = 10
TEST_FILE = 'test_data.csv'


def read_data(file_name='train_data.csv'):
    with open(file_name, 'r') as fin:
        data = [line.strip().split(',') for line in fin.readlines()]
        data = [d for d in data if d[1] not in ('null', 'Open')]
    return data


def stack_data(data, n_steps=N_STEPS):
    stacked = []
    for i in range(n_steps, len(data) - 1):
        stacked.append([[d[1]] for d in data[i - n_steps:i]])
    return np.array(stacked)


def create_y(data, n_steps=N_STEPS):
    return np.array([[d[1]] for d in data[n_steps + 1:]])


def create_model(n_features=1, n_steps=N_STEPS):
    model = Sequential()
    model.add(LSTM(50, activation='relu', input_shape=(n_steps, n_features)))
    model.add(Dense(1))
    model.compile(optimizer='adam', loss='mse')
    return model


def save_model(model):
    '''
    from
    https://machinelearningmastery.com/save-load-keras-deep-learning-models/
    '''
    # serialize model to JSON
    model_json = model.to_json()
    with open("model.json", "w") as json_file:
        json_file.write(model_json)
    # serialize weights to HDF5
    model.save_weights("model.h5")
    print("Saved model to disk")


def load_model(file_prefix='model'):
    # load json and create model
    json_file = open(file_prefix + '.json', 'r')
    loaded_model_json = json_file.read()
    json_file.close()
    loaded_model = model_from_json(loaded_model_json)
    # load weights into new model
    loaded_model.load_weights(file_prefix + ".h5")
    # evaluate loaded model on test data
    loaded_model.compile(optimizer='adam', loss='mse')
    return loaded_model


if __name__ == '__main__':
    if len(sys.argv) < 2:
        train = read_data()
    else:
        train = read_data(sys.argv[1])

    if len(sys.argv) < 3:
        test = read_data(TEST_FILE)
    else:
        test = read_data(sys.argv[2])

    X = stack_data(train)
    y = create_y(train)
    X_test = stack_data(test)
    y_test = create_y(test)

    model = create_model()
    model.fit(X, y, epochs=500, validation_data=(X_test, y_test))
    save_model(model)
