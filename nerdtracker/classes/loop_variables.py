class Loop_Variables_Class:

    def __init__(self, initial_dict):
        self.update(**initial_dict)
    
    def update(self, **kwargs):
        for key in kwargs.keys():
            setattr(self, key, kwargs[key])