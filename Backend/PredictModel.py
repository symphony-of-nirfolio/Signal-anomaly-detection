import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

from keras.layers import Conv1D, GlobalMaxPool1D, Dense, MaxPooling1D
from keras.models import Model, Sequential
from keras.callbacks import EarlyStopping, ModelCheckpoint
from CustomGenerator import SequenceGenerator
import time

import random
import numpy as np
import shutil
from matplotlib import pyplot as plt

