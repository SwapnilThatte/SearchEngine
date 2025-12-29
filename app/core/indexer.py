import os
import math
import asyncio
from collections import Counter, defaultdict

from .tokenizer import Tokenizer

class Index:
    def __init__(self):
        self.index = defaultdict(list)
        self.doc_lengths = {}
        self.tokenizer = Tokenizer()
        self.lock = asyncio.Lock()
        self.doc_terms = {}  

    @property
    def num_docs(self) -> int:
        return len(self.doc_lengths)
    
    @property
    def avg_doc_len(self):
        return sum(self.doc_lengths.values()) / self.num_docs

    def index_document(self, filepath: str):
        # doc_name, _ = os.path.splitext(os.path.basename(filepath))
        # print(f"Indexing {doc_name}....")
        # term_count = Counter()

        # with open(filepath, 'r', encoding='utf-8') as f_in:
        #     for line in f_in:
        #         for term in line.strip().split():
        #             term_count[term] += 1

        # for term, count in term_count.most_common():
        #     self.index[term].append((doc_name, count))
        # self.doc_lengths[doc_name] = sum(term_count.values())

        doc_name, _ = os.path.splitext(os.path.basename(filepath))
        
        print(f"Indexing {doc_name}....")
        self._remove_document(doc_name)
        doc_terms = set()

        term_count = Counter()

        with open(filepath, 'r', encoding='utf-8') as f_in:
            print("File Opened....")
            for line in f_in:
                tokens = self.tokenizer.process(line)  # UPDATED
                print(f"Tokenizing....")
                for term in tokens:
                    term_count[term] += 1
                    print("Calculating Term Count....")

        for term, count in term_count.most_common():
            print(f"Creating in memory index")
            self.index[term].append((doc_name, count))

        print("Calculating Document Count")
        self.doc_lengths[doc_name] = sum(term_count.values())
        self.doc_terms[doc_name] = doc_terms

    
    def index_directory(self, directory: str):
        for filename in os.listdir(directory):
            if not filename.endswith(".txt"):
                print(f"Skipping {filename} [Not a text file]")
                continue
            filepath = os.path.join(directory, filename)
            self.index_document(filepath)

    
    def display(self):
        print(f"Displaying contents of index....")
        for term, doc_counts in sorted(self.index.items()):
            print(f"{term}: {doc_counts}")

    def bm25_idf(self, term: str) -> float:
        df = len(self.index.get(term, []))
        return math.log(1 + (self.num_docs - df + 0.5) / (df + 0.5))

    def query_bm25(self, query: str, k1=2.0, b=0.75):
        # doc_scores = defaultdict(float)
        # for term in query.strip().split():
        #     for doc, tf in self.index[term]:
        #         doc_len_norm = (k1 + 1.0) / (tf + k1 * (1 - b + b*(self.doc_lengths[doc] / self.avg_doc_len))) 
        #         doc_scores[doc] += tf * self.bm25_idf(term) * doc_len_norm
        # return doc_scores

        doc_scores = defaultdict(float)

        query_terms = self.tokenizer.process(query)  # UPDATED

        for term in query_terms:
            for doc, tf in self.index.get(term, []):
                doc_len_norm = (k1 + 1.0) / (
                    tf + k1 * (1 - b + b * (self.doc_lengths[doc] / self.avg_doc_len))
                )
                doc_scores[doc] += tf * self.bm25_idf(term) * doc_len_norm

        return doc_scores
    
    # async def snapshot(self):
    #     """Return a safe snapshot of index data."""
    #     async with self.lock:
    #         return {
    #             "index": dict(self.index),
    #             "doc_lengths": dict(self.doc_lengths)
    #         }
    async def snapshot(self):                      #  CHANGE: async
        async with self.lock:                      #  ADD
            return {
                "index": dict(self.index),
                "doc_lengths": dict(self.doc_lengths),
                "doc_terms": {k: list(v) for k, v in self.doc_terms.items()}
            }


    # ➕ ADDED
    def load_snapshot(self, data: dict):
        self.index = defaultdict(list, data["index"])        #  UPDATED
        self.doc_lengths = data["doc_lengths"]               #  UPDATED
        self.doc_terms = {k: set(v) for k, v in data["doc_terms"]}

    def _remove_document(self, doc_name: str):
        if doc_name not in self.doc_terms:
            return

        for term in self.doc_terms[doc_name]:
            self.index[term] = [
                (d, tf) for (d, tf) in self.index[term] if d != doc_name
            ]
            if not self.index[term]:
                del self.index[term]

        del self.doc_terms[doc_name]
        self.doc_lengths.pop(doc_name, None)
