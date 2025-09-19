# can be used like a Lua table

class Table:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def __getitem__(self, key):
        return getattr(self, key)

    def __setitem__(self, key, value):
        setattr(self, key, value)

    def __delitem__(self, key):
        delattr(self, key)

    def __contains__(self, key):
        return hasattr(self, key)

    def __keys(self):
        return self.__dict__.keys()

    def __values(self):
        return self.__dict__.values()

    def __items(self):
        return self.__dict__.items()

    def __repr__(self):
        return f"Table({self.__dict__})"
