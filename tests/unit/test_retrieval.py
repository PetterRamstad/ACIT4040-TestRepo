from packages.retrieval.retriever import FurnitureRetriever

def test_metadata_filtering():
 out=FurnitureRetriever().retrieve(filters={'category':'chair'}); assert [x['item'].id for x in out]==['chair-001']
