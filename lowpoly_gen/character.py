"""Parametric chibi humanoid, proportions measured from the 52 reference FBX files.

Reference facts (all files): Z up, front = -Y, T-pose, 3.77 tall incl. hat, head
z 2.07..3.13 (~45% of height), arm span 3.24, one mesh "Body" with flat-colour
material slots, 19 weighted deform bones.  Everything below is expressed in those
units so generated models are drop-in compatible with the reference animations.
"""
import math

from .builder import Builder
from .palettes import col, NAMED

HEAD_Z0, HEAD_Z1 = 2.07, 3.13


# --------------------------------------------------------------------------- spec
def default_spec():
    return dict(
        name="Character", gender="male", skin="light", head_scale=1.0,
        torso=dict(color="blue", sleeves="short"),
        legs=dict(color="navy", length="long"),
        boots=None, gloves=None, belt=None, vest=None,
        hair=dict(style="short", color="hairbrown"),
        beard=None, hat=None,
        face="default", ears="round", snout=None, nose=True,
        extras=[],
    )


def merge(base, over):
    out = dict(base)
    for k, v in (over or {}).items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = merge(out[k], v)
        else:
            out[k] = v
    return out


# --------------------------------------------------------------------------- helpers
class Ctx:
    def __init__(self, b, sp):
        self.b, self.sp = b, sp
        self.hs = float(sp.get("head_scale", 1.0))
        self.fem = sp.get("gender") == "female"

    def hz(self, z):
        """Head-relative z (scales around the neck base)."""
        return HEAD_Z0 + (z - HEAD_Z0) * self.hs

    def hr(self, r):
        return r * self.hs

    def mat(self, name, color):
        return self.b.material(name, col(color))


def ring(c, ru, rv=None, w=None, **kw):
    d = dict(c=c, ru=ru, rv=ru if rv is None else rv, w=w)
    d.update(kw)
    return d


