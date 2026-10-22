"""Render CAD preview (optional): matplotlib, trimesh, CadQuery 2.8.0."""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import trimesh
import cadquery as cq
from generate_enclosure import OUT,make_upper_shell,make_bottom_lid

for name,shape in [('upper_temp.stl',make_upper_shell()),('bottom_temp.stl',make_bottom_lid())]:
    cq.exporters.export(shape,str(OUT/name),tolerance=0.18,angularTolerance=0.25)
shell=trimesh.load(OUT/'upper_temp.stl',force='mesh')
lid=trimesh.load(OUT/'bottom_temp.stl',force='mesh')
def obj(ax,mesh,rgb,offset=(0,0,0)):
    triangles=mesh.triangles+np.array(offset)
    light=np.array([.30,.55,.78]);light/=np.linalg.norm(light)
    intensity=np.maximum(.35,.70+.32*(mesh.face_normals@light))
    color=np.clip(np.array(rgb)[None,:]*intensity[:,None],0,1)
    ax.add_collection3d(Poly3DCollection(triangles,facecolors=color,edgecolors='none',zsort='average'))
def render(name,exploded):
    fig=plt.figure(figsize=(9.4,7.1),dpi=190,facecolor='#f8fafb')
    ax=fig.add_subplot(111,projection='3d',computed_zorder=True)
    ax.set_facecolor('#f8fafb')
    obj(ax,shell,(0.32,0.52,0.68))
    obj(ax,lid,(0.94,0.68,0.33),offset=(0,0,-11 if exploded else 0))
    ax.set_xlim(-48,48);ax.set_ylim(-48,48)
    ax.set_zlim(-18 if exploded else -13,41)
    ax.set_box_aspect((1,1,.67));ax.view_init(elev=32,azim=42)
    ax.set_proj_type('ortho');ax.set_axis_off()
    fig.tight_layout(pad=0)
    fig.savefig(OUT/name,bbox_inches='tight',pad_inches=0.05,facecolor=fig.get_facecolor())
    plt.close(fig)
render('ESP32_P4_NANO_RevA_assembled.png',False)
render('ESP32_P4_NANO_RevA_exploded.png',True)
for name in ['upper_temp.stl','bottom_temp.stl']:
    (OUT/name).unlink()
