
class AppSingleton(object):
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(AppSingleton, cls).__new__(cls)
        return cls.instance
    