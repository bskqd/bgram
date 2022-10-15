class MissingTasksSchedulerException(Exception):
    def __init__(self):
        self.message = 'Tasks scheduler is required for this action but missing'

    def __str__(self):
        return repr(self.message)
