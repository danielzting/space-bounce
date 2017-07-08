"""
Easy-to-use timer module for PyGame.
"""

class Timer():
    """Timer class, supporting countdown and stopwatch modes."""
    def __init__(self, start):
        """Initialize a Timer."""
        # Sanitize input
        if not isinstance(start, tuple):
            raise ValueError('time must be specified as tuple')
        if not len(start) == 3:
            raise TypeError('time must be')
        for number in start:
            if not isinstance(number, int):
                raise ValueError('times must be of type int')
        # Timer data structure
        self.time = {'hours': None, 'minutes': None, 'seconds': None}
        self.start = (0, 0, 0, 0)
        if start == None:
            self.mode = 'up'
        else:
            self.mode = 'down'
            for measurement, number in zip(self.time, start):
                self.time[measurement] = number
            self.start = self.time

    def tick(self, fps):
        """Make the timer pass one frame. If countdown timer has ended, return False."""
        # Pass one frame
        if self.mode == 'up':
            self.time['seconds'] += 1 / fps
            # Carry
            if self.time['seconds'] >= 60:
                self.time['seconds'] = 0
                self.time['minutes'] += 1
            if self.time['minutes'] >= 60:
                self.time['minutes'] = 0
                self.time['hours'] += 1
        elif self.mode == 'down':
            self.time['seconds'] -= 1 / fps
            # Carry
            if self.time['seconds'] < 0:
                self.time['seconds'] = 60 - 1 / fps
                self.time['minutes'] -= 1
            if self.time['minutes'] < 0:
                self.time['minutes'] = 59
                self.time['hours'] -= 1
            if self.time['hours'] < 0:
                return False

    def str_time(self):
        """Return the time formatted as HH:MM:SS."""
        return ':'.join(str(int(x)).zfill(2) for x in self.time.values())