# --------------------------------------------------------------------------- body
def build_body(cx):
    b, sp = cx.b, cx.sp
    fem = cx.fem
    sw = 0.93 if fem else 1.0
    hw = 1.06 if fem else 1.0
    skin = cx.mat("Skin", sp["skin"])
    torso = sp["torso"]
    legs = sp["legs"]
    cx.mat("Shirt", torso["color"])
    cx.mat("Pants", legs["color"])
    sleeves = torso.get("sleeves", "short")
    skirt = legs.get("length") == "skirt"
    lower_mat = "Shirt" if skirt else "Pants"
    if torso.get("bare"):
        shirt_mat = "Skin"
    else:
        shirt_mat = "Shirt"

    # --- spine: hips -> abdomen -> chest, 8 sided squircle prism
    spine = [
        ring((0, 0.02, 0.88), 0.27 * hw, 0.20, "Hips"),
        ring((0, 0.02, 1.10), 0.31 * hw, 0.22, "Hips"),
        ring((0, 0.00, 1.30), 0.30 * hw, 0.22, {"Hips": 0.5, "Abdomen": 0.5}),
        ring((0, 0.00, 1.45), 0.29, 0.21, "Abdomen"),
        ring((0, 0.00, 1.57), 0.31 * sw, 0.21, {"Abdomen": 0.5, "Torso": 0.5}),
        ring((0, 0.00, 1.85), 0.37 * sw, 0.23, "Torso"),
        ring((0, 0.00, 2.08), 0.30 * sw, 0.19, "Torso"),
    ]
    mats = [lower_mat, lower_mat, shirt_mat, shirt_mat, shirt_mat, shirt_mat]
    if torso.get("bare"):
        mats = [lower_mat, lower_mat, "Skin", "Skin", "Skin", "Skin"]
    b.loft(spine, "Skin", sides=8, rot=math.pi / 8, sq=0.62, ring_mats=mats)

    # --- neck
    b.loft([ring((0, 0, 2.0), 0.13, 0.12, "Neck"), ring((0, 0, 2.2), 0.13, 0.12, "Neck")],
           "Skin", sides=6, caps=(False, False))

    # --- head
    build_head(cx)

    # --- belt
    if sp.get("belt"):
        cx.mat("Belt", sp["belt"])
        b.loft([ring((0, 0.0, 1.20), 0.325 * hw, 0.235, {"Hips": 1.0}),
                ring((0, 0.0, 1.34), 0.315 * hw, 0.23, {"Hips": 0.5, "Abdomen": 0.5})],
               "Belt", sides=8, rot=math.pi / 8, sq=0.62, caps=(False, False))
        b.box((0, -0.235, 1.27), (0.12, 0.03, 0.12), "Gold" if "Gold" in b.mat_names else "Belt", "Hips")

    # --- arms
    if sp.get("gloves"):
        cx.mat("Gloves", sp["gloves"])
    hand = "Gloves" if sp.get("gloves") else "Skin"
    sleeve_mat = "Shirt" if not torso.get("bare") else "Skin"
    if sleeves == "none":
        upper, lower = "Skin", "Skin"
    elif sleeves == "short":
        upper, lower = sleeve_mat, "Skin"
    else:
        upper, lower = sleeve_mat, sleeve_mat
    for s, side in ((1, "L"), (-1, "R")):
        z, y = 1.87, 0.015
        r = [
            ring((s * 0.14, y, z), 0.16, 0.16, "Shoulder." + side),
            ring((s * 0.34, y, z), 0.16, 0.16, {"Shoulder." + side: 0.5, "UpperArm." + side: 0.5}),
            ring((s * 0.85, y + 0.02, z), 0.14, 0.14, {"UpperArm." + side: 0.5, "LowerArm." + side: 0.5}),
            ring((s * 1.27, y + 0.01, z - 0.01), 0.125, 0.125, {"LowerArm." + side: 0.5, "Fist." + side: 0.5}),
            ring((s * 1.43, y, z - 0.01), 0.165, 0.16, "Fist." + side),
            ring((s * 1.62, y, z - 0.01), 0.10, 0.10, "Fist." + side),
        ]
        b.loft(r, "Skin", sides=6, rot=math.pi / 6, ring_mats=[upper, upper, lower, hand, hand])

    # --- legs
    boots = sp.get("boots")
    if boots:
        cx.mat("Boots", boots)
    shorts = legs.get("length") == "shorts"
    for s, side in ((1, "L"), (-1, "R")):
        x = s * 0.26
        r = [
            ring((x, 0.03, 1.10), 0.17, 0.17, "UpperLeg." + side),
            ring((x, 0.02, 0.78), 0.155, 0.155, "UpperLeg." + side),
            ring((x, 0.00, 0.54), 0.14, 0.14, {"UpperLeg." + side: 0.5, "LowerLeg." + side: 0.5}),
            ring((x, 0.03, 0.34), 0.125, 0.125, "LowerLeg." + side),
            ring((x, 0.04, 0.10), 0.13, 0.13, "LowerLeg." + side),
        ]
        if skirt:
            mm = ["Skin", "Skin", "Skin", "Boots" if boots else "Skin"]
        elif shorts:
            mm = ["Pants", "Pants", "Skin", "Boots" if boots else "Skin"]
        else:
            mm = ["Pants", "Pants", "Pants", "Boots" if boots else "Pants"]
        b.loft(r, "Skin", sides=6, rot=math.pi / 6, ring_mats=mm)
        foot_mat = "Boots" if boots else ("Skin" if (skirt or shorts) else "Pants")
        b.box((x, -0.12, 0.07), (0.27, 0.50, 0.15), foot_mat, "Foot." + side, taper=(0.9, 0.8))

    if skirt:
        cx.mat("Skirt", legs["color"])
        b.loft([ring((0, 0.01, 1.30), 0.33 * hw, 0.25, {"Hips": 1.0}),
                ring((0, 0.0, 0.95), 0.50, 0.40, {"Hips": 0.6, "UpperLeg.L": 0.2, "UpperLeg.R": 0.2}),
                ring((0, 0.0, 0.62), 0.62, 0.52, {"Hips": 0.5, "UpperLeg.L": 0.25, "UpperLeg.R": 0.25})],
               "Skirt", sides=8, rot=math.pi / 8, caps=(False, False))


def build_head(cx):
    b, sp, hs = cx.b, cx.sp, cx.hs
    prof = [(2.07, 0.30, 0.30), (2.20, 0.44, 0.43), (2.45, 0.52, 0.50),
            (2.80, 0.53, 0.50), (3.00, 0.49, 0.47), (3.13, 0.34, 0.33)]
    rings = [ring((0, 0, cx.hz(z)), cx.hr(ru), cx.hr(rv), "Head") for z, ru, rv in prof]
    b.loft(rings, "Skin", sides=8, rot=math.pi / 8, sq=0.6)


