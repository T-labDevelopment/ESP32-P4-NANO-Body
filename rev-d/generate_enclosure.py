#!/usr/bin/env python3
"""ESP32-P4-NANO-Body Rev.D: mirror Rev.C USB-A/RJ45 window, widen 5 mm.

CadQuery 2.8.0, mm. Rev.B mechanics preserved. Connector dimensions and
mating remain unverified. The photo-derived connector proxies are NOT reused.
"""
from __future__ import annotations

import sys
from dataclasses import replace
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

import cadquery as cq

HERE=Path(__file__).resolve().parent
REV_B=HERE.parent/'rev-b'/'generate_enclosure.py'
if not REV_B.is_file():
    raise FileNotFoundError(f'Required parent source: {REV_B}')
spec=spec_from_file_location('enclosure_rev_b_core',REV_B)
assert spec is not None and spec.loader is not None
core=module_from_spec(spec)
sys.modules[spec.name]=core
spec.loader.exec_module(core)

# +Y is USB-A/RJ45 side, -Y USB-C. Viewed from outside the +Y face:
# viewer LEFT = increasing X; viewer RIGHT = decreasing X.
# Rev.C: [-23.0, +1.8] => opening width 24.8; walls LEFT 35.2, RIGHT 14.0.
# Mirrored: [-1.8, +23.0] => walls LEFT 14.0, RIGHT 35.2.
# Cut an ADDITIONAL 5mm into the wider viewer-RIGHT wall:
# Rev.D: [-6.8, +23.0] => width 29.8; walls LEFT 14.0, RIGHT 30.2.
# No board rotation or socket position assumptions.
P=replace(core.P,front_window_x0=-6.8,front_window_x1=23.0)
core.P=P
core.HERE=HERE
make_upper=core.make_upper
make_lid=core.make_lid
reference_pcb=core.reference_pcb

def validate_aperture():
    tol=1e-6
    width=P.front_window_x1-P.front_window_x0
    wall_left=P.outside_x/2-P.front_window_x1
    wall_right=P.outside_x/2+P.front_window_x0
    assert abs(width-29.8)<tol and abs(wall_left-14.0)<tol and abs(wall_right-30.2)<tol
    assert abs(P.front_window_x0+6.8)<tol and abs(P.front_window_x1-23.0)<tol
    # Keep front corner screw bosses clear in the X direction.
    inner_boss_x=P.screw_x-P.screw_boss_r
    assert P.front_window_x0 > -inner_boss_x and P.front_window_x1 < inner_boss_x
    print(f'Rev.D aperture width={width:.1f}mm; outside walls left={wall_left:.1f}mm, right={wall_right:.1f}mm')

def make_coupons(shell,lid):
    """+Y port face trial coupon; does not replace four-screw final housing."""
    start_y=12.0
    cutter=(cq.Workplane('XY')
            .box(P.outside_x+4,P.outside_y/2-start_y+2,P.height+4,
                 centered=(True,False,False)).translate((0,start_y,-2)))
    return shell.intersect(cutter).clean(),lid.intersect(cutter).clean()

def main():
    validate_aperture()
    shell,lid,pcb=make_upper(),make_lid(),reference_pcb()
    core.validate(shell,lid,pcb)
    assembly=cq.Assembly(name='ESP32-P4-NANO-RevD')
    assembly.add(shell,name='upper_cover',color=cq.Color(.24,.44,.59))
    assembly.add(lid,name='bottom_lid',color=cq.Color(.87,.65,.36))
    assembly.add(pcb,name='PCB_outline_ESTIMATE',color=cq.Color(.15,.42,.24))
    # Do not copy oblique-photo-based Rev.C USB-A/RJ45 connector proxies:
    # their positions were estimated and cannot validate this requested cutout.
    assembly.save(str(HERE/'ESP32_P4_NANO_RevD_assembly.step'))
    cq.exporters.export(shell,str(HERE/'ESP32_P4_NANO_RevD_upper.step'))
    cq.exporters.export(lid,str(HERE/'ESP32_P4_NANO_RevD_bottom.step'))
    cq.exporters.export(pcb,str(HERE/'ESP32_P4_NANO_RevD_PCB_proxy.step'))
    upper_print=shell.rotate((0,0,0),(1,0,0),180).translate((0,0,P.height))
    cq.exporters.export(upper_print,str(HERE/'ESP32_P4_NANO_RevD_upper_print.stl'),
                        tolerance=.075,angularTolerance=.18)
    cq.exporters.export(lid,str(HERE/'ESP32_P4_NANO_RevD_bottom_print.stl'),
                        tolerance=.075,angularTolerance=.18)
    coupon_upper,coupon_lid=make_coupons(shell,lid)
    assert len(coupon_upper.solids().vals()) == len(coupon_lid.solids().vals()) == 1
    coupon_upper=coupon_upper.rotate((0,0,0),(1,0,0),180).translate((0,0,P.height))
    cq.exporters.export(coupon_upper,str(HERE/'ESP32_P4_NANO_RevD_front_coupon_upper.stl'),
                        tolerance=.075,angularTolerance=.18)
    cq.exporters.export(coupon_lid,str(HERE/'ESP32_P4_NANO_RevD_front_coupon_bottom.stl'),
                        tolerance=.075,angularTolerance=.18)
    print('Rev.D: mirrored plus 5mm expanded opening exported. PHYSICAL FIT NOT VERIFIED.')

if __name__=='__main__':
    main()
