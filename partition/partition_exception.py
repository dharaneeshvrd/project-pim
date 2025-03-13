class PartitionError(Exception):
    """ Exception raised for all lpar related errors """
    def __init__(self, message):
        super().__init__(message)

    def __str__(self):
        return f"{self.message}"
