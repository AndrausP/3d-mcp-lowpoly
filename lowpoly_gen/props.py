"""Small static props in the same flat-colour low-poly style."""
import math

from .builder import Builder
from .palettes import col


def _r(c, ru, rv=None, **kw):
    d = dict(c=c, ru=ru, rv=ru if rv is None else rv)
    d.update(kw)
    return d


def tree_pine(b, p):
    b.material("Trunk", col(p.get("trunk", "darkbrown")))
    b.material("Leaves", col(p.get("leaves", "green")))
    b.loft([_r((0, 0, 0), 0.22), _r((0, 0, 0.9), 0.18)], "Trunk", sides=6)
    for i in range(4):
        z = 0.7 + i * 0.85
        r = 1.35 - i * 0.28
        b.cone((0, 0, z), (0, 0, z + 1.35), r, "Leaves", sides=7)


def tree_round(b, p):
    b.material("Trunk", col(p.get("trunk", "brown")))
    b.material("Leaves", col(p.get("leaves", "green")))
    b.loft([_r((0, 0, 0), 0.28), _r((0, 0, 1.6), 0.2)], "Trunk", sides=6)
    b.blob((0, 0, 2.5), (1.1, 1.1, 1.0), "Leaves", sides=7, rings=3)
    b.blob((0.55, 0.2, 2.0), (0.65, 0.65, 0.55), "Leaves", sides=6, rings=2)
    b.blob((-0.5, -0.25, 2.1), (0.6, 0.6, 0.5), "Leaves", sides=6, rings=2)


def rock(b, p):
    b.material("Rock", col(p.get("color", "grey")))
    b.blob((0, 0, 0.35), (0.9, 0.7, 0.55), "Rock", sides=7, rings=3)
    b.blob((0.7, 0.2, 0.2), (0.45, 0.4, 0.3), "Rock", sides=6, rings=2)


def bush(b, p):
    b.material("Leaves", col(p.get("leaves", "green")))
    b.blob((0, 0, 0.4), (0.7, 0.6, 0.45), "Leaves", sides=7, rings=3)
    b.blob((0.5, 0.1, 0.3), (0.4, 0.4, 0.3), "Leaves", sides=6, rings=2)


def crate(b, p):
    b.material("Wood", col(p.get("color", "lightbrown")))
    b.material("Strap", col(p.get("strap", "darkbrown")))
    b.box((0, 0, 0.5), (1, 1, 1), "Wood")
    for s in (1, -1):
        b.box((s * 0.5, 0, 0.5), (0.08, 1.04, 1.04), "Strap")
    b.box((0, 0, 0.5), (1.04, 1.04, 0.08), "Strap")


def barrel(b, p):
    b.material("Wood", col(p.get("color", "lightbrown")))
    b.material("Ring", col(p.get("ring", "steel")))
    b.loft([_r((0, 0, 0), 0.4), _r((0, 0, 0.5), 0.52), _r((0, 0, 1.0), 0.4)], "Wood", sides=8)
    for z in (0.18, 0.82):
        b.loft([_r((0, 0, z - 0.04), 0.46 if z < 0.5 else 0.46), _r((0, 0, z + 0.04), 0.46)], "Ring", sides=8,
               caps=(False, False))


def house(b, p):
    b.material("Wall", col(p.get("wall", "cream")))
    b.material("Roof", col(p.get("roof", "red")))
    b.material("Door", col("darkbrown"))
    b.material("Window", col("wizardblue"))
    b.box((0, 0, 1.0), (3, 2.6, 2), "Wall")
    b.loft([_r((0, 0, 2.0), 2.3, 1.9), _r((0, 0, 3.1), 0.05, 0.05)], "Roof", sides=4, rot=math.pi / 4)
    b.box((0, -1.31, 0.7), (0.7, 0.06, 1.4), "Door")
    for s in (1, -1):
        b.box((s * 1.0, -1.31, 1.3), (0.5, 0.06, 0.5), "Window")
    b.box((0.9, 0.3, 3.0), (0.4, 0.4, 0.9), "Wall")


def sword(b, p):
    b.material("Blade", col(p.get("blade", "silver"))); b.material("Grip", col(p.get("grip", "brown")))
    b.material("Guard", col(p.get("guard", "gold")))
    b.box((0, 0, 0.15), (0.09, 0.09, 0.4), "Grip")
    b.box((0, 0, 0.38), (0.55, 0.12, 0.1), "Guard")
    b.box((0, 0, 1.35), (0.16, 0.05, 1.9), "Blade", taper=(0.2, 0.5))


def shield(b, p):
    b.material("Face", col(p.get("color", "red"))); b.material("Rim", col("gold"))
    b.loft([_r((0, 0, 0), 0.6, 0.12), _r((0, 0, 0.1), 0.52, 0.1)], "Face", sides=8)
    b.blob((0, -0.08, 0.05), (0.18, 0.12, 0.12), "Rim", sides=6, rings=2, axis=1)


def mushroom(b, p):
    b.material("Stem", col("cream")); b.material("Cap", col(p.get("color", "red")))
    b.loft([_r((0, 0, 0), 0.18), _r((0, 0, 0.5), 0.14)], "Stem", sides=6)
    b.blob((0, 0, 0.55), (0.55, 0.55, 0.38), "Cap", sides=8, rings=3)


def chest(b, p):
    b.material("Wood", col("lightbrown")); b.material("Metal", col("gold"))
    b.box((0, 0, 0.3), (1.2, 0.7, 0.6), "Wood")
    b.loft([_r((-0.6, 0, 0.6), 0.3, 0.35), _r((0.6, 0, 0.6), 0.3, 0.35)], "Wood", sides=6, rot=0)
    b.box((0, -0.36, 0.55), (0.14, 0.04, 0.2), "Metal")


def fence(b, p):
    b.material("Wood", col("lightbrown"))
    for i in range(5):
        b.box((i * 0.5 - 1.0, 0, 0.45), (0.14, 0.12, 0.9), "Wood", taper=(0.7, 0.7))
    for z in (0.3, 0.65):
        b.box((0, 0, z), (2.2, 0.08, 0.12), "Wood")


def campfire(b, p):
    b.material("Log", col("brown")); b.material("Stone", col("grey"))
    b.material("Fire", col("orange")); b.material("Fire2", col("yellow"))
    for k in range(6):
        a = 2 * math.pi * k / 6
        b.blob((math.cos(a) * 0.65, math.sin(a) * 0.65, 0.12), (0.2, 0.18, 0.14), "Stone", sides=5, rings=2)
    b.box((0, 0, 0.12), (0.9, 0.12, 0.12), "Log", rotz=0.5)
    b.box((0, 0, 0.12), (0.9, 0.12, 0.12), "Log", rotz=-0.5)
    b.cone((0, 0, 0.1), (0, 0, 0.9), 0.3, "Fire", sides=5)
    b.cone((0, 0, 0.1), (0.05, 0, 0.6), 0.18, "Fire2", sides=5)


PROPS = {f.__name__: f for f in (tree_pine, tree_round, rock, bush, crate, barrel, house, sword, shield, mushroom,
                                 chest, fence, campfire)}


def list_props():
    return sorted(PROPS)


def build_prop(name, params=None):
    if name not in PROPS:
        raise KeyError("unknown prop %r. Known: %s" % (name, ", ".join(list_props())))
    b = Builder(name)
    PROPS[name](b, params or {})
    return b
