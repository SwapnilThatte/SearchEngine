# main.py
from typing import Dict
from contextlib import asynccontextmanager

from core.indexer import Index
from storage.index_persistor import IndexPersistor, load_index
from schema.models import FilePathRequest, DirPathRequest, SearchRequest

from fastapi import FastAPI, Depends
from fastapi.concurrency import run_in_threadpool
import uvicorn

# -------------------------
# Global application state
# -------------------------
index = Index()
persistor = IndexPersistor(
    index=index,
    filepath="index.json",
    interval_seconds=10,
)


# -------------------------
# Lifespan management
# -------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    # ---- Startup ----
    load_index(index)
    await persistor.start()

    yield  # Application runs here

    # ---- Shutdown ----
    await persistor.stop()


app = FastAPI(lifespan=lifespan)


# -------------------------
# Dependencies
# -------------------------
def get_index() -> Index:
    return index


# -------------------------
# API Routes
# -------------------------
@app.post("/search")
def search(
    request: SearchRequest,
    index: Index = Depends(get_index),
) -> Dict[str, float]:
    """
    BM25 search endpoint
    """
    return index.query_bm25(request.query)


@app.post("/index")
async def index_document(
    request_body: FilePathRequest,
    index: Index = Depends(get_index),
):
    """
    Index a single document by filesystem path
    """
    # index.index_document(filepath)
    try:
        await run_in_threadpool(index.index_document, request_body.filepath)
        return {"status": "indexed", "file": request_body.filepath}
    except Exception as e:
        return {"status" : "[500] Internal Server Error", "msg" : e}

@app.post("/index-directory")
def index_directory(
    request: DirPathRequest,
    index: Index = Depends(get_index),
):
    """
    Index all .txt documents in a directory
    """
    index.index_directory(request.dirpath)
    return {"status": "indexed", "directory": request.dirpath}


@app.get("/stats")
def stats(index: Index = Depends(get_index)):
    """
    Basic index statistics
    """
    return {
        "documents": index.num_docs,
        "average_doc_length": index.avg_doc_len if index.num_docs else 0,
        "terms": len(index.index),
    }


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)

# import httpx
# import asyncio
# import hashlib

# class ClusterCoordinator:
#     def __init__(self, nodes: list):
#         self.nodes = nodes # e.g., ["http://node1:8001", "http://node2:8001"]
#         self.num_shards = 4

#     def _get_nodes_for_shard(self, shard_id: int):
#         """
#         Industry Standard: Determine which nodes hold the Primary and Replicas.
#         Shard 0 -> Primary: Node 1, Replica: Node 2
#         """
#         primary_node = self.nodes[shard_id % len(self.nodes)]
#         replica_node = self.nodes[(shard_id + 1) % len(self.nodes)]
#         return primary_node, replica_node

#     async def index_document(self, doc_id: str, user_id: str, text: str):
#         tokens = tokenizer.process(text)
#         shard_id = int(hashlib.md5(doc_id.encode()).hexdigest(), 16) % self.num_shards
#         primary, replica = self._get_nodes_for_shard(shard_id)

#         # Write to both Primary and Replica for Fault Tolerance
#         async with httpx.AsyncClient() as client:
#             tasks = [
#                 client.post(f"{primary}/shards/{shard_id}/index", json={...}),
#                 client.post(f"{replica}/shards/{shard_id}/index", json={...})
#             ]
#             await asyncio.gather(*tasks)

#     async def search(self, query: str, user_id: str):
#         tokens = tokenizer.process(query)
#         global_stats = await self._aggregate_global_stats()
        
#         results = {}
#         async with httpx.AsyncClient() as client:
#             for shard_id in range(self.num_shards):
#                 primary, replica = self._get_nodes_for_shard(shard_id)
                
#                 # Fault Tolerance: Try Primary, Failover to Replica
#                 try:
#                     resp = await client.post(f"{primary}/shards/{shard_id}/search", ...)
#                     shard_scores = resp.json()['scores']
#                 except httpx.RequestError:
#                     print(f"Node {primary} failed! Falling back to {replica}")
#                     resp = await client.post(f"{replica}/shards/{shard_id}/search", ...)
#                     shard_scores = resp.json()['scores']
                
#                 results.update(shard_scores)
#         return results