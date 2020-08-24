import random
from keras.layers import Input, Conv2D, MaxPooling2D, UpSampling2D
from keras.models import Model
from keras.optimizers import RMSprop
from keras.callbacks import EarlyStopping, ModelCheckpoint
from matplotlib import pyplot as plt
from CustomGenerator import SequenceGenerator

in_channel = 1
in_x = 72
in_y = 96

epochs = 40
batch_size = 4
input_img = Input(shape=(in_x, in_y, in_channel))


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
model.compile(loss='mean_squared_error', optimizer=RMSprop())
model.summary()

early_stopper = EarlyStopping(patience=5, verbose=1)
check_pointer = ModelCheckpoint('checkpoints/01_temperature.h5', verbose=1, save_best_only=True)

all_samples = [i for i in range(113)]
random.shuffle(all_samples)
train = all_samples[:68]
valid = all_samples[68:92]
test = all_samples[92:]
with open('split/train/01.dat', 'w') as file:
    file.write(" ".join(str(elem) for elem in train) + "\n")
with open('split/valid/01.dat', 'w') as file:
    file.write(" ".join(str(elem) for elem in valid) + "\n")
with open('split/test/01.dat', 'w') as file:
    file.write(" ".join(str(elem) for elem in test) + "\n")

train_generator = SequenceGenerator(train, batch_size, 'temp_graphics/01/')
valid_generator = SequenceGenerator(valid, batch_size, 'temp_graphics/01/')

history = model.fit_generator(generator=train_generator,
                              steps_per_epoch=len(train_generator),
                              epochs=epochs,
                              verbose=1,
                              validation_data=valid_generator,
                              validation_steps=len(valid_generator),
                              callbacks=[early_stopper, check_pointer])

print(history.history.keys())
# "Loss"
plt.plot(history.history['loss'])
plt.plot(history.history['val_loss'])
plt.title('model loss')
plt.ylabel('loss')
plt.xlabel('epoch')
plt.legend(['train', 'validation'], loc='upper left')
plt.show()