# --------------------------------------------------------------------------- face
def build_face(cx):
    b, sp = cx.b, cx.sp
    style = sp.get("face", "default")
    if style == "none":
        return
    eye = cx.mat("Face", sp.get("face_color", "eye"))
    fy = -0.47 * cx.hs        # front plane of the head
    z = cx.hz(2.62)
    s = cx.hs
    if style == "default":
        for sx in (1, -1):
            b.box((sx * 0.2 * s, fy, z), (0.075 * s, 0.09, 0.17 * s), "Face", "Head")
        b.box((0, fy, cx.hz(2.33)), (0.17 * s, 0.09, 0.045 * s), "Face", "Head")
    elif style == "cute":
        for sx in (1, -1):
            b.box((sx * 0.22 * s, fy, cx.hz(2.55)), (0.11 * s, 0.09, 0.22 * s), "Face", "Head")
        b.box((0, fy, cx.hz(2.3)), (0.08 * s, 0.09, 0.04 * s), "Face", "Head")
    elif style == "angry":
        for sx in (1, -1):
            b.box((sx * 0.2 * s, fy, z), (0.09 * s, 0.09, 0.12 * s), "Face", "Head")
            b.box((sx * 0.2 * s, fy, cx.hz(2.76)), (0.17 * s, 0.09, 0.04 * s), "Face", "Head",
                  rotz=0.0, roty=sx * 0.35)
        b.box((0, fy, cx.hz(2.3)), (0.26 * s, 0.09, 0.05 * s), "Face", "Head")
    elif style in ("goblin", "zombie"):
        sizes = [(0.13, 0.19), (0.13, 0.19)] if style == "goblin" else [(0.15, 0.2), (0.07, 0.07)]
        for sx, (w, h) in zip((1, -1), sizes):
            b.box((sx * 0.21 * s, fy, z), (w * s, 0.09, h * s), "Face", "Head")
        b.box((0, fy, cx.hz(2.3)), (0.32 * s, 0.09, 0.07 * s), "Face", "Head")
        if style == "goblin":
            cx.mat("Teeth", "teeth")
            for sx in (1, -1):
                b.box((sx * 0.1 * s, fy - 0.01, cx.hz(2.36)), (0.05 * s, 0.07, 0.1 * s), "Teeth", "Head")
    if sp.get("nose", True) and not sp.get("snout"):
        b.box((0, fy - 0.01, cx.hz(2.47)), (0.1 * s, 0.1, 0.12 * s), "Skin", "Head")


# --------------------------------------------------------------------------- ears / snout / beard
def build_ears(cx):
    b, sp, s = cx.b, cx.sp, cx.hs
    kind = sp.get("ears", "round")
    z = cx.hz(2.62)
    if kind == "round":
        for sx in (1, -1):
            b.box((sx * 0.53 * s, 0.05, z), (0.1, 0.18, 0.24 * s), "Skin", "Head")
    elif kind == "elf":
        for sx in (1, -1):
            b.loft([ring((sx * 0.48 * s, 0.06, z - 0.02), 0.11, 0.06, "Head"),
                    ring((sx * 0.92 * s, 0.12, z + 0.30), 0.02, 0.02, "Head")],
                   "Skin", sides=4, rot=math.pi / 4, caps=(True, False))
    elif kind == "goblin":
        for sx in (1, -1):
            b.loft([ring((sx * 0.48 * s, 0.06, z), 0.15, 0.06, "Head"),
                    ring((sx * 1.05 * s, 0.1, z + 0.12), 0.03, 0.02, "Head")],
                   "Skin", sides=4, rot=math.pi / 4, caps=(True, False))
    elif kind in ("pug", "floppy"):
        cx.mat("EarFloppy", sp.get("ear_color", "darkbrown"))
        for sx in (1, -1):
            b.box((sx * 0.56 * s, -0.05, cx.hz(2.75)), (0.12, 0.34, 0.5 * s), "EarFloppy", "Head", taper=(1, 0.8))
    elif kind == "cow":
        cx.mat("EarCow", sp.get("ear_color", "cowblack"))
        for sx in (1, -1):
            b.box((sx * 0.74 * s, 0.05, cx.hz(2.82)), (0.4, 0.18, 0.16), "EarCow", "Head", rotz=sx * 0.2)
    elif kind == "cat":
        for sx in (1, -1):
            b.cone((sx * 0.3 * s, 0.05, cx.hz(3.05)), (sx * 0.42 * s, 0.05, cx.hz(3.45)), 0.17, "Skin", "Head",
                   sides=4, rot=math.pi / 4)


