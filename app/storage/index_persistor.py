# index_persistor.py
import asyncio
import time
from pathlib import Path
import json


class IndexPersistor:
    def __init__(
        self,
        index,
        filepath: str = "index.json",
        interval_seconds: int = 10,
    ):
        self.index = index
        self.filepath = Path(filepath)
        self.interval = interval_seconds
        self._task: asyncio.Task | None = None
        self._stop_event = asyncio.Event()
        self._lock = asyncio.Lock()

    async def start(self):
        if self._task is None:
            self._task = asyncio.create_task(self._run())

    async def stop(self):
        self._stop_event.set()
        if self._task:
            await self._task

    async def _run(self):
        while not self._stop_event.is_set():
            await asyncio.sleep(self.interval)
            await self.persist()

    async def persist(self):
        async with self._lock:
            snapshot = await self.index.snapshot()                 # 🔄 UPDATED

            tmp = self.filepath.with_suffix(".tmp")
            with tmp.open("w", encoding="utf-8") as f:        # 🔄 UPDATED
                json.dump(snapshot, f)                        # 🔄 UPDATED

            tmp.replace(self.filepath)
            print(f"[IndexPersistor] Saved @ {time.ctime()}")


def load_index(index, filepath="index.json"):
    path = Path(filepath)
    if not path.exists():
        return False

    with path.open("r", encoding="utf-8") as f:               # 🔄 UPDATED
        data = json.load(f)                                   # 🔄 UPDATED

    index.load_snapshot(data)                                 # 🔄 UPDATED
    return True


# import asyncio
# import pickle
# from pathlib import Path
# from ..core.indexer import Index
# import datetime

# class IndexPersistor:
#     def __init__(
#         self,
#         index: Index,
#         filepath: str = f"index_{datetime.datetime.now().isoformat()}.pkl",
#         interval: int = 30,
#     ):
#         self.index = index
#         self.filepath = Path(filepath)
#         self.interval = interval
#         self._task = None
#         self._stop_event = asyncio.Event()

#     async def _run(self):
#         while not self._stop_event.is_set():
#             await asyncio.sleep(self.interval)

#             snapshot = await self.index.snapshot()

#             with open(self.filepath, "wb") as f:
#                 pickle.dump(snapshot, f)

#             print("📦 Index snapshot saved")

#     async def start(self):
#         if self._task is None:
#             self._task = asyncio.create_task(self._run())

#     async def stop(self):
#         self._stop_event.set()
#         if self._task:
#             await self._task
