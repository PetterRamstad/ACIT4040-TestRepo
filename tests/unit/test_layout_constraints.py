from packages.layout.models import Room,Layout,Placement
from packages.layout.constraints import validate
def test_boundary_violation(): assert "boundary" in validate(Room(2,2),Layout([Placement("x",2,1,1,1)]))["violations"]
def test_collision(): assert "collision" in validate(Room(3,3),Layout([Placement("a",1,1,1,1),Placement("b",1.2,1,1,1)]))["violations"]