def build_snout(cx):
    b, sp, s = cx.b, cx.sp, cx.hs
    kind = sp.get("snout")
    if not kind:
        return
    if kind == "pug":
        cx.mat("Snout", sp.get("snout_color", "beige"))
        b.box((0, -0.53 * s, cx.hz(2.42)), (0.42 * s, 0.22, 0.30 * s), "Snout", "Head")
        b.box((0, -0.65 * s, cx.hz(2.48)), (0.16 * s, 0.05, 0.1 * s), "Face", "Head")
    elif kind == "cow":
        cx.mat("Snout", sp.get("snout_color", "pink"))
        b.box((0, -0.56 * s, cx.hz(2.3)), (0.58 * s, 0.26, 0.34 * s), "Snout", "Head")
        for sx in (1, -1):
            b.box((sx * 0.1 * s, -0.7 * s, cx.hz(2.3)), (0.07, 0.03, 0.08), "Face", "Head")
    elif kind == "beak":
        cx.mat("Snout", sp.get("snout_color", "orange"))
        b.cone((0, -0.45 * s, cx.hz(2.4)), (0, -0.95 * s, cx.hz(2.35)), 0.2 * s, "Snout", "Head",
               sides=4, rot=math.pi / 4)


def build_beard(cx):
    b, sp, s = cx.b, cx.sp, cx.hs
    bd = sp.get("beard")
    if not bd:
        return
    kind = bd.get("style", "moustache")
    cx.mat("Beard", bd.get("color", "hairbrown"))
    fy = -0.47 * s
    if kind in ("moustache", "full"):
        b.box((0, fy - 0.01, cx.hz(2.41)), (0.42 * s, 0.09, 0.09 * s), "Beard", "Head")
    if kind == "full":
        b.box((0, fy + 0.02, cx.hz(2.17)), (0.72 * s, 0.14, 0.38 * s), "Beard", "Head", taper=(0.8, 1))
        for sx in (1, -1):
            b.box((sx * 0.5 * s, fy + 0.3, cx.hz(2.4)), (0.07, 0.34, 0.45 * s), "Beard", "Head")
    if kind == "goatee":
        b.box((0, fy + 0.02, cx.hz(2.2)), (0.2 * s, 0.1, 0.22 * s), "Beard", "Head", taper=(0.6, 1))
    if kind == "long":
        b.loft([ring((0, fy + 0.05, cx.hz(2.3)), 0.3 * s, 0.07, "Head"),
                ring((0, fy + 0.1, cx.hz(1.9)), 0.26 * s, 0.07, {"Head": 0.5, "Neck": 0.5}),
                ring((0, fy + 0.2, cx.hz(1.45)), 0.08, 0.05, "Torso")],
               "Beard", sides=4, rot=math.pi / 4)


# --------------------------------------------------------------------------- hair
def _dome(cx, mat, z_low=2.82, grow=1.07):
    s = cx.hs
    pts = [(z_low, 0.535, 0.505), (3.0, 0.50, 0.475), (3.13, 0.37, 0.35), (3.2, 0.2, 0.19)]
    rings = [ring((0, 0.0, cx.hz(z)), cx.hr(ru * grow), cx.hr(rv * grow), "Head") for z, ru, rv in pts]
    cx.b.loft(rings, mat, sides=8, rot=math.pi / 8, sq=0.6, caps=(False, True))


