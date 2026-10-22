#!/usr/bin/env python3
"""ESP32-P4-NANO Rev.A two-piece enclosure (CadQuery 2.8.0). All dimensions mm.
Reference: https://www.waveshare.com/img/devkit/ESP32-P4-NANO/ESP32-P4-NANO-details-size.jpg
PORT CUTOUTS, PCB THICKNESS, and MOUNTING HOLE INSIDE DIAMETER MUST BE TEST FIT.
"""
from dataclasses import dataclass
from pathlib import Path
import cadquery as cq

@dataclass(frozen=True)
class Parameters:
    pcb_width: float=50.0
    pcb_thickness: float=1.60
    pcb_hole_pitch: float=45.10
    alignment_pin_d: float=1.65
    body_width: float=58.8
    body_corner_r: float=3.8
    wall: float=2.6
    outer_height: float=27.6
    bottom_lid_thickness: float=3.2
    roof_thickness: float=2.6
    post_xy: float=30.5
    post_r: float=4.8
    post_top_z: float=16.5
    heat_insert_pilot_d: float=4.05
    heat_insert_pilot_depth: float=9.4
    m3_clearance_d: float=3.35
    head_recess_d: float=6.3
    head_recess_depth: float=1.9
    lid_registration_height: float=1.45
    lid_registration_wall: float=1.0
    tongue_wall_clearance: float=0.52
    pcb_bottom_z: float=5.62
    pcb_top_support_z: float=7.30
    board_pad_r: float=2.35
    lid_locator_height: float=2.0
    rj45_usba_window_xmin: float=-20.15
    rj45_usba_window_xmax: float=10.35
    rj45_usba_window_top_z: float=24.0
    usbc_window_width: float=15.2
    usbc_window_top_z: float=14.6

P=Parameters()
OUT=Path(__file__).resolve().parent

def round_square(side,height,z,radius):
    return (cq.Workplane("XY").box(side,side,height,centered=(True,True,False))
            .translate((0,0,z)).edges("|Z").fillet(radius))
def corner_positions():
    return [(x*P.post_xy,y*P.post_xy) for x in (-1,1) for y in (-1,1)]
def hole_positions():
    v=P.pcb_hole_pitch/2
    return [(x*v,y*v) for x in (-1,1) for y in (-1,1)]

def make_upper_shell():
    bottom=P.bottom_lid_thickness
    cavity_width=P.body_width-2*P.wall
    roof_bottom=P.outer_height-P.roof_thickness
    shell=round_square(P.body_width,P.outer_height-bottom,bottom,P.body_corner_r)
    for x,y in corner_positions():
        ear=(cq.Workplane("XY").workplane(offset=bottom).center(x,y)
             .circle(P.post_r).extrude(P.post_top_z-bottom))
        shell=shell.union(ear)
    cavity=round_square(cavity_width,roof_bottom-bottom+0.25,
                        bottom-0.20,max(0.75,P.body_corner_r-P.wall))
    shell=shell.cut(cavity)
    for x,y in hole_positions():
        leg=(cq.Workplane("XY").workplane(offset=P.pcb_top_support_z)
             .center(x,y).circle(P.board_pad_r)
             .extrude(roof_bottom-P.pcb_top_support_z+0.05))
        shell=shell.union(leg)
        relief=(cq.Workplane("XY").workplane(offset=P.pcb_top_support_z-0.03)
                .center(x,y).circle((P.alignment_pin_d+0.65)/2)
                .extrude(P.lid_locator_height+0.9))
        shell=shell.cut(relief)
    a,b=P.rj45_usba_window_xmin,P.rj45_usba_window_xmax
    front=(cq.Workplane("XY")
           .box(b-a,12,P.rj45_usba_window_top_z-bottom+0.3,
                centered=(True,True,False))
           .translate(((a+b)/2,P.body_width/2+1.0,bottom-0.2)))
    shell=shell.cut(front)
    rear=(cq.Workplane("XY")
          .box(P.usbc_window_width,12,P.usbc_window_top_z-bottom+0.3,
               centered=(True,True,False))
          .translate((0,-(P.body_width/2+1.0),bottom-0.2)))
    shell=shell.cut(rear)
    for x,y in corner_positions():
        pilot=(cq.Workplane("XY").workplane(offset=bottom-0.15)
               .center(x,y).circle(P.heat_insert_pilot_d/2)
               .extrude(P.heat_insert_pilot_depth+0.15))
        shell=shell.cut(pilot)
    return shell.clean()

