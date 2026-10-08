class SigLIP2EmbeddingProvider:
    def __init__(self,model_id="google/siglip2-base-patch16-224"):
        self.model_id=model_id
    @property
    def model_version(self): return self.model_id
    def embed_image(self,image):
        raise RuntimeError("SigLIP2 adapter requires an explicitly provisioned local ML environment")