def build_hair(cx):
    b, sp, s = cx.b, cx.sp, cx.hs
    h = sp.get("hair")
    if not h or h.get("style") in (None, "bald", "none"):
        return
    style = h["style"]
    cx.mat("Hair", h.get("color", "hairbrown"))
    if style == "afro":
        b.blob((0, 0.05, cx.hz(2.95)), (cx.hr(0.72), cx.hr(0.68), cx.hr(0.62)), "Hair", "Head", sides=8, rings=4)
        return
    if style in ("beanie_hair",):
        return
    z_low = 2.82 if style not in ("fringe",) else 2.7
    _dome(cx, "Hair", z_low)
    back_y = 0.5 * s
    if style in ("short", "spiky", "ponytail", "bun", "fringe"):
        b.box((0, back_y, cx.hz(2.65)), (cx.hr(0.98), 0.14, cx.hr(0.42)), "Hair", "Head")
        for sx in (1, -1):
            b.box((sx * cx.hr(0.535), 0.1, cx.hz(2.72)), (0.07, cx.hr(0.55), cx.hr(0.3)), "Hair", "Head")
    if style in ("long", "bob"):
        bottom = 2.2 if style == "bob" else 1.7
        mid = (bottom + 2.9) / 2
        b.box((0, back_y + 0.04, mid), (cx.hr(1.04), 0.16, 2.9 - bottom), "Hair", {"Head": 0.6, "Neck": 0.4})
        for sx in (1, -1):
            b.box((sx * cx.hr(0.54), 0.2, (bottom + 2.95) / 2 + (0.15 if style == "long" else 0.05)),
                  (0.09, cx.hr(0.55), (2.95 - bottom) - 0.3), "Hair", {"Head": 0.7, "Neck": 0.3})
    if style == "fringe":
        b.box((0, -0.5 * s, cx.hz(2.82)), (cx.hr(1.0), 0.1, cx.hr(0.2)), "Hair", "Head")
    if style == "ponytail":
        b.loft([ring((0, 0.5 * s, cx.hz(2.95)), 0.14, 0.14, "Head"),
                ring((0, 0.82 * s, cx.hz(2.8)), 0.15, 0.15, "Head"),
                ring((0, 0.92 * s, cx.hz(2.25)), 0.11, 0.11, {"Head": 0.5, "Neck": 0.5}),
                ring((0, 0.88 * s, cx.hz(1.9)), 0.05, 0.05, "Neck")],
               "Hair", sides=5)
    if style == "bun":
        b.blob((0, 0.1, cx.hz(3.38)), (0.24 * s, 0.24 * s, 0.2 * s), "Hair", "Head", sides=6, rings=2)
    if style == "spiky":
        for (x, y) in ((0, 0), (0.25, 0.1), (-0.25, 0.1), (0.15, -0.2), (-0.15, -0.2), (0, 0.3)):
            b.cone((x * s, y * s, cx.hz(3.13)), (x * s * 1.3, y * s * 1.3, cx.hz(3.55)), 0.13 * s, "Hair", "Head",
                   sides=4, rot=math.pi / 4)
    if style == "mohawk":
        for i, y in enumerate((-0.3, -0.1, 0.1, 0.3)):
            b.box((0, y * s, cx.hz(3.28)), (0.12, 0.2 * s, 0.4 * s), "Hair", "Head", taper=(1, 0.7))


