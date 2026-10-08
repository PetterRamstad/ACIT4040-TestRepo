from .models import Room,Layout
def validate(room,layout):
    violations=[]
    for p in layout.placements:
        if p.x-p.width/2<0 or p.x+p.width/2>room.width or p.y-p.depth/2<0 or p.y+p.depth/2>room.depth: violations.append("boundary")
    for i,a in enumerate(layout.placements):
        for b in layout.placements[i+1:]:
            if abs(a.x-b.x)<(a.width+b.width)/2 and abs(a.y-b.y)<(a.depth+b.depth)/2: violations.append("collision")
    return {"valid":not violations,"violations":violations}
class LayoutValidator:
    def validate(self,room,layout): return validate(room,layout)
