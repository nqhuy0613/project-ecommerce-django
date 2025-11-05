from django.core.management.base import BaseCommand
from store.models import Product
import os, pickle
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

INDEX_DIR = "var/assistant_index"
os.makedirs(INDEX_DIR, exist_ok=True)

class Command(BaseCommand):
    help = "Build vector index for Product search"

    def handle(self, *args, **opts):
        model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
        items, texts = [], []
        for p in Product.objects.all():
            txt = f"{p.title} | {p.description or ''} | Category: {getattr(p.category,'name', '')}"
            items.append({"id": p.id, "title": p.title})
            texts.append(txt.strip())

        if not texts:
            self.stdout.write(self.style.WARNING("No products found."))
            return

        embs = model.encode(texts, convert_to_numpy=True, show_progress_bar=True)
        dim = embs.shape[1]
        index = faiss.IndexFlatIP(dim)
        faiss.normalize_L2(embs)
        index.add(embs)

        faiss.write_index(index, os.path.join(INDEX_DIR, "products.faiss"))
        with open(os.path.join(INDEX_DIR, "meta.pkl"), "wb") as f:
            pickle.dump(items, f)

        self.stdout.write(self.style.SUCCESS(f"Indexed {len(items)} products"))