# --------------------------------------------------------------------------- hats
def build_hat(cx):
    b, sp, s = cx.b, cx.sp, cx.hs
    h = sp.get("hat")
    if not h:
        return
    kind = h["type"]
    c1 = h.get("color", "brown")
    c2 = h.get("color2", "gold")
    cx.mat("Hat", c1)
    z = lambda v: cx.hz(v)
    R = lambda v: cx.hr(v)

    def band(zb, r, thick=0.1, name="HatBand", rr=None):
        cx.mat(name, c2)
        b.loft([ring((0, 0, z(zb)), R(r), R(rr or r * 0.95), "Head"),
                ring((0, 0, z(zb + thick)), R(r), R(rr or r * 0.95), "Head")],
               name, sides=10, caps=(False, False))

    if kind in ("wizard", "witch"):
        b.disc_ring((0, 0, z(3.0)), 0.55 * s, 0.9 * s, 0.07, "Hat", "Head", sides=10)
        b.loft([ring((0, 0.0, z(3.03)), R(0.58), R(0.55), "Head"),
                ring((0, 0.02, z(3.4)), R(0.46), R(0.44), "Head"),
                ring((0, 0.08, z(3.8)), R(0.30), R(0.28), "Head"),
                ring((0, 0.25, z(4.15) if kind == "wizard" else z(4.3)), 0.02, 0.02, "Head")],
               "Hat", sides=8, caps=(False, True))
        band(3.03, 0.585, 0.12)
    elif kind == "cowboy":
        b.loft([ring((0, 0, z(3.0)), R(0.9), R(0.72), "Head"),
                ring((0, 0, z(3.07)), R(0.55), R(0.52), "Head")], "Hat", sides=12)
        for sx in (1, -1):   # curled up sides
            b.box((sx * R(0.78), 0, z(3.12)), (0.2, R(0.9), 0.06), "Hat", "Head", roty=sx * -0.35)
        b.loft([ring((0, 0, z(3.05)), R(0.52), R(0.5), "Head"),
                ring((0, 0, z(3.40)), R(0.50), R(0.48), "Head"),
                ring((0, 0, z(3.52)), R(0.40), R(0.38), "Head")], "Hat", sides=8, caps=(False, True))
        band(3.07, 0.535, 0.1, rr=0.51)
    elif kind == "chef":
        band(2.98, 0.56, 0.35, "HatBand", 0.53)
        b.blob((0, 0, z(3.55)), (R(0.72), R(0.66), 0.4 * s), "Hat", "Head", sides=8, rings=3)
    elif kind in ("viking", "helmet", "soldier"):
        tall = 3.42 if kind == "viking" else 3.3
        b.loft([ring((0, 0, z(2.9)), R(0.575), R(0.55), "Head"),
                ring((0, 0, z(3.1)), R(0.56), R(0.53), "Head"),
                ring((0, 0, z(tall - 0.12)), R(0.42), R(0.4), "Head"),
                ring((0, 0, z(tall)), R(0.14), R(0.14), "Head")],
               "Hat", sides=8, rot=math.pi / 8, sq=0.8, caps=(False, True))
        if kind == "viking":
            cx.mat("Horns", "horn")
            for sx in (1, -1):
                b.loft([ring((sx * R(0.52), 0, z(3.0)), 0.14, 0.14, "Head"),
                        ring((sx * R(0.82), 0, z(3.05)), 0.13, 0.13, "Head"),
                        ring((sx * R(0.98), 0, z(3.35)), 0.09, 0.09, "Head"),
                        ring((sx * R(0.9), 0, z(3.7)), 0.02, 0.02, "Head")],
                       "Horns", sides=5)
        if kind == "soldier":
            b.box((0, -R(0.5), z(3.0)), (R(0.9), 0.14, 0.06), "Hat", "Head")
    elif kind == "tophat":
        b.disc_ring((0, 0, z(3.08)), 0.5 * s, 0.68 * s, 0.06, "Hat", "Head", sides=10)
        b.loft([ring((0, 0, z(3.08)), R(0.44), R(0.42), "Head"), ring((0, 0, z(3.8)), R(0.42), R(0.4), "Head")],
               "Hat", sides=10)
        band(3.1, 0.445, 0.14)
    elif kind in ("hardhat", "cap"):
        b.loft([ring((0, 0, z(2.95)), R(0.57), R(0.55), "Head"),
                ring((0, 0, z(3.2)), R(0.5), R(0.48), "Head"),
                ring((0, 0, z(3.42)), R(0.24), R(0.22), "Head")],
               "Hat", sides=8, rot=math.pi / 8, sq=0.8, caps=(False, True))
        b.box((0, -R(0.55), z(3.0)), (R(0.8), 0.45, 0.07), "Hat", "Head")
        if kind == "hardhat":
            b.box((0, 0, z(3.36)), (0.14, R(0.9), 0.1), "Hat", "Head")
    elif kind == "bicorne":
        b.loft([ring((0, 0, z(3.0)), R(0.62), R(0.5), "Head"), ring((0, 0, z(3.32)), R(0.78), R(0.4), "Head"),
                ring((0, 0, z(3.5)), R(0.45), R(0.2), "Head")], "Hat", sides=8, caps=(False, True))
        for sx in (1, -1):
            b.box((sx * R(0.7), 0, z(3.2)), (0.14, R(1.0), 0.38), "Hat", "Head", roty=sx * 0.5)
        band(3.0, 0.63, 0.1, rr=0.51)
    elif kind == "crown":
        cx.mat("Hat", c1)
        b.loft([ring((0, 0, z(3.05)), R(0.5), R(0.48), "Head"), ring((0, 0, z(3.3)), R(0.5), R(0.48), "Head")],
               "Hat", sides=10, caps=(False, False))
        for k in range(5):
            a = 2 * math.pi * k / 5
            b.cone((math.cos(a) * R(0.5), math.sin(a) * R(0.48), z(3.3)),
                   (math.cos(a) * R(0.5), math.sin(a) * R(0.48), z(3.62)), 0.1, "Hat", "Head", sides=4, rot=math.pi / 4)
    elif kind == "knight":
        b.loft([ring((0, 0, z(2.15)), R(0.57), R(0.55), "Head"),
                ring((0, 0, z(2.5)), R(0.6), R(0.58), "Head"),
                ring((0, 0, z(3.0)), R(0.6), R(0.58), "Head"),
                ring((0, 0, z(3.2)), R(0.46), R(0.44), "Head"),
                ring((0, 0, z(3.3)), R(0.2), R(0.2), "Head")],
               "Hat", sides=8, rot=math.pi / 8, sq=0.6, caps=(False, True))
        cx.mat("Visor", "darkgrey")
        b.box((0, -R(0.6), z(2.62)), (R(0.78), 0.05, 0.1 * s), "Visor", "Head")
        cx.mat("Plume", c2)
        b.box((0, 0.0, z(3.45)), (0.1, R(0.55), 0.3 * s), "Plume", "Head", taper=(1, 0.5))
    elif kind == "ninja":
        cx.mat("Hat", c1)
        b.loft([ring((0, 0, z(2.1)), R(0.55), R(0.52), "Head"), ring((0, 0, z(2.49)), R(0.57), R(0.55), "Head")],
               "Hat", sides=8, rot=math.pi / 8, sq=0.6, caps=(False, False))
        b.loft([ring((0, 0, z(2.76)), R(0.575), R(0.55), "Head"), ring((0, 0, z(3.0)), R(0.55), R(0.52), "Head"),
                ring((0, 0, z(3.13)), R(0.4), R(0.38), "Head"), ring((0, 0, z(3.2)), R(0.2), R(0.2), "Head")],
               "Hat", sides=8, rot=math.pi / 8, sq=0.6, caps=(False, True))
        b.box((0, 0.55 * s, z(2.95)), (0.18, 0.5, 0.12), "Hat", "Head", rotz=0.0)   # knot tail
    elif kind == "beanie":
        b.loft([ring((0, 0, z(2.88)), R(0.57), R(0.54), "Head"), ring((0, 0, z(3.1)), R(0.55), R(0.52), "Head"),
                ring((0, 0, z(3.3)), R(0.38), R(0.36), "Head"), ring((0, 0, z(3.38)), R(0.12), R(0.12), "Head")],
               "Hat", sides=8, rot=math.pi / 8, sq=0.8, caps=(False, True))
        b.blob((0, 0, z(3.46)), (0.14 * s, 0.14 * s, 0.12 * s), "HatBand" if "HatBand" in b.mat_names else "Hat", "Head",
               sides=5, rings=2)


