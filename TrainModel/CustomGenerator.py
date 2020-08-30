import numpy as np
import keras
from PIL import Image
import random


class SequenceGenerator(keras.utils.Sequence):

    def __init__(self, labels, batch_size, directory):
        self.batch_size = batch_size
        self.directory = directory
        self.labels = labels
        self.data = np.fromfile(directory, sep=',')

    def __len__(self):
        return (np.ceil(len(self.labels)/float(self.batch_size))).astype(np.int)

    def __getitem__(self, item):
        # batch = self.labels[min(item * self.batch_size, len(self.labels)-self.batch_size):
        #                     min((item+1)*self.batch_size, len(self.labels))]
        batch = self.labels[item * self.batch_size:(item+1)*self.batch_size]
        answer = np.empty(0, float)
        for ind in batch:
            # temp = np.asarray(Image.open(self.directory + str(file_name) + '.png'))
            # print(temp.shape)
            # temp = temp[:, :, 0]
            # data = temp/255.0
            # print(data.shape)
            data = self.data[ind*8: ind*8 + 28]
            # data[20] = 0.49
            # data[19] = 0.4
            # data[21] = 0.3
            # for i in range(28):
            #     data[i] = 0.3 - random.randint(90, 90)*0.001
            # print(ind)
            answer = np.append(answer, data)

        oof = answer.reshape(self.batch_size, 28, 1)

        return oof, oof.copy()
