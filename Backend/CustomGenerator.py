import numpy as np
import keras


class SequenceGenerator(keras.utils.Sequence):

    def __init__(self, labels, batch_size, data, scale, window_size):
        self.batch_size = batch_size
        self.labels = labels
        self.data = data
        self.scale = scale
        self.window_size = window_size

    def __len__(self):
        return (np.ceil(len(self.labels)/float(self.batch_size))).astype(np.int)

    def __getitem__(self, item):
        batch = self.labels[item * self.batch_size:(item+1)*self.batch_size]
        answer = np.empty(0, float)
        for ind in batch:
            data = self.data[ind*self.scale: ind*self.scale + self.window_size]
            answer = np.append(answer, data)

        answer = answer.reshape(self.batch_size, self.window_size, 1)

        return answer, answer.copy()