# --------------------------------------------------------------------------- extras
def build_extras(cx):
    b, sp = cx.b, cx.sp
    for ex in sp.get("extras", []):
        t = ex["type"]
        c = ex.get("color", "red")
        if t == "cape":
            cx.mat("Cape", c)
            b.loft([ring((0, 0.27, 2.08), 0.52, 0.04, "Torso", sq=1.0),
                    ring((0, 0.38, 1.5), 0.62, 0.04, {"Torso": 0.5, "Abdomen": 0.5}),
                    ring((0, 0.46, 0.75), 0.78, 0.04, {"Abdomen": 0.5, "Hips": 0.5})],
                   "Cape", sides=4, rot=math.pi / 4)
        elif t == "scarf":
            cx.mat("Scarf", c)
            b.loft([ring((0, 0, 2.0), 0.24, 0.22, "Neck"), ring((0, 0, 2.16), 0.23, 0.21, "Neck")],
                   "Scarf", sides=8, rot=math.pi / 8, caps=(False, False))
            b.box((0.18, -0.24, 1.8), (0.18, 0.05, 0.42), "Scarf", "Torso")
        elif t == "shoulder_pads":
            cx.mat("Pad", c)
            for s, side in ((1, "L"), (-1, "R")):
                b.blob((s * 0.34, 0.01, 2.08), (0.26, 0.24, 0.15), "Pad", "Shoulder." + side, sides=6, rings=2)
        elif t == "chest_armor":
            cx.mat("Armor", c)
            b.loft([ring((0, 0, 1.52), 0.34, 0.235, {"Abdomen": 0.5, "Torso": 0.5}),
                    ring((0, 0, 1.85), 0.40, 0.255, "Torso"),
                    ring((0, 0, 2.09), 0.32, 0.215, "Torso")],
                   "Armor", sides=8, rot=math.pi / 8, sq=0.62, caps=(False, False))
        elif t == "vest":
            cx.mat("Vest", c)
            b.loft([ring((0, 0, 1.45), 0.30, 0.215, "Abdomen"), ring((0, 0, 1.85), 0.385, 0.245, "Torso"),
                    ring((0, 0, 2.0), 0.35, 0.22, "Torso")],
                   "Vest", sides=8, rot=math.pi / 8, sq=0.62, caps=(False, False))
        elif t == "backpack":
            cx.mat("Pack", c)
            b.box((0, 0.36, 1.78), (0.52, 0.3, 0.6), "Pack", "Torso")
        elif t == "tail":
            cx.mat("Tail", c)
            b.loft([ring((0, 0.2, 1.05), 0.1, 0.1, "Hips"), ring((0, 0.6, 0.95), 0.09, 0.09, "Hips"),
                    ring((0, 0.9, 1.15), 0.07, 0.07, "Hips"), ring((0, 0.95, 1.5), 0.03, 0.03, "Hips")],
                   "Tail", sides=5)
        elif t == "bones":
            cx.mat("Bones", c)
            for sx in (1, -1):
                b.box((sx * 0.1, -0.235, 1.75), (0.3, 0.05, 0.05), "Bones", "Torso", rotz=0.0)
                b.box((sx * 0.1, -0.235, 1.62), (0.26, 0.05, 0.05), "Bones", "Torso")
        elif t in ("sword", "staff", "axe", "torch"):
            _held(cx, t, c, ex.get("color2", "brown"))
        elif t == "glasses":
            cx.mat("Glasses", c)
            for sx in (1, -1):
                b.box((sx * 0.2 * cx.hs, -0.5 * cx.hs, cx.hz(2.62)), (0.22 * cx.hs, 0.04, 0.2 * cx.hs), "Glasses", "Head")
            b.box((0, -0.5 * cx.hs, cx.hz(2.64)), (0.2 * cx.hs, 0.04, 0.03), "Glasses", "Head")
        elif t == "eyepatch":
            cx.mat("Patch", c)
            b.box((0.2 * cx.hs, -0.51 * cx.hs, cx.hz(2.62)), (0.22 * cx.hs, 0.05, 0.22 * cx.hs), "Patch", "Head")
        elif t == "horns":
            cx.mat("Horns", c)
            for sx in (1, -1):
                b.loft([ring((sx * cx.hr(0.3), 0, cx.hz(3.1)), 0.11, 0.11, "Head"),
                        ring((sx * cx.hr(0.5), 0, cx.hz(3.3)), 0.09, 0.09, "Head"),
                        ring((sx * cx.hr(0.62), 0, cx.hz(3.6)), 0.02, 0.02, "Head")], "Horns", sides=5)
        elif t == "wounds":
            cx.mat("Guts", c)
            b.box((0.1, -0.235, 1.7), (0.3, 0.04, 0.26), "Guts", "Torso")
            b.box((-0.15, -0.49 * cx.hs, cx.hz(2.45)), (0.16, 0.04, 0.12), "Guts", "Head")


