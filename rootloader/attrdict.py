class attrdict(dict):
    """
        Provides common functions for dictionaries of data containers
    """

    def __getattr__(self, name):
        if name in self.keys():
            return self[name]
        else:
            return getattr(dict, name)

    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

    def __repr__(self):
        klist = list(self.keys())
        if klist:
            klist.sort()
            s = self.__class__.__name__+': {'
            for k in self.keys():

                if type(k) is str:
                    if k[:2] == "__":
                        continue
                    s+= f"'{k}', "

                else:
                    s+=f'{k}, '
            s = s[:-2]
            s+='}'
            return s
        else:
            return self.__class__.__name__ + "()"

    def __dir__(self):
        return list(self.keys())

    def copy(self):
        """Make a copy of this object"""
        copy = attrdict()
        for key, value in self.items():
            if hasattr(value, 'copy'):
                copy[key] = value.copy()
            else:
                copy[key] = value
        return copy
