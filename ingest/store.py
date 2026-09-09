"""Second-brain data layer seam.

If CHROMA_PATH is set, every ingested article is upserted into a persistent
Chroma collection keyed by Article.doc_id, with metadata for later filtering
(source, date, matched interests). If it isn't set — the default in CI today —
this is a no-op and `chromadb` need not be installed.

The same collection convention will hold hand-written learning notes once the
second brain is built, so news and notes are queried through one interface.
"""
from __future__ import annotations

from .article import Article
from .config import CHROMA_COLLECTION, CHROMA_PATH


def enabled() -> bool:
    return bool(CHROMA_PATH)


def _collection():
    import chromadb  # lazy: only needed when CHROMA_PATH is set

    client = chromadb.PersistentClient(path=CHROMA_PATH)
    return client.get_or_create_collection(
        name=CHROMA_COLLECTION, metadata={"hnsw:space": "cosine"}
    )


def _embedding_text(a: Article) -> str:
    from .article import clean_text
    return f"{a.title}\n\n{a.preview or clean_text(a.body)}".strip()


def upsert_articles(articles: list[Article]) -> None:
    if not enabled():
        print("  store: CHROMA_PATH unset — skipping vector upsert")
        return
    if not articles:
        return
    try:
        col = _collection()
        col.upsert(
            ids=[a.doc_id for a in articles],
            documents=[_embedding_text(a) for a in articles],
            metadatas=[
                {
                    "kind": "news",
                    "title": a.title,
                    "url": a.url,
                    "source": a.source,
                    "date": a.date_str,
                }
                for a in articles
            ],
        )
        print(f"  store: upserted {len(articles)} articles into '{CHROMA_COLLECTION}'")
    except Exception as e:
        print(f"  store: upsert failed (non-fatal): {e}")
