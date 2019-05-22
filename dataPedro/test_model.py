from train_model import (
    stack_data,
    create_y,
    read_data,
    load_model,
    TEST_FILE
)


test_data = read_data(TEST_FILE)
X_test, y_test = stack_data(test_data), create_y(test_data)

model = load_model()

predict = model.predict(X_test)
print(predict)
