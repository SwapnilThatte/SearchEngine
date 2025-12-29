# 🔍✨ Search Index & Retrieval Engine

A production-inspired full-text search engine built from scratch in Python, implementing core information retrieval concepts such as inverted indexing, BM25 ranking, document sharding, and asynchronous persistence.
Designed to be scalable, fault-aware, and extensible, this project mirrors the internals of real-world systems like Elasticsearch ⚡.

## 📐 Design Philosophy

This project prioritizes:

🔍 Deep understanding of search engine internals

🧱 Clean modular architecture

⚙️ Production-oriented design decisions

🌱 Extensibility toward distributed systems



## 🌟 Key Features

🔎 Full-text search with BM25 relevance scoring

🧠 Inverted Index for efficient term-to-document lookups

🧩 Document-level sharding for scalable indexing & querying

⏱️ Asynchronous background persistence using asyncio

💾 Crash-safe recovery via JSON snapshots

♻️ Idempotent indexing (safe re-indexing without duplicates)

🚀 FastAPI-powered REST API with clean lifecycle management

🧱 Modular architecture designed for future replication & distribution


Efficiently maps terms → documents with term frequencies for fast lookup.

## 💾 Persistence & Recovery

Index state is periodically stored as JSON snapshots

On startup, the system automatically restores the latest snapshot

Ensures durability and crash safety 🛡️


## 🛡️ Consistency Guarantees

❌ Duplicate documents are prevented

♻️ Documents are removed before re-indexing

🧩 Shards remain isolated yet deterministic

🔁 Index state stays consistent across restarts

## 🛠️ Tech Stack

🐍 Python

🚀 FastAPI

⏳ asyncio

🧠 NLTK (tokenization, stemming, stop-word removal)

💾 JSON persistence