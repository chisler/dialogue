class Message(object):
    def __init__(self, text='', sender_name='', date=None):
        self.text = text
        self.sender_name = sender_name
        self.date = date

    def __str__(self):
        return '{}'.format(self.text)


