"""Presets that recreate the 52 reference models (colours come from the FBX materials).

Each key is a base outfit; `<Base>_Male` / `<Base>_Female` / plain names resolve to it.
"""
import random

from .character import default_spec, merge
from .palettes import HAIR_POOL, SHIRT_POOL, PANTS_POOL, SKIN_POOL, pick

P = {}


def _p(name, **kw):
    P[name] = kw


_p("BaseCharacter", torso=dict(color="skin_light", bare=True, sleeves="none"), legs=dict(color="skin_light", length="shorts"),
   hair=None)
_p("Casual", torso=dict(color="blue", sleeves="short"), legs=dict(color="brown"), belt="brown",
   hair=dict(style="short", color="hairbrown"), boots="darkbrown")
_p("Casual_Bald", torso=dict(color=[0.184, 0.047, 0.156], sleeves="short"), legs=dict(color="brown"),
   belt="brown", hair=None)
_p("Casual2", torso=dict(color="purple", sleeves="short"), legs=dict(color="navy"), belt="brown",
   hair=dict(style="short", color="blonde"), boots="darkbrown")
_p("Casual3", torso=dict(color=[0.184, 0.181, 0.17], sleeves="long"), legs=dict(color=[0.071, 0.077, 0.029]),
   belt="brown", hair=dict(style="short", color="hairdark"), boots="black")
_p("Soldier", torso=dict(color="olive", sleeves="long"), legs=dict(color="olive"), boots="black", gloves="black",
   belt="black", hat=dict(type="soldier", color=[0.043, 0.07, 0.021]), extras=[dict(type="vest", color="darkgreen")])
_p("BlueSoldier", torso=dict(color="bluearmy", sleeves="long"), legs=dict(color="bluearmy"), boots="black",
   gloves="black", belt="black", hat=dict(type="soldier", color="bluearmy"), extras=[dict(type="vest", color="grey")])
_p("Chef", torso=dict(color="white", sleeves="long"), legs=dict(color=[0.334, 0.334, 0.334]), boots="black",
   belt=None, hair=dict(style="short", color="hairgrey"), extras=[dict(type="scarf", color="red")])
_p("Chef_Hat", torso=dict(color="white", sleeves="long"), legs=dict(color=[0.334, 0.334, 0.334]), boots="black",
   hat=dict(type="chef", color="cream", color2="red"), beard=dict(style="moustache", color="cream"), hair=None)
_p("Cowboy", torso=dict(color=[0.077, 0.04, 0.011], sleeves="long"), legs=dict(color="darkbrown"), boots="darkbrown",
   belt="lightbrown", hat=dict(type="cowboy", color="lightbrown", color2=[0.8, 0.376, 0.186]),
   hair=dict(style="short", color="lightbrown"),
   extras=[dict(type="scarf", color="red"), dict(type="vest", color=[0.227, 0.063, 0.014])])
_p("Cowboy_Hair", torso=dict(color=[0.077, 0.04, 0.011], sleeves="long"), legs=dict(color="darkbrown"), boots="darkbrown",
   hat=None, hair=dict(style="short", color=[0.107, 0.041, 0.007]),
   extras=[dict(type="scarf", color="red")])
_p("Doctor_Old", torso=dict(color="silver", sleeves="long"), legs=dict(color=[0.01, 0.031, 0.033]), boots="black",
   hair=dict(style="short", color="hairgrey"), extras=[dict(type="glasses", color="black")])
_p("Doctor_Young", torso=dict(color="silver", sleeves="long"), legs=dict(color=[0.01, 0.031, 0.033]), boots="black",
   hair=dict(style="short", color="hairbrown"), extras=[dict(type="glasses", color="black")])
_p("Elf", skin="pale", ears="elf", torso=dict(color="green", sleeves="short"), legs=dict(color="darkbrown"),
   belt="darkbrown", boots="darkbrown", hat=dict(type="beanie", color=[0.012, 0.042, 0.019]),
   hair=dict(style="long", color="blonde"))
_p("Goblin", skin="green", ears="goblin", face="goblin", torso=dict(color=[0.26, 0.229, 0.182], sleeves="none"),
   legs=dict(color=[0.111, 0.078, 0.031], length="shorts"), hair=None, nose=True, head_scale=1.05)
_p("Kimono", torso=dict(color="white", sleeves="long"), legs=dict(color="white", length="skirt"), belt="red",
   boots="darkbrown", hair=dict(style="bun", color="black"))
_p("Knight_Golden", skin="light", torso=dict(color="darkgrey", sleeves="long"), legs=dict(color="darkgrey"),
   boots="goldarmor", gloves="goldarmor", hat=dict(type="knight", color="goldarmor", color2="darkred"), hair=None,
   extras=[dict(type="chest_armor", color="goldarmor"), dict(type="shoulder_pads", color="goldarmor")])
