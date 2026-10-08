"""Long-term memory using Pinecone.

Groq does not make embeddings, so we use Pinecone's built-in embedding model.
Flow:  text -> embedding (numbers) -> stored in Pinecone -> searched by meaning.

A 'namespace' is a separate drawer inside the same index:
  ""          -> your personal memories (used by the chat)
  "practice"  -> English practice scores (used by the Daily Practice page)
"""
import time
import uuid
from pinecone import Pinecone, ServerlessSpec
from config import (PINECONE_API_KEY, PINECONE_INDEX,
                    EMBED_MODEL, EMBED_DIMENSION)

pc = Pinecone(api_key=PINECONE_API_KEY)


def _get_index():
    """Create the index the first time, then reuse it."""
    if PINECONE_INDEX not in pc.list_indexes().names():
        pc.create_index(
            name=PINECONE_INDEX,
            dimension=EMBED_DIMENSION,
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region="us-east-1"),
        )
    return pc.Index(PINECONE_INDEX)


index = _get_index()


def _embed(text, input_type):
    result = pc.inference.embed(
        model=EMBED_MODEL,
        inputs=[text],
        parameters={"input_type": input_type, "truncate": "END"},
    )
    return result[0]["values"]


def remember(text, namespace="", extra=None):
    """Save a fact. 'extra' adds more info (like scores) to the record."""
    metadata = {"text": text, "saved_at": int(time.time())}
    metadata.update(extra or {})
    index.upsert(
        vectors=[{
            "id": str(uuid.uuid4()),
            "values": _embed(text, "passage"),
            "metadata": metadata,
        }],
        namespace=namespace,
    )


def recall(query, top_k=3, min_score=0.75, namespace=""):
    """Find saved facts related to the query. Returns a list of strings."""
    try:
        result = index.query(
            vector=_embed(query, "query"),
            top_k=top_k,
            include_metadata=True,
            namespace=namespace,
        )
        return [m["metadata"]["text"] for m in result["matches"]
                if m["score"] >= min_score]
    except Exception:
        return []   # memory should never crash the chat


def list_records(namespace=""):
    """Every saved record (newest first) as dicts: {'id':..., 'text':..., ...}."""
    records = []
    for page in index.list(namespace=namespace):
        ids = [item.id for item in page.vectors]
        if not ids:
            continue
        fetched = index.fetch(ids=ids, namespace=namespace)
        for vec_id, vec in fetched.vectors.items():
            records.append({"id": vec_id, **(vec.metadata or {})})
    return sorted(records, key=lambda r: r.get("saved_at", 0), reverse=True)


def forget(record_id, namespace=""):
    """Delete one record."""
    index.delete(ids=[record_id], namespace=namespace)
