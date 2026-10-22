#!/usr/bin/env python3
"""ESP32-P4-NANO-Body Rev.C; photo-oriented USB-A/RJ45 port aperture.
CadQuery 2.8.0. Base Rev.B source resides in ../rev-b/generate_enclosure.py.
The original PCB mounting orientation is preserved.
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
    raise FileNotFoundError(f'Rev.B parent CAD source required: {REV_B}')
spec=spec_from_file_location('enclosure_rev_b_core', REV_B)
assert spec is not None and spec.loader is not None
core=module_from_spec(spec)
sys.modules[spec.name]=core
spec.loader.exec_module(core)

# +Y is USB-A/RJ45, and -Y is USB-C.
# Looking INTO +Y connector face with roof UP, USB-A LEFT, RJ45 RIGHT.
# Rev.B X=[-21.4,+13.4] was offset toward empty space at photograph left.
# Rev.C X=[-23.0,+1.8] moves aperture toward observed sockets.
# Oblique photo-based placement: physical dimensional fit is unverified.
P=replace(core.P,front_window_x0=-23.0,front_window_x1=1.8)
core.P=P
core.HERE=HERE
make_upper=core.make_upper
make_lid=core.make_lid
reference_pcb=core.reference_pcb
bolt_xy=core.bolt_xy
pcb_xy=core.pcb_xy

# Approximate face envelopes (not manufacturer connector CAD).
PORT_PROXIES={
    'USB_A': {'cx':-3.0,'width':7.8,'bottom':7.5,'top':20.6},
    'RJ45': {'cx':-14.0,'width':12.4,'bottom':9.8,'top':22.5},
}

def make_connector_proxies():
    proxies={}
    for name,info in PORT_PROXIES.items():
        proxies[name]=(cq.Workplane('XY').workplane(offset=info['bottom'])
                       .center(info['cx'],P.outside_y/2-3.6)
                       .box(info['width'],4,info['top']-info['bottom'],
                            centered=(True,True,False)))
    return proxies

def make_coupons(shell,lid):
    """Front 19mm shell/lid parts for trial fitting, not operational use."""
    start_y=12.0
    section=(cq.Workplane('XY')
             .box(P.outside_x+4,P.outside_y/2-start_y+2,P.height+4,
                  centered=(True,False,False)).translate((0,start_y,-2)))
    return shell.intersect(section).clean(),lid.intersect(section).clean()

def validate_photo_orientation():
    assert PORT_PROXIES['USB_A']['cx'] > PORT_PROXIES['RJ45']['cx'], 'Exterior port order'
    for port in PORT_PROXIES.values():
        x0=port['cx']-port['width']/2
        x1=port['cx']+port['width']/2
        assert P.front_window_x0+1.0 < x0 and x1 < P.front_window_x1-.7
        assert P.lid_thickness+1.0 < port['bottom']
        assert port['top'] < P.front_window_top-.75

def main():
    shell,lid,pcb=make_upper(),make_lid(),reference_pcb()
    core.validate(shell,lid,pcb)
    validate_photo_orientation()
    assembly=cq.Assembly(name='ESP32-P4-NANO-RevC')
    assembly.add(shell,name='upper_cover',color=cq.Color(.24,.44,.59))
    assembly.add(lid,name='bottom_lid',color=cq.Color(.87,.65,.36))
    assembly.add(pcb,name='PCB_outline_ESTIMATE',color=cq.Color(.15,.42,.24))
    for name,shape in make_connector_proxies().items():
        assembly.add(shape,name=name+'_FACE_ESTIMATE',color=cq.Color(.95,.45,.16))
    assembly.save(str(HERE/'ESP32_P4_NANO_RevC_assembly.step'))
    cq.exporters.export(shell,str(HERE/'ESP32_P4_NANO_RevC_upper.step'))
    cq.exporters.export(lid,str(HERE/'ESP32_P4_NANO_RevC_bottom.step'))
    cq.exporters.export(pcb,str(HERE/'ESP32_P4_NANO_RevC_PCB_proxy.step'))
    upper_print=shell.rotate((0,0,0),(1,0,0),180).translate((0,0,P.height))
    cq.exporters.export(upper_print,str(HERE/'ESP32_P4_NANO_RevC_upper_print.stl'),
                        tolerance=.075,angularTolerance=.18)
    cq.exporters.export(lid,str(HERE/'ESP32_P4_NANO_RevC_bottom_print.stl'),
                        tolerance=.075,angularTolerance=.18)
    upper_coupon,bottom_coupon=make_coupons(shell,lid)
    assert len(upper_coupon.solids().vals())==len(bottom_coupon.solids().vals())==1
    upper_coupon_print=upper_coupon.rotate((0,0,0),(1,0,0),180).translate((0,0,P.height))
    cq.exporters.export(upper_coupon_print,str(HERE/'ESP32_P4_NANO_RevC_front_coupon_upper.stl'),
                        tolerance=.075,angularTolerance=.18)
    cq.exporters.export(bottom_coupon,str(HERE/'ESP32_P4_NANO_RevC_front_coupon_bottom.stl'),
                        tolerance=.075,angularTolerance=.18)
    print('Rev.C: aperture corrected to actual connector-side orientation; physical fit not yet verified')

if __name__=='__main__':
    main()
