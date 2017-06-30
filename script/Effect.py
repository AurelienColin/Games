class Effect():
    def __init__(self, properties, power, duration):
        self._properties = properties
        self._power = power
        self._duration = duration
        self._since = 0