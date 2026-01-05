import abc
from typing import List, Dict, Optional

class DataProvider(abc.ABC):
    """Abstract interface for data providers."""

    @abc.abstractmethod
    def get_limit_up_pool(self, date: str) -> List[Dict]:
        raise NotImplementedError

    @abc.abstractmethod
    def get_lhb(self, date: str) -> List[Dict]:
        raise NotImplementedError

    @abc.abstractmethod
    def get_kline(self, code: str, start: str, end: str) -> List[Dict]:
        raise NotImplementedError

    @abc.abstractmethod
    def get_ytd_return(self, code: str, date: str) -> Optional[float]:
        raise NotImplementedError

    @abc.abstractmethod
    def get_stock_profile(self, code: str) -> Optional[Dict]:
        raise NotImplementedError

    @abc.abstractmethod
    def get_shareholders(self, code: str) -> Optional[List[Dict]]:
        raise NotImplementedError
