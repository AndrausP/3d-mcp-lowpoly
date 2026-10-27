"""Summarise any FBX/GLB/OBJ: this is how the reference pack was studied."""
import os

import bpy


def run(job):
    path = job["path"]
    bpy.ops.wm.read_factory_settings(use_empty=True)
    ext = os.path.splitext(path)[1].lower()
    if ext == ".fbx":
        bpy.ops.import_scene.fbx(filepath=path)
    elif ext in (".glb", ".gltf"):
        bpy.ops.import_scene.gltf(filepath=path)
    elif ext == ".obj":
        bpy.ops.wm.obj_import(filepath=path)
    else:
        raise ValueError("unsupported file type " + ext)
    out = {"file": path, "meshes": [], "armatures": [], "actions": [a.name.split("|")[-1] for a in bpy.data.actions]}
    for o in bpy.data.objects:
        if o.type == "MESH":
            me = o.data
            xs = [v.co.x for v in me.vertices] or [0]
            ys = [v.co.y for v in me.vertices] or [0]
            zs = [v.co.z for v in me.vertices] or [0]
            mats = {}
            for p in me.polygons:
                m = me.materials[p.material_index] if p.material_index < len(me.materials) else None
                n = m.name if m else "?"
                d = mats.setdefault(n, {"faces": 0, "color": [round(x, 3) for x in (m.diffuse_color[:3] if m else (0, 0, 0))],
                                        "zmin": 9e9, "zmax": -9e9})
                d["faces"] += 1
                for vi in p.vertices:
                    z = me.vertices[vi].co.z
                    d["zmin"] = round(min(d["zmin"], z), 3)
                    d["zmax"] = round(max(d["zmax"], z), 3)
            out["meshes"].append({
                "name": o.name, "verts": len(me.vertices), "faces": len(me.polygons),
                "tris": sum(len(p.vertices) - 2 for p in me.polygons),
                "bbox_min": [round(min(xs), 3), round(min(ys), 3), round(min(zs), 3)],
                "bbox_max": [round(max(xs), 3), round(max(ys), 3), round(max(zs), 3)],
                "vertex_groups": [g.name for g in o.vertex_groups], "materials": mats,
                "uv_layers": [u.name for u in me.uv_layers], "modifiers": [m.type for m in o.modifiers]})
        elif o.type == "ARMATURE":
            out["armatures"].append({"name": o.name, "bones": [
                {"name": b.name, "parent": b.parent.name if b.parent else None,
                 "head": [round(v, 3) for v in b.head_local], "tail": [round(v, 3) for v in b.tail_local]}
                for b in o.data.bones]})
    return out
