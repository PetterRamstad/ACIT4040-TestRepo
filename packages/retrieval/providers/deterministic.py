import hashlib
class DeterministicEmbeddingProvider:
    model_version="fixture-embedding-v1"
    def __init__(self,dimension=32): self.dimension=dimension
    def embed_image(self,image):
        raw=image if isinstance(image,bytes) else str(image).encode()
        digest=hashlib.sha256(raw).digest()
        return [(digest[i%len(digest)]/255.0) for i in range(self.dimension)]
