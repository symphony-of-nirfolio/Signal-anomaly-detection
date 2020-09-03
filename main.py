import os

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

from gui.gui import main_ui

if __name__ == "__main__":
    main_ui()
