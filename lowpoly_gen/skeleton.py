"""Armature identical to the reference pack (32 bones, T-pose, Z up, front = -Y)."""
import json
import os

import bpy
from mathutils import Vector

DATA = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")

DEFORM = ["Body", "Hips", "Abdomen", "Torso", "Neck", "Head",
          "Shoulder.L", "UpperArm.L", "LowerArm.L", "Fist.L",
          "Shoulder.R", "UpperArm.R", "LowerArm.R", "Fist.R",
          "UpperLeg.L", "LowerLeg.L", "UpperLeg.R", "LowerLeg.R",
          "Foot.L", "Foot.R"]


def load_skeleton():
    with open(os.path.join(DATA, "skeleton.json"), "r", encoding="utf-8") as fh:
        return json.load(fh)


def build_armature(name="CharacterArmature"):
    sk = load_skeleton()
    ad = bpy.data.armatures.new(name)
    ob = bpy.data.objects.new(name, ad)
    bpy.context.scene.collection.objects.link(ob)
    bpy.context.view_layer.objects.active = ob
    ob.select_set(True)
    bpy.ops.object.mode_set(mode="EDIT")
    eb = {}
    for b in sk["bones"]:
        e = ad.edit_bones.new(b["name"])
        e.head = Vector(b["head"])
        e.tail = Vector(b["tail"])
        e.roll = b["roll"]
        e.use_deform = b["name"] in DEFORM
        eb[b["name"]] = e
    for b in sk["bones"]:
        if b["parent"]:
            eb[b["name"]].parent = eb[b["parent"]]
    bpy.ops.object.mode_set(mode="OBJECT")
    ad.display_type = "OCTAHEDRAL"
    return ob


def bind(mesh_ob, arm_ob):
    mesh_ob.parent = arm_ob
    mod = mesh_ob.modifiers.new("Armature", "ARMATURE")
    mod.object = arm_ob
