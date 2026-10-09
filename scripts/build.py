import numpy as np
import trimesh
from shapely.geometry import Polygon, Point, box
from shapely.ops import triangulate
from pathlib import Path

OUT = Path("models")
OUT.mkdir(exist_ok=True)
scene = trimesh.Scene()
GOLD=[192,126,34,255]; LIGHT=[232,183,77,255]; SHINE=[255,219,125,255]
CREAM=[225,221,205,255]; WHITE=[247,246,239,255]; DARK=[128,79,23,255]

def extrude(poly, z0, z1, color, name):
    if poly.is_empty: return
    if poly.geom_type == "MultiPolygon":
        for i, part in enumerate(poly.geoms):
            extrude(part,z0,z1,color,name+str(i))
        return
    if not poly.is_valid: poly=poly.buffer(0)
    poly=poly.simplify(.25,preserve_topology=True)
    vertices=[]; faces=[]
    def pt(x,y,z):
        vertices.append([x,y,z])
        return len(vertices)-1
    for tri in triangulate(poly):
        if not poly.covers(tri): continue
        coords=list(tri.exterior.coords)[:3]
        top=[pt(x,y,z1) for x,y in coords]
        bottom=[pt(x,y,z0) for x,y in coords]
        faces.extend([top,bottom[::-1]])
    for ring in [poly.exterior,*poly.interiors]:
        for (x,y),(u,v) in zip(list(ring.coords)[:-1],list(ring.coords)[1:]):
            a=pt(x,y,z0); b=pt(u,v,z0); c=pt(u,v,z1); d=pt(x,y,z1)
            faces.extend([[a,b,c],[a,c,d]])
    mesh=trimesh.Trimesh(vertices=np.array(vertices),faces=np.array(faces),process=False)
    mesh.visual.vertex_colors=np.tile(color,(len(vertices),1))
    scene.add_geometry(mesh,geom_name=name)

def polygon(coords): return Polygon(coords).buffer(0)
def rounded(x0,y0,x1,y1,r):
    return box(x0+r,y0+r,x1-r,y1-r).union(box(x0,y0+r,x1,y1-r)).union(
        Point(x0+r,y0+r).buffer(r,resolution=10)).union(
        Point(x1-r,y0+r).buffer(r,resolution=10)).union(
        Point(x0+r,y1-r).buffer(r,resolution=10)).union(
        Point(x1-r,y1-r).buffer(r,resolution=10))

outer=polygon([(-416,-324),(-416,280),(-398,322),(-375,345),(-336,348),
(-336,390),(-318,405),(-167,405),(-68,393),(0,362),(68,393),
(167,405),(318,405),(336,390),(336,348),(375,345),(398,322),
(416,280),(416,-324),(397,-357),(356,-366),(75,-366),(40,-392),
(0,-404),(-40,-392),(-75,-366),(-356,-366),(-397,-357)])
outer=outer.buffer(16,join_style=1).buffer(-16,join_style=1)
extrude(outer,-16,-2,DARK,"outer shadow")
extrude(outer,-2,5,GOLD,"gold backing")
extrude(outer.buffer(-13),5,9,LIGHT,"gold border")
extrude(outer.buffer(-33),9,11,SHINE,"gold bevel")
extrude(outer.buffer(-42),11,13,GOLD,"recess trim")
extrude(outer.buffer(-55),13,16,CREAM,"ivory field")

panel=polygon([(-300,-307),(-300,327),(-185,327),(-99,312),
(-40,283),(0,250),(40,283),(99,312),(185,327),(300,327),
(300,-307),(185,-307),(94,-321),(35,-346),(0,-362),
(-35,-346),(-94,-321),(-185,-307)])
panel=panel.buffer(13,join_style=1).buffer(-13,join_style=1)
extrude(panel,16,21,GOLD,"book edge")
extrude(panel.buffer(-15),21,24,SHINE,"book ridge")
extrude(panel.buffer(-35),24,25,GOLD,"book inner trim")
extrude(panel.buffer(-43),25,26,WHITE,"book page")

left=polygon([(-225,230),(-140,230),(-140,202),(-195,202),
(-195,-205),(-61,-205),(-61,-241),(-225,-241)])
right=polygon([(225,230),(140,230),(140,202),(195,202),
(195,-205),(61,-205),(61,-241),(225,-241)])
for i, part in enumerate((left,right)):
    extrude(part,26,36,DARK,f"bracket shadow {i}")
    extrude(part,36,47,GOLD,f"bracket gold {i}")
    extrude(part.buffer(-3),47,50,SHINE,f"bracket shine {i}")
pill=rounded(-95,93,95,184,24)
extrude(pill,26,36,DARK,"pill shadow")
extrude(pill,36,48,LIGHT,"pill gold")
extrude(pill.buffer(-4),48,52,SHINE,"pill shine")
for i,y in enumerate((39,-42,-123)):
    bar=box(-130,y-18,130,y+18)
    extrude(bar,26,34,DARK,f"line shadow {i}")
    extrude(bar,34,45,GOLD,f"line gold {i}")
    extrude(bar.buffer(-3),45,48,SHINE,f"line shine {i}")
scene.export(OUT/"otzaria_logo_3d.glb")
trimesh.util.concatenate(scene.dump()).export(OUT/"otzaria_logo_3d.stl")
print("Exported 3D logo")