_p("Knight", skin="light", torso=dict(color="darkgrey", sleeves="long"), legs=dict(color="darkgrey"),
   boots="steel", gloves="steel", hat=dict(type="knight", color="steel", color2="darkred"), hair=None,
   extras=[dict(type="chest_armor", color="steel"), dict(type="shoulder_pads", color="steel")])
_p("Ninja", torso=dict(color=[0.008, 0.008, 0.008], sleeves="long"), legs=dict(color=[0.008, 0.008, 0.008]),
   boots="grey", gloves="grey", belt=[0.058, 0.01, 0.054], hat=dict(type="ninja", color=[0.008, 0.008, 0.008]), hair=None)
_p("Ninja_Sand", torso=dict(color="sand", sleeves="long"), legs=dict(color="sand"), boots=[0.319, 0.212, 0.073],
   gloves=[0.319, 0.212, 0.073], belt=[0.058, 0.003, 0.038], hat=dict(type="ninja", color="sand"), hair=None)
_p("OldClassy", torso=dict(color=[0.638, 0.638, 0.638], sleeves="long"), legs=dict(color=[0.209, 0.205, 0.112]),
   belt=[0.084, 0.035, 0.014], boots="darkbrown", hat=dict(type="tophat", color=[0.007, 0.007, 0.005], color2="red"),
   hair=dict(style="short", color="hairgrey"), beard=dict(style="moustache", color="hairgrey"),
   extras=[dict(type="vest", color=[0.274, 0.107, 0.037])])
_p("Pirate", torso=dict(color="tan", sleeves="long"), legs=dict(color="navy"), boots="darkbrown",
   belt="brown", hat=dict(type="bicorne", color="black", color2="gold"), hair=dict(style="long", color=[0.212, 0.12, 0.032]),
   beard=dict(style="full", color=[0.212, 0.12, 0.032]),
   extras=[dict(type="vest", color="navy"), dict(type="eyepatch", color="black"), dict(type="sword", color="steel", color2="brown")])
_p("Pug", ears="pug", ear_color="darkbrown", snout="pug", face="default", nose=False, skin="beige",
   torso=dict(color="white", sleeves="short"), legs=dict(color="cowblack"), belt="cowblack", boots="cowblack",
   hair=None, head_scale=0.95, extras=[dict(type="tail", color="beige")])
_p("Cow", ears="cow", ear_color="cowblack", snout="cow", skin="white", nose=False,
   torso=dict(color="white", sleeves="short"), legs=dict(color="cowblack"), belt="cowblack", boots="cowblack",
   hair=None, extras=[dict(type="horns", color="cream"), dict(type="tail", color="white")])
_p("Suit", torso=dict(color="cowblack", sleeves="long"), legs=dict(color="cowblack"), boots="black", gloves=None,
   hair=dict(style="short", color="hairbrown"), belt="cowblack",
   extras=[dict(type="vest", color=[0.615, 0.615, 0.615])])
_p("Viking", torso=dict(color=[0.058, 0.028, 0.022], sleeves="short"), legs=dict(color=[0.025, 0.013, 0.01]),
   boots="brown", belt="lightbrown", hair=dict(style="long", color=[0.147, 0.036, 0.015]),
   beard=dict(style="full", color=[0.147, 0.036, 0.015]), extras=[dict(type="vest", color=[0.538, 0.408, 0.283])])
_p("VikingHelmet", torso=dict(color=[0.058, 0.028, 0.022], sleeves="short"), legs=dict(color=[0.025, 0.013, 0.01]),
   boots="brown", belt="lightbrown", hair=dict(style="short", color=[0.147, 0.036, 0.015]),
   hat=dict(type="viking", color="steel"), beard=dict(style="full", color=[0.147, 0.036, 0.015]),
   extras=[dict(type="vest", color=[0.538, 0.408, 0.283])])
_p("Witch", ears="elf", torso=dict(color="witchpurple", sleeves="long"), legs=dict(color="witchpurple", length="skirt"),
   belt="darkbrown", boots="black", hat=dict(type="witch", color=[0.012, 0.018, 0.042], color2=[0.007, 0.003, 0.017]),
   hair=dict(style="long", color="hairwhite"), extras=[dict(type="staff", color="green", color2="darkbrown")])
_p("Wizard", ears="round", torso=dict(color="wizardblue", sleeves="long"), legs=dict(color="wizardblue", length="skirt"),
   belt="darkbrown", boots="darkbrown", hat=dict(type="wizard", color=[0.007, 0.019, 0.042], color2="gold"),
   hair=dict(style="long", color="hairwhite"), beard=dict(style="long", color="hairwhite"),
   extras=[dict(type="staff", color="gold", color2="darkbrown")])
