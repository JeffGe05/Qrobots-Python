class DefaultDict(dict):
    def __init__(self, defaultvalue=None, *args, **kwargs):
        dict.__init__(self, *args, **kwargs)
        self.defaultvalue = defaultvalue

    def __getitem__(self, key):
        return self.get(key, self.defaultvalue)
