#!/usr/bin/env python3
"""Schematic 3D and plan preview from CadQuery source. (not photo render)"""
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import patches
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import trimesh
import cadquery as cq
from generate_enclosure import HERE, P, make_upper, make_lid, reference_pcb, bolt_xy, pcb_xy

shapes={'shell':make_upper(),'lid':make_lid(),'pcb':reference_pcb()}
meshes={}
for key,sh in shapes.items():
    tmp=HERE/f'_render_{key}.stl'
    cq.exporters.export(sh,str(tmp),tolerance=.18,angularTolerance=.28)
    meshes[key]=trimesh.load(tmp,force='mesh')
    tmp.unlink()


def add_obj(ax, mesh, rgb, offset=(0,0,0), opacity=1):
    light=np.array([.40,.37,.83]); light/=np.linalg.norm(light)
    normals=mesh.face_normals
    strength=np.clip(.67 + .35*(normals@light),.36,1)
    base=np.array(rgb)
    colors=np.clip(base[None,:]*strength[:,None],0,1)
    poly=Poly3DCollection(mesh.triangles+np.array(offset),facecolors=colors,
                          linewidths=0.0,edgecolors='none',zsort='average',alpha=opacity)
    ax.add_collection3d(poly)


def three_d(filename,explode=False):
    fig=plt.figure(figsize=(9,7),dpi=170,facecolor='#f7fafc')
    ax=fig.add_subplot(111,projection='3d',computed_zorder=True)
    ax.set_facecolor('#f7fafc')
    add_obj(ax,meshes['shell'],(.24,.44,.59))
    add_obj(ax,meshes['lid'],(.86,.63,.32),offset=(0,0,-14 if explode else 0))
    if explode:
        add_obj(ax,meshes['pcb'],(.18,.56,.32),offset=(0,0,-5))
    ax.set_xlim(-47,47);ax.set_ylim(-43,43);ax.set_zlim(-22 if explode else -8,41)
    ax.set_box_aspect((1,.92,.64));ax.set_proj_type('ortho')
    ax.view_init(elev=25,azim=48)
    ax.set_axis_off()
    fig.tight_layout(pad=0)
    fig.savefig(HERE/filename,bbox_inches='tight',pad_inches=0.08,facecolor=fig.get_facecolor())
    plt.close(fig)


def underside(filename):
    fig=plt.figure(figsize=(9,7),dpi=170,facecolor='#f7fafc')
    ax=fig.add_subplot(111,projection='3d',computed_zorder=True)
    shell=meshes['shell'].copy()
    # Rotate upside down to show inner 4 bosses, support pads and thin perimeter wall
    import trimesh.transformations as tf
    shell.apply_transform(tf.rotation_matrix(np.pi,[1,0,0]))
    shell.apply_translation([0,0,P.height])
    add_obj(ax,shell,(.24,.44,.59))
    ax.set_xlim(-46,46);ax.set_ylim(-39,39);ax.set_zlim(-3,39)
    ax.set_box_aspect((1,.90,.66));ax.set_proj_type('ortho')
    ax.view_init(elev=45,azim=-55)
    ax.set_axis_off();fig.tight_layout(pad=0)
    fig.savefig(HERE/filename,bbox_inches='tight',pad_inches=0.08,facecolor=fig.get_facecolor())
    plt.close(fig)


def plan(filename):
    fig,ax=plt.subplots(figsize=(9.6,7.8),dpi=190,facecolor='white')
    ax.set_aspect('equal')
    from matplotlib.patches import FancyBboxPatch, Rectangle, Circle
    xw=P.outside_x;yw=P.outside_y
    outer=FancyBboxPatch((-xw/2,-yw/2),xw,yw,boxstyle='round,pad=0,rounding_size=4.2',facecolor='#d9e6ec',edgecolor='#23495b',lw=2.2)
    inner=FancyBboxPatch((-xw/2+P.side_wall,-yw/2+P.connector_wall),xw-2*P.side_wall,yw-2*P.connector_wall,boxstyle='round,pad=0,rounding_size=2.2',facecolor='white',edgecolor='#58788b',lw=1.4)
    ax.add_patch(outer);ax.add_patch(inner)
    ax.add_patch(Rectangle((-25,-25),50,50,facecolor='#b2d1c0',edgecolor='#29724d',alpha=.45,lw=1.6))
    for x,y in bolt_xy():
        ax.add_patch(Circle((x,y),P.screw_boss_r,color='#6389a0',alpha=.62))
        ax.add_patch(Circle((x,y),P.insert_pilot_d/2,facecolor='white',edgecolor='#24425c',lw=1.4))
    for x,y in pcb_xy():
        ax.add_patch(Circle((x,y),P.clamp_pad_r,facecolor='#65a885',edgecolor='#296444',alpha=.9))
        ax.add_patch(Circle((x,y),P.locator_d/2,facecolor='white',edgecolor='#296444',lw=.8))
    ax.plot([P.front_window_x0,P.front_window_x1],[P.outside_y/2]*2,color='#d87838',lw=7,solid_capstyle='butt')
    ax.plot([-P.usbc_window_width/2,P.usbc_window_width/2],[-P.outside_y/2]*2,color='#d87838',lw=7,solid_capstyle='butt')
    ax.text(-5,P.outside_y/2+2.7,'RJ45 + USB-A',ha='center',fontsize=12,color='#8f4a22')
    ax.text(0,-P.outside_y/2-4.4,'USB-C',ha='center',fontsize=12,color='#8f4a22')
    ax.text(0,0,'PCB 50 × 50',ha='center',fontsize=13,color='#245b40',weight='bold')
    ax.annotate('',xy=(-37,-36),xytext=(37,-36),arrowprops={'arrowstyle':'<->','color':'#344e62','lw':1.4})
    ax.text(0,-37.9,'74 mm',va='top',ha='center',fontsize=12)
    ax.annotate('',xy=(42,-31),xytext=(42,31),arrowprops={'arrowstyle':'<->','color':'#344e62','lw':1.4})
    ax.text(44,0,'62 mm',rotation=90,ha='center',va='center',fontsize=12)
    ax.set_xlim(-47,52);ax.set_ylim(-45,42);ax.axis('off');fig.tight_layout()
    fig.savefig(HERE/filename,bbox_inches='tight',pad_inches=.1);plt.close(fig)

if __name__=='__main__':
    three_d('ESP32_P4_NANO_RevB_assembled.png')
    three_d('ESP32_P4_NANO_RevB_exploded.png',True)
    underside('ESP32_P4_NANO_RevB_inside_view.png')
    plan('ESP32_P4_NANO_RevB_plan.png')
