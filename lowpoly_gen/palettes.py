"""Colour helpers + palettes harvested from the reference pack."""
import random


def srgb(hexstr):
    """'#rrggbb' -> linear rgb tuple (what Blender stores)."""
    h = hexstr.lstrip("#")
    out = []
    for i in (0, 2, 4):
        c = int(h[i:i + 2], 16) / 255.0
        out.append(c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4)
    return tuple(round(v, 4) for v in out)


def col(v, default=(0.5, 0.5, 0.5)):
    """Accepts '#rrggbb', a palette key, or a linear [r,g,b] list."""
    if v is None:
        return default
    if isinstance(v, str):
        if v.startswith("#"):
            return srgb(v)
        if v in SKIN:
            return SKIN[v]
        if v in NAMED:
            return NAMED[v]
        raise ValueError("unknown colour %r" % v)
    return tuple(v)[:3]


SKIN = {
    "light": srgb("#f1c6a2"),
    "tan": srgb("#d9a066"),
    "brown": srgb("#a8693f"),
    "dark": srgb("#6f4328"),
    "pale": srgb("#f7dccb"),
    "green": (0.10, 0.111, 0.024),     # Goblin_* in the pack
    "zombie": (0.042, 0.077, 0.035),   # Zombie_* in the pack
}

# values copied from the reference materials (linear)
NAMED = {
    **{"skin_" + k: v for k, v in SKIN.items()},
    "black": (0.015, 0.015, 0.015), "white": (0.56, 0.56, 0.56), "cream": (0.911, 0.905, 0.815),
    "grey": (0.07, 0.07, 0.07), "darkgrey": (0.03, 0.03, 0.03), "silver": (0.429, 0.429, 0.429),
    "red": (0.233, 0.036, 0.021), "darkred": (0.128, 0.014, 0.011), "pink": (0.8, 0.176, 0.217),
    "brown": (0.099, 0.045, 0.022), "darkbrown": (0.047, 0.015, 0.007), "lightbrown": (0.227, 0.1, 0.045),
    "tan": (0.487, 0.447, 0.339), "beige": (0.799, 0.604, 0.337),
    "gold": (0.342, 0.183, 0.034), "goldarmor": (0.26, 0.201, 0.028), "bone": (0.342, 0.3, 0.211),
    "navy": (0.014, 0.02, 0.044), "blue": (0.068, 0.106, 0.184), "bluearmy": (0.023, 0.037, 0.07),
    "purple": (0.112, 0.096, 0.184), "wizardblue": (0.02, 0.055, 0.111), "witchpurple": (0.02, 0.021, 0.067),
    "green": (0.035, 0.111, 0.021), "olive": (0.063, 0.091, 0.041), "darkgreen": (0.032, 0.042, 0.012),
    "yellow": (0.367, 0.319, 0.051), "orange": (0.19, 0.09, 0.039), "teal": (0.067, 0.212, 0.191),
    "sand": (0.202, 0.161, 0.07), "horn": (0.411, 0.352, 0.228), "steel": (0.07, 0.07, 0.07),
    "blonde": (0.26, 0.18, 0.056), "ginger": (0.212, 0.051, 0.047), "hairbrown": (0.107, 0.048, 0.023),
    "hairdark": (0.05, 0.032, 0.012), "hairgrey": (0.332, 0.332, 0.332), "hairwhite": (0.638, 0.638, 0.638),
    "eye": (0.02, 0.02, 0.019), "teeth": (0.26, 0.256, 0.128), "cowblack": (0.006, 0.006, 0.006),
}

HAIR_POOL = ["blonde", "ginger", "hairbrown", "hairdark", "hairgrey", "black", "teal"]
SHIRT_POOL = ["red", "blue", "purple", "green", "orange", "yellow", "white", "teal", "olive", "pink", "navy"]
PANTS_POOL = ["navy", "darkbrown", "olive", "darkgrey", "tan", "blue", "brown"]
SKIN_POOL = ["light", "tan", "brown", "dark", "pale"]


def pick(rng, pool):
    return pool[rng.randrange(len(pool))]
