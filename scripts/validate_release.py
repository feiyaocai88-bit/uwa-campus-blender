"""Validate a reopened publication file; write a JSON report and fail on errors.

blender -b UWA_Campus.blend -t 2 --python validate_release.py -- --output report.json
This checks packaging and presence, not architectural accuracy.
"""
import argparse
import json
from pathlib import Path
import sys

import bpy


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="publication_validation.json")
    args = parser.parse_args(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else [])
    scene = bpy.context.scene
    libraries = [{"name": x.name, "packed": bool(x.packed_file)} for x in bpy.data.libraries]
    images = [x for x in bpy.data.images if x.source == "FILE"]
    unpacked_images = [x.name for x in images if not (x.packed_file or x.packed_files)]
    external_fonts = [x.name for x in bpy.data.fonts if x.filepath != "<builtin>"]
    required = ["REID_01_Concrete_Frame", "AUD28_06_Winthrop_Sculptures",
                "MU24_Music_Entrances", "HF35_Hackett_Forecourt_PRIVATE", "CV14_Irwin_West_And_2024"]
    absent = [x for x in required if bpy.data.collections.get(x) is None]
    raw_paths = list(bpy.utils.blend_paths(absolute=False, packed=False))
    # Cleared provenance records of appended data may appear as empty strings.
    # They name no file and are not live resource dependencies.
    external_paths = sorted(set(path for path in raw_paths if path.strip()))
    checks = {
        "three_packed_libraries": len(libraries) == 3 and all(x["packed"] for x in libraries),
        "all_file_images_packed": bool(images) and not unpacked_images,
        "no_external_fonts": not external_fonts,
        "required_collections_present": not absent,
        "full_scene_object_count": len(scene.objects) >= 26264,
        "overview_camera": scene.camera is not None and scene.camera.name == "PUBLIC_Campus_Overview",
        "public_credit_text": bpy.data.texts.get("PUBLIC_CREDITS.md") is not None,
        "no_unpacked_file_dependencies": not external_paths,
    }
    result = {
        "file": Path(bpy.data.filepath).name,
        "blender": bpy.app.version_string,
        "source_revision": 25,
        "reopened_successfully": True,
        "all_passed": all(checks.values()),
        "checks": checks,
        "scene_objects": len(scene.objects),
        "data_objects": len(bpy.data.objects),
        "libraries": libraries,
        "file_images": len(images),
        "unpacked_images": unpacked_images,
        "external_fonts": external_fonts,
        "absent_collections": absent,
        "unpacked_file_dependencies": external_paths,
        "empty_provenance_entries_ignored": sum(not path.strip() for path in raw_paths),
        "scope": "Packaging and scene-presence checks only; not a survey or comprehensive intersection test.",
    }
    output = Path(args.output).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf8")
    print("PUBLICATION_VALIDATION", json.dumps(result), flush=True)
    if not result["all_passed"]:
        raise RuntimeError("Publication validation failed; inspect the JSON report")


if __name__ == "__main__":
    main()
