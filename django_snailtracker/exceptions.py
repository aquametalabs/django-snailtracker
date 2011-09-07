class SnailtrackerError(Exception):
    pass

class ParentNotFoundError(SnailtrackerError):
    
    def __init__(self, child_instance, parent):
        self.child_instance = child_instance
        self.parent = parent
        super(ParentNotFoundError, self).__init__()

    def __str__(self):
        return '%s has no parent attribute %s' % \
                (repr(self.child_instance), self.parent)

