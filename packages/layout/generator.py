from .models import Layout,Placement,Room
from .constraints import validate

class LayoutEngine:
    def generate(self,room,furniture):
        placements=[]
        cursor_x=0.6
        cursor_y=0.6
        row_depth=0.0
        for item in furniture:
            w,d=item.dimensions[:2]
            if cursor_x+w/2>room.width:
                cursor_x=0.6
                cursor_y+=row_depth+0.6
                row_depth=0.0
            if cursor_y+d/2>room.depth:
                break
            placements.append(Placement(item.id,cursor_x+w/2,cursor_y+d/2,w,d))
            cursor_x+=w+0.6
            row_depth=max(row_depth,d)
        layout=Layout(placements)
        return layout if validate(room,layout)["valid"] else Layout([])
