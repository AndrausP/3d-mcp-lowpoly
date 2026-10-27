# lowpoly-mcp

MCP server that generates rigged low-poly characters and props with headless Blender.
Built from an analysis of the 52 reference FBX files (Quaternius-style characters).

## What the reference models are (measured)
- 1 mesh `Body`, 1k–5k verts, flat-colour material slots (no textures / UVs), flat shading
- 1 armature `CharacterArmature`, 32 bones (19 deform), T-pose, Z up, front = -Y
- Chibi proportions: 3.77 tall incl. hat, head z 2.07..3.13 (45%), arm span 3.24
- Cow / Pug are the same humanoid rig with different head parts (ears, snout, horns, tail)
- 17 shared actions (Idle, Walk, Run, Punch, SwordSlash, ...) keyed on the same bone names

`data/skeleton.json` = exact rest pose of that rig. `lowpoly_gen/character.py` = those
proportions as code (lofted rings + boxes, rigid weights with 50/50 joint blends).

## Install
    pip install "mcp<2"
    claude mcp add lowpoly -- python -m lowpoly_mcp.server   (run from this folder, or set cwd/PYTHONPATH)

Env: `LOWPOLY_BLENDER`, `LOWPOLY_REF_DIR`, `LOWPOLY_OUT_DIR`.

## Tools
| tool | what |
|---|---|
| `list_presets` | 28 base presets (+ `_Male`/`_Female`), props, spec schema |
| `generate_character` | preset and/or custom spec -> FBX/GLB/OBJ/blend + preview PNG |
| `random_character` | seeded random character |
| `generate_prop` | tree_pine, tree_round, rock, bush, crate, barrel, house, sword, shield, mushroom, chest, fence, campfire |
| `analyze_model` | stats of any FBX/GLB/OBJ (how the reference was studied) |

`animations_from="Pirate_Male"` copies the reference actions onto the generated rig
(bone names/rest pose match), so Unity/Godot animation sets keep working.

`python selftest.py` runs everything end to end.
