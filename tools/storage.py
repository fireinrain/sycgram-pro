import asyncio
import pickle
from os import mkdir, path
from typing import Any, Dict


class SimpleStore:
    """简单的存一些东西，凑合用用"""

    def __init__(
        self,
        file_name: str = './data/app.pickle',
        auto_flush: bool = True
    ) -> None:
        self.__lock = asyncio.Lock()
        self.__file_name = file_name
        self.__auto_flush = auto_flush

        try:
            self.__store = pickle.load(open(file_name, 'rb'), encoding='utf-8')
        except EOFError:
            self.__store = {}
        except FileNotFoundError:
            self.__store = {}
            if not path.exists("./data"):
                mkdir('./data')
            pickle.dump({}, open(file_name, 'wb'))
        except Exception as e:
            raise e

    async def __aenter__(self):
        await self.__lock.acquire()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.__auto_flush:
            self.flush()

        if self.__lock.locked():
            self.__lock.release()

    def get_lock(self) -> asyncio.Lock:
        return self.__lock

    @property
    def data(self) -> Dict[str, Any]:
        return self.__store

    def get_data(self, key: Any) -> Dict:  # , typed: Any
        if self.__store.get(key):
            return self.__store[key]
        else:
            self.__store[key] = {}
            return self.__store[key]

    # def update(self, data: Dict):
    #     return self.__store.update(data)

    # def clear(self) -> Dict:
    #     self.__store.clear()

    # def getter(self, key: Any) -> Any:
    #     return self.__store.get(key)

    # def setter(self, key: Any, value: Any) -> None:
    #     self.__store[key] = value

    # def deleter(self, key: Any) -> Optional[Any]:
    #     return self.__store.pop(key, None)

    def flush(self):
        """更新数据并持久化到pickle文件"""
        pickle.dump(self.__store, open(self.__file_name, 'wb'))


# storage = SimpleStorage('./data/app.pickle')