def make_bottom_lid():
    lid_z=P.bottom_lid_thickness
    lid=round_square(P.body_width,lid_z,0,P.body_corner_r)
    for x,y in corner_positions():
        lid=lid.union(cq.Workplane("XY").center(x,y).circle(P.post_r).extrude(lid_z))
    cavity_width=P.body_width-2*P.wall
    rib_outer=cavity_width-2*P.tongue_wall_clearance
    rib_inner=rib_outer-2*P.lid_registration_wall
    rib=round_square(rib_outer,P.lid_registration_height,lid_z,2.0)
    hollow=round_square(rib_inner,P.lid_registration_height+0.3,lid_z-0.15,1.1)
    lid=lid.union(rib.cut(hollow))
    for x,y in hole_positions():
        pad=(cq.Workplane("XY").workplane(offset=lid_z).center(x,y)
             .circle(P.board_pad_r).extrude(P.pcb_bottom_z-lid_z))
        pin=(cq.Workplane("XY").workplane(offset=P.pcb_bottom_z-0.02)
             .center(x,y).circle(P.alignment_pin_d/2).extrude(P.lid_locator_height+0.02))
        lid=lid.union(pad).union(pin)
    for x,y in corner_positions():
        through=(cq.Workplane("XY").workplane(offset=-0.12).center(x,y)
                 .circle(P.m3_clearance_d/2).extrude(lid_z+0.24))
        recess=(cq.Workplane("XY").workplane(offset=-0.12).center(x,y)
                .circle(P.head_recess_d/2).extrude(P.head_recess_depth+0.12))
        lid=lid.cut(through).cut(recess)
    return lid.clean()

def export():
    shell,lid=make_upper_shell(),make_bottom_lid()
    assembly=cq.Assembly(name="ESP32-P4-NANO-Enclosure-RevA")
    assembly.add(shell,name="upper_shell",color=cq.Color(0.16,0.20,0.25))
    assembly.add(lid,name="bottom_lid",color=cq.Color(0.65,0.71,0.75))
    assembly.save(str(OUT/"ESP32_P4_NANO_Enclosure_RevA_assembly.step"))
    cq.exporters.export(shell,str(OUT/"ESP32_P4_NANO_Upper.step"))
    cq.exporters.export(lid,str(OUT/"ESP32_P4_NANO_Bottom.step"))
    shell_print=shell.rotate((0,0,0),(1,0,0),180).translate((0,0,P.outer_height))
    cq.exporters.export(shell_print,str(OUT/"ESP32_P4_NANO_Upper_print.stl"),
                        tolerance=0.08,angularTolerance=0.18)
    cq.exporters.export(lid,str(OUT/"ESP32_P4_NANO_Bottom_print.stl"),
                        tolerance=0.08,angularTolerance=0.18)
    pcb=(cq.Workplane("XY")
         .box(P.pcb_width,P.pcb_width,P.pcb_thickness,centered=(True,True,False))
         .translate((0,0,P.pcb_bottom_z)))
    for x,y in hole_positions():
        pcb=pcb.cut(cq.Workplane("XY").workplane(offset=P.pcb_bottom_z-0.1)
                    .center(x,y).circle(1.2).extrude(P.pcb_thickness+0.2))
    cq.exporters.export(pcb,str(OUT/"ESP32_P4_NANO_PCB_envelope_approx.step"))
    collision=shell.val().intersect(lid.val()).Volume()
    pcb_collision=(pcb.val().intersect(lid.val()).Volume()+
                   pcb.val().intersect(shell.val()).Volume())
    if collision>0.025 or pcb_collision>0.10:
        raise RuntimeError(f"Collision: shell/lid={collision:.4f} PCB={pcb_collision:.4f}")
    print(f"Upper {shell.val().Volume():.1f} mm3; bottom {lid.val().Volume():.1f} mm3")
    print(f"Collisions: shell/lid={collision:.5f}, PCB proxy={pcb_collision:.5f} mm3")
if __name__=="__main__":
    export()
