from __future__ import annotations

import json
from pathlib import Path

from sentence_transformers import SentenceTransformer


MODEL_NAME = "all-MiniLM-L6-v2"

PROJECT_ROOT = Path(__file__).resolve().parents[2]

PRODUCT_EMBEDDINGS_FILE = (
    PROJECT_ROOT / "data" / "product_embeddings.json"
)


class EmbeddingService:
    def __init__(self) -> None:
        self.model = SentenceTransformer(MODEL_NAME)

        # Cache embeddings generated from arbitrary text.
        self.cache: dict[str, list[float]] = {}

        # Persisted product embeddings.
        self.product_embeddings: dict[
            int | str,
            list[float],
        ] = {}

        self._load_product_embeddings()

    # ========================================================
    # PERSISTED PRODUCT EMBEDDINGS
    # ========================================================

    def _load_product_embeddings(self) -> None:
        """
        Load pre-generated product embeddings from disk.

        Product embeddings are generated offline by:

            scripts/generate_product_embeddings.py

        and stored in:

            data/product_embeddings.json
        """

        if not PRODUCT_EMBEDDINGS_FILE.exists():
            return

        try:
            with PRODUCT_EMBEDDINGS_FILE.open(
                "r",
                encoding="utf-8",
            ) as file:
                embeddings = json.load(file)

            self.product_embeddings = {
                item["product_id"]: item["embedding"]
                for item in embeddings
                if (
                    "product_id" in item
                    and "embedding" in item
                )
            }

        except (
            OSError,
            json.JSONDecodeError,
            TypeError,
            KeyError,
        ):
            # Do not prevent the application from starting if
            # the persisted embedding file is unavailable or
            # malformed.
            self.product_embeddings = {}

    def get_product_embedding(
        self,
        product_id: int | str,
    ) -> list[float] | None:
        """
        Return a persisted embedding for a product.

        Returns None if the product does not have a
        persisted embedding.
        """

        return self.product_embeddings.get(
            product_id
        )

    def reload_product_embeddings(self) -> None:
        """
        Reload persisted product embeddings from disk.

        Useful after running the embedding generation script.
        """

        self.product_embeddings.clear()

        self._load_product_embeddings()

    # ========================================================
    # TEXT EMBEDDINGS
    # ========================================================

    def embed_text(
        self,
        text: str,
    ) -> list[float]:
        """
        Generate a normalized semantic embedding.

        Embeddings are cached by text so repeated requests
        do not recompute the same embedding.
        """

        if not text:
            return []

        cached_embedding = self.cache.get(text)

        if cached_embedding is not None:
            return cached_embedding

        embedding = self.model.encode(
            text,
            normalize_embeddings=True,
        )

        result = embedding.tolist()

        self.cache[text] = result

        return result

    # ========================================================
    # CACHE MANAGEMENT
    # ========================================================

    def clear_cache(self) -> None:
        """
        Clear all text-based cached embeddings.
        """

        self.cache.clear()


embedding_service = EmbeddingService()