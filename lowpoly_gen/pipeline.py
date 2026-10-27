"""bpy-side job runner: build -> (anim) -> export -> preview."""
import json
import math
import os

import bpy
from mathutils import Vector

from . import skeleton, presets
from .character import build_character, default_spec, merge
from .props import build_prop


def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)


def attach_animations(arm, ref_fbx, only=None):
    """Copy every action from a reference FBX onto our (bone-name compatible) armature."""
    before = set(bpy.data.objects)
    bpy.ops.import_scene.fbx(filepath=ref_fbx)
    new = [o for o in bpy.data.objects if o not in before]
    acts = [a for a in bpy.data.actions]
    for o in new:
        bpy.data.objects.remove(o, do_unlink=True)
    ad = arm.animation_data_create()
    names = []
    for a in acts:
        short = a.name.split("|")[-1]
        if only and short not in only:
            bpy.data.actions.remove(a)
            continue
        a.name = short
        a.use_fake_user = True
        slot = None
        try:
            ad.action = a
            slot = ad.action_slot
            if slot is None and len(a.slots):
                ad.action_slot = a.slots[0]
                slot = a.slots[0]
        except Exception:
            pass
        tr = ad.nla_tracks.new()
        tr.name = short
        st = tr.strips.new(short, int(a.frame_range[0]), a)
        try:
            if slot is not None:
                st.action_slot = slot
        except Exception:
            pass
        names.append(short)
    ad.action = None
    return names


def build_preview(out_png, ob_list, size=(640, 800), view="three_quarter"):
    sc = bpy.context.scene
    sc.render.engine = "BLENDER_WORKBENCH"
    sc.render.resolution_x, sc.render.resolution_y = size
    sc.render.film_transparent = False
    sh = sc.display.shading
    sh.light = "STUDIO"
    sh.color_type = "MATERIAL"
    sh.show_cavity = False
    sh.show_shadows = False
    sh.show_object_outline = True
    sh.object_outline_color = (0.0, 0.0, 0.0)
    try:
        sc.world = bpy.data.worlds.new("w")
        sc.world.color = (0.62, 0.72, 0.82)
    except Exception:
        pass
    # bbox of meshes
    mn = Vector((9e9, 9e9, 9e9)); mx = Vector((-9e9, -9e9, -9e9))
    for o in ob_list:
        if o.type != "MESH":
            continue
        for v in o.data.vertices:
            for i in range(3):
                mn[i] = min(mn[i], v.co[i]); mx[i] = max(mx[i], v.co[i])
    ctr = (mn + mx) / 2
    ext = max((mx - mn).x, (mx - mn).y, (mx - mn).z)
    cam = bpy.data.cameras.new("cam")
    cam.type = "ORTHO"
    cam.ortho_scale = ext * 1.25
    co = bpy.data.objects.new("cam", cam)
    sc.collection.objects.link(co)
    ang = {"three_quarter": 35.0, "front": 0.0, "side": 90.0, "back": 180.0}.get(view, 35.0)
    d = ext * 3
    a = math.radians(ang)
    co.location = ctr + Vector((math.sin(a) * d, -math.cos(a) * d, d * 0.35))
    direction = ctr - co.location
    co.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
    sc.camera = co
    sc.render.filepath = out_png
    sc.render.image_settings.file_format = "PNG"
    bpy.ops.render.render(write_still=True)
    return out_png


def export_all(out_dir, name, formats, has_anim, objs):
    paths = {}
    bpy.ops.object.select_all(action="DESELECT")
    for o in objs:
        o.select_set(True)
    for fmt in formats:
        fmt = fmt.lower()
        fp = os.path.join(out_dir, name + "." + fmt)
        if fmt == "fbx":
            bpy.ops.export_scene.fbx(
                filepath=fp, use_selection=True, object_types={"ARMATURE", "MESH"}, add_leaf_bones=False,
                bake_anim=has_anim, bake_anim_use_all_actions=has_anim, bake_anim_use_nla_strips=False,
                bake_anim_force_startend_keying=True, mesh_smooth_type="FACE", axis_forward="-Z", axis_up="Y")
        elif fmt in ("glb", "gltf"):
            bpy.ops.export_scene.gltf(filepath=fp, export_format="GLB" if fmt == "glb" else "GLTF_SEPARATE",
                                      use_selection=True, export_animations=has_anim)
        elif fmt == "obj":
            bpy.ops.wm.obj_export(filepath=fp, export_selected_objects=True)
        elif fmt == "blend":
            bpy.ops.wm.save_as_mainfile(filepath=fp)
        else:
            raise ValueError("unsupported format " + fmt)
        paths[fmt] = fp
    return paths


def run(job):
    if job.get("kind") == "analyze":
        from . import analyze
        return analyze.run(job)
    os.makedirs(job["out_dir"], exist_ok=True)
    reset()
    kind = job.get("kind", "character")
    objs, info = [], {}
    has_anim = False
    if kind == "character":
        if job.get("preset"):
            sp = presets.preset_spec(job["preset"])
        elif job.get("seed") is not None and not job.get("spec"):
            sp = presets.random_spec(int(job["seed"]), job.get("archetype"))
        else:
            sp = merge(default_spec(), job.get("spec") or {})
        if job.get("spec") and job.get("preset"):
            sp = merge(sp, job["spec"])
        if job.get("name"):
            sp["name"] = job["name"]
        name = sp["name"]
        bld = build_character(sp)
        mesh = bld.build()
        arm = skeleton.build_armature("CharacterArmature")
        skeleton.bind(mesh, arm)
        objs = [mesh, arm]
        if job.get("animations_from"):
            names = attach_animations(arm, job["animations_from"], job.get("animation_names"))
            has_anim = bool(names)
            info["animations"] = names
        info["spec"] = sp
        info["materials"] = bld.mat_names
    elif kind == "prop":
        name = job.get("name") or job["prop"]
        bld = build_prop(job["prop"], job.get("params"))
        mesh = bld.build()
        objs = [mesh]
        info["materials"] = bld.mat_names
    else:
        raise ValueError("unknown kind " + kind)
    me = objs[0].data
    info.update(name=name, vertices=len(me.vertices), faces=len(me.polygons),
                triangles=sum(len(p.vertices) - 2 for p in me.polygons))
    files = {}
    if job.get("formats"):
        files = export_all(job["out_dir"], name, job["formats"], has_anim, objs)
    if job.get("preview", True):
        png = os.path.join(job["out_dir"], name + ".png")
        build_preview(png, objs, view=job.get("view", "three_quarter"))
        files["png"] = png
    info["files"] = files
    return info
