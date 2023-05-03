import abc


class Executor(abc.ABC):
    @abc.abstractmethod
    def __init__(self, *args, **kwargs):
        pass

    @abc.abstractmethod
    def execute(self, *args, **kwargs):
        pass

    @abc.abstractmethod
    def parse(self, *args, **kwargs):
        pass

    @abc.abstractmethod
    def save(self, *args, **kwargs):
        pass
