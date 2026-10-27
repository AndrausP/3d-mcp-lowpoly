"""MCP server: generate low-poly rigged characters / props through headless Blender.

Run:  python -m lowpoly_mcp.server      (stdio transport)
Env:  LOWPOLY_BLENDER  path to blender.exe
      LOWPOLY_REF_DIR  folder with the reference FBX pack (used for animations_from / analyze)
      LOWPOLY_OUT_DIR  default output folder
"""
import json
import os
import subprocess
import sys
import tempfile

from mcp.server.fastmcp import FastMCP, Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

BLENDER = os.environ.get("LOWPOLY_BLENDER", r"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe")
REF_DIR = os.environ.get("LOWPOLY_REF_DIR",
                         r"C:\Users\AndrausFelipeRibeiro\Downloads\FBX-20261027T125302Z-1-001\FBX")
OUT_DIR = os.environ.get("LOWPOLY_OUT_DIR", os.path.join(ROOT, "out"))
RUNNER = os.path.join(ROOT, "lowpoly_gen", "run_job.py")

mcp = FastMCP("lowpoly")

SPEC_HELP = """Character spec (all keys optional, merged over defaults):
  gender: male|female            skin: light|tan|brown|dark|pale|green|zombie|'#rrggbb'
  head_scale: 0.9..1.15
  torso: {color, sleeves: none|short|long, bare: bool}
  legs:  {color, length: long|shorts|skirt}
  boots / gloves / belt: colour or null
  hair:  {style: short|long|bob|ponytail|bun|spiky|mohawk|afro|fringe|bald, color}
  beard: {style: moustache|goatee|full|long, color}
  hat:   {type: wizard|witch|cowboy|chef|viking|helmet|soldier|tophat|hardhat|cap|bicorne|crown|knight|ninja|beanie,
          color, color2}
  face:  default|cute|angry|goblin|zombie|none       face_color: colour
  ears:  round|elf|goblin|pug|cow|cat|none           snout: pug|cow|beak|null
  extras: list of {type, color[, color2]} with type in
          cape|scarf|shoulder_pads|chest_armor|vest|backpack|tail|bones|sword|staff|axe|torch|glasses|eyepatch|horns|wounds
Colours: '#rrggbb', a palette name (red, navy, gold, hairbrown, skin_light ...) or linear [r,g,b]."""


def _blender(job, timeout=300):
    if not os.path.isfile(BLENDER):
        raise RuntimeError("Blender not found at %s (set LOWPOLY_BLENDER)" % BLENDER)
    with tempfile.TemporaryDirectory() as td:
        jp, rp = os.path.join(td, "job.json"), os.path.join(td, "result.json")
        with open(jp, "w", encoding="utf-8") as fh:
            json.dump(job, fh)
        proc = subprocess.run([BLENDER, "-b", "--factory-startup", "-P", RUNNER, "--", jp, rp],
                              stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=timeout)
        if not os.path.isfile(rp):
            raise RuntimeError("Blender produced no result.\n" + (proc.stderr or proc.stdout)[-2000:])
        with open(rp, "r", encoding="utf-8") as fh:
            res = json.load(fh)
    if not res.get("ok"):
        raise RuntimeError(res.get("error", "failed") + "\n" + res.get("trace", ""))
    return res["result"]


def _anim_path(animations_from):
    if not animations_from:
        return None
    p = animations_from
    if not os.path.isabs(p):
        p = os.path.join(REF_DIR, p if p.lower().endswith(".fbx") else p + ".fbx")
    if not os.path.isfile(p):
        raise RuntimeError("animation source not found: " + p)
    return p


def _reply(info, preview):
    summary = {k: v for k, v in info.items() if k != "spec"}
    out = [json.dumps(summary, indent=1)]
    png = info.get("files", {}).get("png")
    if preview and png and os.path.isfile(png):
        out.append(Image(path=png))
    return out


@mcp.tool()
def list_presets() -> str:
    """List character presets (recreations of the reference pack), props and the spec schema."""
    from lowpoly_gen import presets, props
    return json.dumps({
        "presets": presets.list_presets(),
        "note": "append _Male/_Female to any preset (e.g. Pirate_Female, Doctor_Male_Old)",
        "props": props.list_props(),
        "spec": SPEC_HELP,
    }, indent=1)


@mcp.tool()
def generate_character(spec: dict | None = None, preset: str | None = None, name: str | None = None,
                       formats: list[str] | None = None, animations_from: str | None = None,
                       animations: list[str] | None = None, view: str = "three_quarter",
                       out_dir: str | None = None, preview: bool = True):
    """Generate a rigged low-poly character (same 32-bone skeleton/proportions as the reference FBX pack).

    preset: optional base (see list_presets). spec: overrides / full custom spec (see list_presets for schema).
    formats: any of fbx, glb, obj, blend (default fbx+glb). animations_from: reference FBX name/path whose actions
    (Idle, Walk, Run, Punch, ...) are copied onto the new rig; animations filters which ones.
    view: three_quarter|front|side|back.  Returns stats, file paths and a preview image.
    """
    job = dict(kind="character", preset=preset, spec=spec, name=name, formats=formats or ["fbx", "glb"],
               animations_from=_anim_path(animations_from), animation_names=animations, view=view,
               out_dir=out_dir or OUT_DIR, preview=preview)
    return _reply(_blender(job), preview)


@mcp.tool()
def random_character(seed: int = 0, archetype: str | None = None, formats: list[str] | None = None,
                     animations_from: str | None = None, out_dir: str | None = None, preview: bool = True):
    """Random character from a seed (deterministic). archetype = optional preset base to force (e.g. 'Wizard')."""
    job = dict(kind="character", seed=seed, archetype=archetype, formats=formats or ["fbx", "glb"],
               animations_from=_anim_path(animations_from), out_dir=out_dir or OUT_DIR, preview=preview)
    return _reply(_blender(job), preview)


@mcp.tool()
def generate_prop(prop: str, params: dict | None = None, name: str | None = None,
                  formats: list[str] | None = None, out_dir: str | None = None, preview: bool = True):
    """Generate a static low-poly prop (tree_pine, tree_round, rock, bush, crate, barrel, house, sword, shield,
    mushroom, chest, fence, campfire). params = colour overrides, e.g. {"leaves": "#3a7d2c"}."""
    job = dict(kind="prop", prop=prop, params=params, name=name, formats=formats or ["fbx", "glb"],
               out_dir=out_dir or OUT_DIR, preview=preview)
    return _reply(_blender(job), preview)


@mcp.tool()
def analyze_model(path: str) -> str:
    """Inspect an FBX/GLB/OBJ (meshes, tri counts, bbox, material slots with z-range, bones, actions).
    Relative names resolve inside the reference pack folder."""
    if not os.path.isabs(path):
        path = os.path.join(REF_DIR, path if "." in os.path.basename(path) else path + ".fbx")
    return json.dumps(_blender(dict(kind="analyze", path=path)), indent=1)


if __name__ == "__main__":
    mcp.run()