def _held(cx, kind, c, c2):
    b = cx.b
    x, z = -1.45, 1.86
    w = "Fist.R"
    if kind == "sword":
        cx.mat("Blade", c)
        cx.mat("Grip", c2)
        b.box((x, 0, z + 0.05), (0.07, 0.07, 0.34), "Grip", w)
        b.box((x, 0, z + 0.24), (0.1, 0.45, 0.07), "Blade" if c == "steel" else "Grip", w)
        b.box((x, 0, z + 0.85), (0.08, 0.2, 1.2), "Blade", w, taper=(0.4, 0.4))
    elif kind == "staff":
        cx.mat("Staff", c2)
        cx.mat("Orb", c)
        b.loft([ring((x, 0, z - 0.9), 0.06, 0.06, w), ring((x, 0, z + 1.5), 0.07, 0.07, w)], "Staff", sides=5)
        b.blob((x, 0, z + 1.75), (0.17, 0.17, 0.17), "Orb", w, sides=6, rings=2)
    elif kind == "axe":
        cx.mat("Grip", c2)
        cx.mat("Blade", c)
        b.loft([ring((x, 0, z - 0.4), 0.05, 0.05, w), ring((x, 0, z + 0.9), 0.05, 0.05, w)], "Grip", sides=4, rot=math.pi / 4)
        b.box((x, -0.15, z + 0.8), (0.07, 0.4, 0.35), "Blade", w, taper=(1, 1))
    elif kind == "torch":
        cx.mat("Grip", c2)
        b.material("Flame", col(c), 0.5, 0.0, 2.0)
        b.loft([ring((x, 0, z - 0.2), 0.05, 0.05, w), ring((x, 0, z + 0.6), 0.06, 0.06, w)], "Grip", sides=5)
        b.cone((x, 0, z + 0.55), (x, 0, z + 1.1), 0.15, "Flame", w, sides=5)


# --------------------------------------------------------------------------- entry
def build_character(sp):
    """sp = merged spec -> Builder."""
    b = Builder("Body")
    cx = Ctx(b, sp)
    # keep material slot order stable and similar to the reference: skin first
    b.material("Skin", col(sp["skin"]))
    b.material("Face", col(sp.get("face_color", "eye")))
    build_body(cx)
    build_face(cx)
    build_ears(cx)
    build_snout(cx)
    build_beard(cx)
    build_hair(cx)
    build_hat(cx)
    build_extras(cx)
    return b
