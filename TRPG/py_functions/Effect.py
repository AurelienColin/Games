class Effect():
    def __init__(self, properties, power, duration, orig):
        self.properties = properties
        self.power = power
        self.duration = duration
        self.since = 0
        self.orig = orig