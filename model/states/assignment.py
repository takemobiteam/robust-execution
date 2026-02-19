class Assignment:
    # A variable / value assignment.
    def __init__(self, variable: str, value):
        self.variable = variable
        self.value = value

    def __eq__(self, other):
        return isinstance(other, Assignment) and self.__dict__ == other.__dict__

    def __str__(self):
        return f"{self.variable}={self.value}"