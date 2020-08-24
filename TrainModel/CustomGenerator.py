import numpy as np
import keras
from PIL import Image


class SequenceGenerator(keras.utils.Sequence):

    def __init__(self, labels, batch_size, directory):
        self.labels = labels
        self.batch_size = batch_size
        self.directory = directory

    def __len__(self):
        return (np.ceil(len(self.labels)/float(self.batch_size))).astype(np.int)

    def __getitem__(self, item):
        batch = self.labels[min(item * self.batch_size, len(self.labels)-self.batch_size):
                            min((item+1)*self.batch_size, len(self.labels))]

        answer = np.empty(0, float)
        for file_name in batch:
            temp = np.asarray(Image.open(self.directory + str(file_name) + '.png'))
            # print(temp.shape)
            temp = temp[:, :, 0]

            data = temp/255.0
            # print(data.shape)
            answer = np.append(answer, data)

        oof = answer.reshape(self.batch_size, 72, 96, 1)

        return oof, oof.copy()
