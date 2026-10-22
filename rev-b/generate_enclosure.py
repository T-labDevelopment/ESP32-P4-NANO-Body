#!/usr/bin/env python3
"""ESP32-P4-NANO low-profile 4-bolt rectangular enclosure, Rev.B.

Parametric source (CadQuery 2.8.0, mm). The mechanical interface is intentionally
based on the manufacturer's 50 x 50 mm outline and mounting-hole pitch; exact
connector elevations, connector protrusions, PCB thickness, hole ID, and cable-
boot / latch clearances require physical verification.

The two-piece body is hollow; corner screw bosses are locally reinforced only.
No externally projecting screw ears. Upper roof points down on print bed.
"""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import cadquery as cq


@dataclass(frozen=True)
class Params:
    pcb_size: float = 50.0
    pcb_thickness: float = 1.60
    pcb_hole_pitch: float = 45.10
    locator_d: float = 1.65
    # Long axis runs through the port faces (RJ45/A at +Y, Type-C at -Y)
    outside_x: float = 74.0
    outside_y: float = 62.0
    outside_corner_r: float = 4.2
    side_wall: float = 2.0
    connector_wall: float = 1.8       # front/rear walls remain thin
    height: float = 31.5
    lid_thickness: float = 3.2
    top_thickness: float = 2.8
    # Screw bosses stay entirely WITHIN the rectangle, attached to side walls
    screw_x: float = 31.35
    screw_y: float = 24.50
    screw_boss_r: float = 5.30
    boss_top_z: float = 19.2
    insert_pilot_d: float = 4.05
    insert_pilot_depth: float = 9.0
    m3_through_d: float = 3.35
    screw_head_recess_d: float = 6.35
    screw_head_recess_depth: float = 1.9
    # PCB clamped between paired pads; 20µm nominal clearance at 1.6mm PCB
    pcb_under_z: float = 5.62
    pcb_top_pad_z: float = 7.24
    clamp_pad_r: float = 2.40
    pin_height: float = 2.00
    # Two registration tongues on the closed left/right side faces only
    tab_length: float = 16.0
    tab_thickness: float = 1.15
    tab_height: float = 1.4
    tab_side_clearance: float = 0.45
    # Openings sized generously so connector housings can pass through
    front_window_x0: float = -21.4
    front_window_x1: float = 13.4
    front_window_top: float = 24.3
    usbc_window_width: float = 18.0
    usbc_window_top: float = 16.6

P = Params()
HERE = Path(__file__).resolve().parent


def rounded_rectangle(w: float, d: float, height: float, z: float, r: float) -> cq.Workplane:
    """Rounded outline with no external protrusions."""
    return (cq.Workplane('XY')
            .box(w, d, height, centered=(True, True, False))
            .translate((0, 0, z)).edges('|Z').fillet(r))


def bolt_xy():
    return [(sx*P.screw_x, sy*P.screw_y) for sx in (-1,1) for sy in (-1,1)]


def pcb_xy():
    pitch2 = P.pcb_hole_pitch/2
    return [(sx*pitch2,sy*pitch2) for sx in (-1,1) for sy in (-1,1)]


def make_upper() -> cq.Workplane:
    lid_top = P.lid_thickness
    roof_z = P.height-P.top_thickness
    cavity_w = P.outside_x-2*P.side_wall
    cavity_d = P.outside_y-2*P.connector_wall
    inner_radius = max(1.,P.outside_corner_r - max(P.side_wall,P.connector_wall))
    shell = rounded_rectangle(P.outside_x,P.outside_y,P.height-lid_top,
                              lid_top,P.outside_corner_r)
    cavity = rounded_rectangle(cavity_w,cavity_d,roof_z-lid_top+0.3,
                               lid_top-0.2,inner_radius)
    shell = shell.cut(cavity)
    # Localized reinforced corner screw bosses; stay INSIDE the outer rectangle
    for x,y in bolt_xy():
        boss=(cq.Workplane('XY').workplane(offset=lid_top)
              .center(x,y).circle(P.screw_boss_r)
              .extrude(P.boss_top_z-lid_top))
        shell = shell.union(boss)

    # Upper PCB compression pads, integral to the roof only at hole lands
    for x,y in pcb_xy():
        standoff = (cq.Workplane('XY').workplane(offset=P.pcb_top_pad_z)
                    .center(x,y).circle(P.clamp_pad_r)
                    .extrude(roof_z-P.pcb_top_pad_z+.55))
        shell=shell.union(standoff)
        pin_pocket=(cq.Workplane('XY').workplane(offset=P.pcb_top_pad_z-.02)
                    .center(x,y).circle((P.locator_d+.7)/2)
                    .extrude(P.pin_height+1.05))
        shell=shell.cut(pin_pocket)

    # One continuous shared window for Type-A and RJ45 without weak separator.
    front_w = P.front_window_x1-P.front_window_x0
    front = (cq.Workplane('XY')
             .box(front_w, 8, P.front_window_top-lid_top+.4,
                  centered=(True,True,False))
             .translate(((P.front_window_x0+P.front_window_x1)/2,
                         P.outside_y/2,P.lid_thickness-.20)))
    shell=shell.cut(front)

    rear=(cq.Workplane('XY')
          .box(P.usbc_window_width,8,P.usbc_window_top-lid_top+.4,
               centered=(True,True,False))
          .translate((0,-P.outside_y/2,P.lid_thickness-.20)))
    shell=shell.cut(rear)

    for x,y in bolt_xy():
        pilot=(cq.Workplane('XY').workplane(offset=lid_top-.2)
               .center(x,y).circle(P.insert_pilot_d/2)
               .extrude(P.insert_pilot_depth+.20))
        shell=shell.cut(pilot)
    return shell.clean()


