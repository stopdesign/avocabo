from enum import Enum


class ChoiceEnum(Enum):
    """
    Класс для вариантов значений, которые передаются в поля:
    models.PositiveIntegerField(choices=Intervals.choices(), default=Intervals.First)
    """

    @classmethod
    def choices(cls):
        choices = list()

        for item in cls:
            choices.append((item.value, str(item)))

        return tuple(choices)

    @classmethod
    def values(cls):
        values = list()

        for item in cls:
            values.append(item.value)

        return tuple(values)

    def __str__(self):
        return self.name.replace('_', ' ')

    def __int__(self):
        return self.value
