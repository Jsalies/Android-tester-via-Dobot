from abc import ABCMeta, abstractmethod


class AbstractEnergyCollector:
    __metaclass__ = ABCMeta

    @abstractmethod
    def start(self, ouputEnergyFileName):
        ...

    @abstractmethod
    def stop(self):
        ...
        