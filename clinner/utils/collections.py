class Register(dict):
    """
    Special case of dictionary that keys cannot be replaced.
    """
    def __setitem__(self, key, value):
        if key in self:
            raise KeyError('{} is already registered'.format(key))

        dict.__setitem__(self, key, value)

    def __repr__(self):
        return dict.__repr__(self)

    def __str__(self):
        return dict.__str__(self)
