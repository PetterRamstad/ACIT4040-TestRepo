from packages.layout.generator import LayoutEngine
from packages.layout.models import Room
from packages.retrieval.providers.fixture import FixtureFurnitureProvider

def test_generator_produces_valid_layout():
 layout=LayoutEngine().generate(Room(8,8),FixtureFurnitureProvider().list_items()); assert layout.placements
