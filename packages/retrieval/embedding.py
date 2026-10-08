from typing import Protocol


class EmbeddingProvider(Protocol):
    @property
    def model_version(self)->str: ...
    def embed_image(self,image:bytes|str)->list[float]: ...
