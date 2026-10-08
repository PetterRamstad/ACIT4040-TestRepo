from packages.retrieval.providers.deterministic import DeterministicEmbeddingProvider


def test_stable_embedding():
 p=DeterministicEmbeddingProvider(); assert p.embed_image(b"x")==p.embed_image(b"x"); assert len(p.embed_image(b"x"))==32
