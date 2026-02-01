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
            snapshot = await self.index.snapshot()                 

            tmp = self.filepath.with_suffix(".tmp")
            with tmp.open("w", encoding="utf-8") as f:        
                json.dump(snapshot, f)                        

            tmp.replace(self.filepath)
            print(f"[IndexPersistor] Saved @ {time.ctime()}")


def load_index(index, filepath="index.json"):
    path = Path(filepath)
    if not path.exists():
        return False

    with path.open("r", encoding="utf-8") as f:               
        data = json.load(f)                                   

    index.load_snapshot(data)                                 
    return True

