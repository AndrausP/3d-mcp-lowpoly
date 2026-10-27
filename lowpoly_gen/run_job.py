"""Entry point executed by Blender:  blender -b --factory-startup -P run_job.py -- job.json result.json"""
import json
import os
import sys
import traceback

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

argv = sys.argv[sys.argv.index("--") + 1:]
job = json.load(open(argv[0], "r", encoding="utf-8"))
try:
    from lowpoly_gen import pipeline
    res = {"ok": True, "result": pipeline.run(job)}
except Exception as e:  # report instead of crashing the MCP call
    res = {"ok": False, "error": str(e), "trace": traceback.format_exc()}
json.dump(res, open(argv[1], "w", encoding="utf-8"), indent=1)
