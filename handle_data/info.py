class Info:
    def __init__(self):
        self.day = 0
        self.max = 100000.0
        self.min = 100000.0
        self.average = 100000.0

    def __str__(self):
        return "{}: {}, {}, {}".format(self.day, self.max, self.min, self.average)
