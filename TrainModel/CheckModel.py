import random
from keras.layers import Input, Conv1D, GlobalMaxPool1D, Dense, MaxPooling1D, Flatten
from keras.models import Model, Sequential
from keras.optimizers import RMSprop
from keras.callbacks import EarlyStopping, ModelCheckpoint
from matplotlib import pyplot as plt
from CustomGenerator import SequenceGenerator
import numpy as np

in_channel = 1
in_x = 28
in_y = 1

epochs = 40
batch_size = 1

model = Sequential()
model.add(Conv1D(filters=4, kernel_size=5, padding='same', activation='tanh', input_shape=(in_x, in_y)))
model.add(MaxPooling1D(4))
model.add(Conv1D(filters=8, kernel_size=5, padding='same', activation='tanh'))
model.add(GlobalMaxPool1D())
# model.add(Dense(8, activation='tanh'))
model.add(Dense(units=in_x, activation='tanh'))

model.load_weights('checkpoints/01_temperature_winter.h5')
model.compile(loss='mean_squared_error', optimizer='adam')
model.summary()


test = np.fromfile('split/test/01_w.dat', sep=' ', dtype=int)

test_generator = SequenceGenerator(test, batch_size, 'data_/winter_min.txt')
results = model.predict_generator(generator=test_generator,
                                  steps=len(test_generator),
                                  verbose=1)

# results *= 255

data = np.fromfile('data_/winter_min.txt',sep=',')
for ind in range(results.shape[0]):
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    ax.set_ylim([0, 1])
    cur = data[test[ind]*8: test[ind]*8+28]
    temp = abs(results[ind, :] - cur)**2
    ax.plot(temp, 'g')
    for i in range(len(temp)):
        if temp[i] > 0.035:
            j = max(i-1, 0)
            oof = np.empty(0)
            pos = np.empty(0)
            oof = np.append(oof, temp[j])
            pos = np.append(pos, j)
            j += 1
            while len(temp) > j and temp[j] > 0.035:
                oof = np.append(oof, temp[j])
                pos = np.append(pos, j)
                j += 1
            if j < len(temp):
                oof = np.append(oof, temp[j])
                pos = np.append(pos, j)
            print(ind)
            ax.plot(pos, oof, 'r')

    fig.savefig('ans_graphics/win/1' + str(ind) + '.png', dpi=100)
    # print(cur)
    # print(results[ind, :])
    plt.close(fig)

'''
def autoencoder(input_img):
    # encoder
    conv1 = Conv2D(32, (3, 3), activation='relu', padding='same')(input_img) # 72 x 96 x 32
    pool1 = MaxPooling2D(pool_size=(2, 2))(conv1) # 36 x 48 x 32
    conv2 = Conv2D(64, (3, 3), activation='relu', padding='same')(pool1) # 36 x 48 x 64
    pool2 = MaxPooling2D(pool_size=(2, 2))(conv2) # 18 x 24 x 64
    conv3 = Conv2D(128, (3, 3), activation='relu', padding='same')(pool2) # 18 x 24 x 128
    pool3 = MaxPooling2D(pool_size=(2, 2))(conv3) # 9 x 12 x 128
    conv4 = Conv2D(256, (3, 3), activation='relu', padding='same')(pool3) # 9 x 12 x 256

    # decoder
    conv5 = Conv2D(256, (3, 3), activation='relu', padding='same')(conv4)  # 9 x 12 x 256
    up1 = UpSampling2D((2, 2))(conv5) # 18 x 24 x 256
    conv6 = Conv2D(128, (3, 3), activation='relu', padding='same')(up1) # 18 x 24 x 128
    up2 = UpSampling2D((2, 2))(conv6) # 36 x 48 x 128
    conv7 = Conv2D(64, (3, 3), activation='relu', padding='same')(up2) # 36 x 48 x 64
    up3 = UpSampling2D((2, 2))(conv7) # 72 x 96 x 64
    decoded = Conv2D(1, (3, 3), activation='sigmoid', padding='same')(up3) # 72 x 96 x 1
    return decoded


model = Model(input_img, autoencoder(input_img))
model.load_weights('checkpoints/01_temperature_batch_1.h5')
model.compile(loss='mean_squared_error', optimizer=RMSprop())
model.summary()

test = [70]

test_generator = SequenceGenerator(test, batch_size, 'temp_graphics/01/')
results = model.predict_generator(generator=test_generator,
                                  steps=len(test_generator),
                                  verbose=1)

results *= 255

for ind in range(results.shape[0]):
    save_img('dsd.png', results[ind, :, :, :])
'''



