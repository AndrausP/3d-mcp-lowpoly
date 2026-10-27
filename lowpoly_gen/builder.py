"""Low-poly mesh builder.

Every shape in the reference pack (Quaternius-style characters) is made of a few
primitives: lofted rings (tube / cone / sphere), boxes, flat colour materials and
rigid-ish bone weights.  `Builder` collects those primitives into one mesh with
material slots and vertex groups, exactly like the reference "Body" object.
"""
import math

import bpy
import bmesh
from mathutils import Vector


def _frame(d, ref=None):
    """Orthonormal (u, v) so that u x v = d."""
    d = Vector(d).normalized()
    if ref is None:
        ref = Vector((0, 1, 0))
        if abs(d.dot(ref)) > 0.9:
            ref = Vector((1, 0, 0))
    u = ref.cross(d).normalized()
    v = d.cross(u).normalized()
    return u, v


def _norm_weights(w):
    if w is None:
        return {}
    if isinstance(w, str):
        return {w: 1.0}
    return dict(w)


class Builder:
    def __init__(self, name="Body"):
        self.name = name
        self.verts = []
        self.vweights = []
        self.faces = []
        self.fmat = []
        self.mat_names = []
        self.mat_colors = {}
        self.mat_props = {}

    # ---------------------------------------------------------------- materials
    def material(self, name, color=None, rough=0.69, metal=0.0, emit=0.0):
        if name not in self.mat_names:
            self.mat_names.append(name)
        if color is not None:
            self.mat_colors[name] = tuple(color)[:3]
        self.mat_props.setdefault(name, (rough, metal, emit))
        return self.mat_names.index(name)

    # ---------------------------------------------------------------- raw
    def vert(self, co, weights=None):
        self.verts.append(tuple(co))
        self.vweights.append(_norm_weights(weights))
        return len(self.verts) - 1

    def face(self, idx, mat):
        self.faces.append(tuple(idx))
        self.fmat.append(self.material(mat) if isinstance(mat, str) else mat)

    # ---------------------------------------------------------------- tube / loft
    def loft(self, rings, mat, sides=6, rot=0.0, caps=(True, True), ref=None,
             ring_mats=None, flat_cap=True, sq=1.0):
        """Loft elliptical rings.

        rings: list of dict(c=(x,y,z), ru=, rv=, w=bone|{bone:w})
               direction is derived from consecutive centres.
        mat:   material name (or ring_mats = one material name per segment).
        rot:   angular offset of the first vertex (pi/sides => flat sided prisms).
        """
        n = len(rings)
        if n < 2:
            raise ValueError("loft needs >= 2 rings")
        cs = [Vector(r["c"]) for r in rings]
        ds = []
        for i in range(n):
            a = cs[max(i - 1, 0)]
            b = cs[min(i + 1, n - 1)]
            ds.append((b - a).normalized())
        base = len(self.verts)
        for i, r in enumerate(rings):
            u, v = _frame(ds[i], ref)
            ru, rv = r["ru"], r.get("rv", r["ru"])
            for j in range(sides):
                a = rot + 2 * math.pi * j / sides
                ca, sa = math.cos(a), math.sin(a)
                q = r.get("sq", sq)
                if q != 1.0:   # squircle: push the ring towards a rounded box
                    ca = math.copysign(abs(ca) ** q, ca)
                    sa = math.copysign(abs(sa) ** q, sa)
                p = cs[i] + u * (ca * ru) + v * (sa * rv)
                self.vert(p, r.get("w"))
        for i in range(n - 1):
            m = ring_mats[i] if ring_mats else mat
            for j in range(sides):
                j2 = (j + 1) % sides
                self.face((base + i * sides + j, base + i * sides + j2,
                           base + (i + 1) * sides + j2, base + (i + 1) * sides + j), m)
        first_mat = ring_mats[0] if ring_mats else mat
        last_mat = ring_mats[-1] if ring_mats else mat
        if caps[0]:
            idx = [base + j for j in reversed(range(sides))]
            self.face(idx, first_mat)
        if caps[1]:
            idx = [base + (n - 1) * sides + j for j in range(sides)]
            self.face(idx, last_mat)

    def tube(self, a, b, r0, r1, mat, w=None, sides=6, rot=0.0, caps=(True, True), rv_scale=1.0):
        self.loft([dict(c=a, ru=r0, rv=r0 * rv_scale, w=w), dict(c=b, ru=r1, rv=r1 * rv_scale, w=w)],
                  mat, sides=sides, rot=rot, caps=caps)

    def cone(self, base_c, tip, r, mat, w=None, sides=6, rot=0.0, rv_scale=1.0):
        base_c, tip = Vector(base_c), Vector(tip)
        self.loft([dict(c=base_c, ru=r, rv=r * rv_scale, w=w),
                   dict(c=tip, ru=0.0001, rv=0.0001, w=w)], mat, sides=sides, rot=rot,
                  caps=(True, False))

    def blob(self, c, radii, mat, w=None, sides=6, rings=3, axis=2, rot=0.0):
        """Low-poly ellipsoid.  radii=(rx,ry,rz); axis = pole axis (0,1,2)."""
        c = Vector(c)
        rx, ry, rz = radii
        out = []
        # pole axis along z in local; remap after
        for k in range(rings + 1):
            t = -math.pi / 2 + math.pi * k / rings
            out.append((math.sin(t), max(math.cos(t), 0.0001)))
        base = len(self.verts)
        ids = []
        for k, (s, cr) in enumerate(out):
            if k in (0, len(out) - 1):
                p = Vector((0, 0, s))
                ids.append([self.vert(self._remap(p, c, radii, axis), w)])
            else:
                row = []
                for j in range(sides):
                    a = rot + 2 * math.pi * j / sides
                    p = Vector((math.cos(a) * cr, math.sin(a) * cr, s))
                    row.append(self.vert(self._remap(p, c, radii, axis), w))
                ids.append(row)
        # bottom fan
        for j in range(sides):
            self.face((ids[0][0], ids[1][(j + 1) % sides], ids[1][j]), mat)
        for k in range(1, len(ids) - 2):
            for j in range(sides):
                j2 = (j + 1) % sides
                self.face((ids[k][j], ids[k][j2], ids[k + 1][j2], ids[k + 1][j]), mat)
        for j in range(sides):
            self.face((ids[-1][0], ids[-2][j], ids[-2][(j + 1) % sides]), mat)

    @staticmethod
    def _remap(p, c, radii, axis):
        rx, ry, rz = radii
        if axis == 2:
            q = Vector((p.x * rx, p.y * ry, p.z * rz))
        elif axis == 0:   # poles on x
            q = Vector((p.z * rx, p.x * ry, p.y * rz))
        else:             # poles on y
            q = Vector((p.x * rx, p.z * ry, p.y * rz))
        return c + q

    # ---------------------------------------------------------------- box
    def box(self, c, size, mat, w=None, taper=(1.0, 1.0), rotz=0.0, rotx=0.0, roty=0.0):
        """Axis-aligned box (optionally rotated about its centre).

        taper = (top_scale_x, top_scale_y) scales the +z face.  size is full extent.
        """
        c = Vector(c)
        sx, sy, sz = (s / 2 for s in size)
        pts = []
        for zi, z in enumerate((-sz, sz)):
            tx, ty = (1.0, 1.0) if zi == 0 else taper
            for (x, y) in ((-sx, -sy), (sx, -sy), (sx, sy), (-sx, sy)):
                pts.append(Vector((x * tx, y * ty, z)))
        from mathutils import Euler
        e = Euler((rotx, roty, rotz), "XYZ").to_matrix()
        base = len(self.verts)
        for p in pts:
            self.vert(c + e @ p, w)
        q = [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
        for f in q:
            self.face([base + i for i in f], mat)

    def disc_ring(self, c, r_in, r_out, thick, mat, w=None, sides=10, dip=0.0, rot=0.0):
        """Flat brim: a short cylinder with a hole-less cap (brim shape)."""
        c = Vector(c)
        self.loft([dict(c=c + Vector((0, 0, -thick / 2)), ru=r_out, rv=r_out * 0.92, w=w),
                   dict(c=c + Vector((0, 0, thick / 2 + dip)), ru=r_in, rv=r_in, w=w)],
                  mat, sides=sides, rot=rot)

    # ---------------------------------------------------------------- bake to bpy
    def build(self, collection=None, smooth=False):
        me = bpy.data.meshes.new(self.name)
        me.from_pydata(self.verts, [], self.faces)
        me.update()
        for name in self.mat_names:
            m = bpy.data.materials.new(name)
            col = self.mat_colors.get(name, (0.5, 0.5, 0.5))
            rough, metal, emit = self.mat_props.get(name, (0.69, 0.0, 0.0))
            m.diffuse_color = (*col, 1.0)
            m.use_nodes = True
            bsdf = m.node_tree.nodes.get("Principled BSDF")
            if bsdf:
                bsdf.inputs["Base Color"].default_value = (*col, 1.0)
                bsdf.inputs["Roughness"].default_value = rough
                bsdf.inputs["Metallic"].default_value = metal
                if emit > 0:
                    for key in ("Emission Color", "Emission"):
                        if key in bsdf.inputs:
                            bsdf.inputs[key].default_value = (*col, 1.0)
                            break
                    if "Emission Strength" in bsdf.inputs:
                        bsdf.inputs["Emission Strength"].default_value = emit
            me.materials.append(m)
        for pi, mi in enumerate(self.fmat):
            me.polygons[pi].material_index = mi
            me.polygons[pi].use_smooth = smooth
        # outward normals per island
        bm = bmesh.new()
        bm.from_mesh(me)
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
        bm.to_mesh(me)
        bm.free()
        me.update()
        ob = bpy.data.objects.new(self.name, me)
        (collection or bpy.context.scene.collection).objects.link(ob)
        # weights
        groups = {}
        for vi, w in enumerate(self.vweights):
            for bn, val in w.items():
                if val <= 0:
                    continue
                g = groups.get(bn)
                if g is None:
                    g = groups[bn] = ob.vertex_groups.new(name=bn)
                g.add([vi], val, "REPLACE")
        return ob