_p("Worker", torso=dict(color=[0.402, 0.448, 0.404], sleeves="long"), legs=dict(color=[0.047, 0.099, 0.163]),
   boots="darkbrown", gloves="orange", belt="brown", hat=dict(type="hardhat", color=[0.367, 0.319, 0.051]),
   hair=dict(style="short", color="hairdark"), extras=[dict(type="vest", color="orange")])
_p("Zombie", skin="zombie", face="zombie", torso=dict(color=[0.087, 0.058, 0.202], sleeves="short"),
   legs=dict(color=[0.334, 0.292, 0.167], length="long"), boots=None, ears="round",
   hair=dict(style="short", color=[0.044, 0.018, 0.007]),
   extras=[dict(type="wounds", color="red"), dict(type="bones", color="bone")])

FEMALE_HAIR = {"Casual": "long", "Casual2": "ponytail", "Casual3": "bob", "Soldier": "ponytail", "BlueSoldier": "ponytail",
               "Chef": "bun", "Cowboy": "long", "Doctor_Old": "bob", "Doctor_Young": "ponytail", "Goblin": "long",
               "Kimono": "bun", "Knight_Golden": "ponytail", "Ninja": "ponytail", "Ninja_Sand": "ponytail",
               "OldClassy": "bun", "Pirate": "long", "Suit": "ponytail", "Viking": "long", "Worker": "ponytail",
               "Zombie": "long"}

ALIASES = {"Casual_Female": "Casual", "Casual_Male": "Casual", "Doctor_Female_Old": "Doctor_Old",
           "Doctor_Female_Young": "Doctor_Young", "Doctor_Male_Old": "Doctor_Old",
           "Doctor_Male_Young": "Doctor_Young", "Ninja_Male": "Ninja", "Ninja_Male_Hair": "Ninja",
           "Ninja_Sand_Female": "Ninja_Sand", "Knight_Golden_Male": "Knight_Golden",
           "Knight_Golden_Female": "Knight_Golden", "Knight_Male": "Knight"}


def list_presets():
    return sorted(P.keys())


def preset_spec(name):
    """'Pirate_Female', 'Wizard', 'Casual2_Male' ... -> spec dict."""
    gender = "female" if name.endswith("_Female") else "male"
    base = ALIASES.get(name, name)
    for suf in ("_Male", "_Female"):
        if base.endswith(suf):
            base = base[: -len(suf)]
    if base not in P:
        raise KeyError("unknown preset %r. Known: %s" % (name, ", ".join(list_presets())))
    sp = merge(default_spec(), P[base])
    sp["name"] = name
    sp["gender"] = gender
    if gender == "female" and base in FEMALE_HAIR and sp.get("hair"):
        sp["hair"] = dict(sp["hair"], style=FEMALE_HAIR[base])
    if gender == "female":
        sp["beard"] = None
    return sp


def random_spec(seed=0, archetype=None):
    rng = random.Random(seed)
    sp = default_spec()
    sp["gender"] = rng.choice(["male", "female"])
    sp["skin"] = pick(rng, SKIN_POOL)
    sp["torso"] = dict(color=pick(rng, SHIRT_POOL), sleeves=rng.choice(["short", "long", "long", "none"]))
    sp["legs"] = dict(color=pick(rng, PANTS_POOL), length=rng.choice(["long", "long", "shorts", "skirt"])
                      if sp["gender"] == "female" else rng.choice(["long", "long", "shorts"]))
    sp["boots"] = rng.choice([None, "darkbrown", "black", "brown"])
    sp["belt"] = rng.choice([None, "brown", "black"])
    styles = ["short", "long", "bob", "ponytail", "bun", "spiky", "mohawk", "afro", "bald"]
    sp["hair"] = dict(style=rng.choice(styles), color=pick(rng, HAIR_POOL))
    sp["face"] = rng.choice(["default", "default", "cute", "angry"])
    sp["head_scale"] = round(rng.uniform(0.92, 1.1), 2)
    if rng.random() < 0.35:
        sp["hat"] = dict(type=rng.choice(["cowboy", "tophat", "hardhat", "beanie", "cap", "chef", "crown"]),
                         color=pick(rng, SHIRT_POOL + ["brown", "black"]), color2="gold")
    if sp["gender"] == "male" and rng.random() < 0.3:
        sp["beard"] = dict(style=rng.choice(["moustache", "goatee", "full"]), color=sp["hair"]["color"])
    ex = []
    if rng.random() < 0.25:
        ex.append(dict(type="cape", color=pick(rng, SHIRT_POOL)))
    if rng.random() < 0.2:
        ex.append(dict(type="backpack", color="brown"))
    if rng.random() < 0.2:
        ex.append(dict(type="scarf", color=pick(rng, SHIRT_POOL)))
    if rng.random() < 0.15:
        ex.append(dict(type="glasses", color="black"))
    sp["extras"] = ex
    if archetype:
        sp = merge(sp, P.get(archetype, {}))
    sp["name"] = "Random_%d" % seed
    return sp