def make_lid() -> cq.Workplane:
    lid=rounded_rectangle(P.outside_x,P.outside_y,P.lid_thickness,
                          0,P.outside_corner_r)
    # Short tongues on the uninterrupted side walls. Avoid screw bosses and ports.
    inside_x=(P.outside_x-2*P.side_wall)/2
    tongue_x=inside_x-P.tab_side_clearance-P.tab_thickness/2
    for sx in (-1,1):
        tab=(cq.Workplane('XY').workplane(offset=P.lid_thickness)
             .center(sx*tongue_x,0)
             .box(P.tab_thickness,P.tab_length,P.tab_height,
                  centered=(True,True,False)))
        lid=lid.union(tab)

    for x,y in pcb_xy():
        pad=(cq.Workplane('XY').workplane(offset=P.lid_thickness)
             .center(x,y).circle(P.clamp_pad_r)
             .extrude(P.pcb_under_z-P.lid_thickness))
        pin=(cq.Workplane('XY').workplane(offset=P.pcb_under_z-.02)
             .center(x,y).circle(P.locator_d/2)
             .extrude(P.pin_height+.02))
        lid=lid.union(pad).union(pin)

    for x,y in bolt_xy():
        through=(cq.Workplane('XY').workplane(offset=-.15)
                 .center(x,y).circle(P.m3_through_d/2)
                 .extrude(P.lid_thickness+.30))
        counter=(cq.Workplane('XY').workplane(offset=-.15)
                 .center(x,y).circle(P.screw_head_recess_d/2)
                 .extrude(P.screw_head_recess_depth+.15))
        lid=lid.cut(through).cut(counter)
    return lid.clean()


def reference_pcb() -> cq.Workplane:
    board=(cq.Workplane('XY')
           .box(P.pcb_size,P.pcb_size,P.pcb_thickness,
                centered=(True,True,False)).translate((0,0,P.pcb_under_z)))
    for x,y in pcb_xy():
        h=(cq.Workplane('XY').workplane(offset=P.pcb_under_z-.1)
           .center(x,y).circle(1.2).extrude(P.pcb_thickness+.2))
        board=board.cut(h)
    return board


def validate(shell:cq.Workplane,lid:cq.Workplane,board:cq.Workplane):
    shell_s, lid_s, board_s = shell.val(),lid.val(),board.val()
    parts_intersection=shell_s.intersect(lid_s).Volume()
    pcb_intersection=(shell_s.intersect(board_s).Volume()+
                      lid_s.intersect(board_s).Volume())
    assert len(shell.solids().vals())==1, 'Upper disconnected'
    assert len(lid.solids().vals())==1, 'Bottom disconnected'
    assert parts_intersection<0.025, f'Shell/lid collision {parts_intersection:.4f}mm3'
    assert pcb_intersection<0.10, f'PCB/shell/lid collision {pcb_intersection:.4f}mm3'
    bounds=shell_s.BoundingBox()
    assert abs(bounds.xlen-P.outside_x)<.001 and abs(bounds.ylen-P.outside_y)<.001
    total_wall_volume=shell_s.Volume()+lid_s.Volume()
    full_box_volume=P.outside_x*P.outside_y*P.height
    print(f'Bounds: {bounds.xlen:.1f}x{bounds.ylen:.1f}x{P.height:.1f} mm')
    print(f'Printed solid volume: {total_wall_volume:.1f} mm3 / '
          f'{full_box_volume:.1f} mm3 bounding box ({total_wall_volume/full_box_volume:.1%})')
    print(f'Shell vs lid overlap: {parts_intersection:.6f}mm3; '
          f'PCB proxy overlap: {pcb_intersection:.6f}mm3')
    print(f'Shell material: {shell_s.Volume():.1f} mm3, lid: {lid_s.Volume():.1f} mm3')


def main():
    shell,lid,pcb=make_upper(),make_lid(),reference_pcb()
    validate(shell,lid,pcb)
    assembly=cq.Assembly(name='ESP32-P4-NANO-Enclosure-RevB')
    assembly.add(shell,name='upper_cover',color=cq.Color(.22,.30,.38))
    assembly.add(lid,name='bottom_lid',color=cq.Color(.65,.72,.78))
    assembly.add(pcb,name='PCB_proxy__not_for_manufacture',color=cq.Color(.14,.42,.24))
    assembly.save(str(HERE/'ESP32_P4_NANO_RevB_assembly.step'))
    cq.exporters.export(shell,str(HERE/'ESP32_P4_NANO_RevB_upper.step'))
    cq.exporters.export(lid,str(HERE/'ESP32_P4_NANO_RevB_bottom.step'))
    cq.exporters.export(pcb,str(HERE/'ESP32_P4_NANO_RevB_PCB_proxy.step'))
    upper_print=(shell.rotate((0,0,0),(1,0,0),180)
                 .translate((0,0,P.height)))
    cq.exporters.export(upper_print,str(HERE/'ESP32_P4_NANO_RevB_upper_print.stl'),
                        tolerance=.075, angularTolerance=.18)
    cq.exporters.export(lid,str(HERE/'ESP32_P4_NANO_RevB_bottom_print.stl'),
                        tolerance=.075, angularTolerance=.18)

if __name__=='__main__':
    main()
