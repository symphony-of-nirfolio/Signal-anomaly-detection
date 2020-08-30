import random
from keras.layers import Input, Conv1D, GlobalMaxPool1D, Dense, MaxPooling1D, Flatten
from keras.models import Model, Sequential
from keras.optimizers import RMSprop
from keras.callbacks import EarlyStopping, ModelCheckpoint
from matplotlib import pyplot as plt
from CustomGenerator import SequenceGenerator

in_channel = 1
in_x = 28
in_y = 1

epochs = 10000
batch_size = 4
input_img = Input(shape=(in_x, in_y, in_channel))


model = Sequential()
model.add(Conv1D(filters=4, kernel_size=5, padding='same', activation='tanh', input_shape=(in_x, in_y)))
model.add(MaxPooling1D(4))
model.add(Conv1D(filters=8, kernel_size=3, padding='same', activation='tanh'))
model.add(GlobalMaxPool1D())
model.add(Dense(units=in_x, activation='tanh'))


model.compile(loss='mean_squared_error', optimizer='adam')
model.summary()

early_stopper = EarlyStopping(patience=10, verbose=1)
check_pointer = ModelCheckpoint('checkpoints/01_temperature_winter.h5', verbose=1, save_best_only=True)

all_samples = [i for i in range(1270)]
random.shuffle(all_samples)
train = all_samples[:764]
valid = all_samples[764:1020]
test = all_samples[1020:]
with open('split/train/01_w.dat', 'w') as file:
    file.write(" ".join(str(elem) for elem in train) + "\n")
with open('split/valid/01_w.dat', 'w') as file:
    file.write(" ".join(str(elem) for elem in valid) + "\n")
with open('split/test/01_w.dat', 'w') as file:
    file.write(" ".join(str(elem) for elem in test) + "\n")

train_generator = SequenceGenerator(train, batch_size, 'data_/winter_min.txt')
valid_generator = SequenceGenerator(valid, batch_size, 'data_/winter_min.txt')

history = model.fit_generator(generator=train_generator,
                              steps_per_epoch=len(train_generator),
                              epochs=epochs,
                              verbose=1,
                              validation_data=valid_generator,
                              validation_steps=len(valid_generator),
                              callbacks=[check_pointer, early_stopper])

print(history.history.keys())
# "Loss"
plt.plot(history.history['loss'])
plt.plot(history.history['val_loss'])
plt.title('model loss')
plt.ylabel('loss')
plt.xlabel('epoch')
plt.legend(['train', 'validation'], loc='upper left')
plt.show()



