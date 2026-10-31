"""Render the published scene without saving changes to its geometry or lighting.

blender -b UWA_Campus.blend -t 2 --python render_gallery.py -- --output images
Use --views hero_overview,winthrop to render only selected views.
"""
import argparse
import math
from pathlib import Path
import sys

import bpy
from mathutils import Vector


VIEWS = {
    "hero_overview": "PUBLIC_Campus_Overview",
    "winthrop": "AUD28_Review_Winthrop",
    "reid": "RL_Hero_Northeast",
    "ezone": "CAMPUS_19_EZONE_West_Streetview",
    "sunken_garden": "AUD28_Review_Sunken_Garden",
    "socrates": "AUD28_Review_Socrates",
    "diotima": "AUD28_Review_Diotima",
}


def overview_camera(scene):
    camera = bpy.data.objects.get("PUBLIC_Campus_Overview")
    if camera is None:
        data = bpy.data.cameras.new("PUBLIC_Campus_Overview")
        camera = bpy.data.objects.new(data.name, data)
        scene.collection.objects.link(camera)
    target = Vector((65, -230, 0))
    camera.location = target + Vector((1000, -1270, 1100))
    camera.rotation_euler = (target - camera.location).to_track_quat("-Z", "Y").to_euler()
    camera.data.type = "ORTHO"
    camera.data.ortho_scale = 1440
    camera.data.clip_end = 5000
    return camera


def setup_lighting(scene, samples):
    for obj in scene.objects:
        if obj.type == "LIGHT" and obj.library is None:
            obj.hide_render = True
    world = bpy.data.worlds.new("PUBLIC_Gallery_World")
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs[0].default_value = (0.72, 0.80, 0.90, 1)
    world.node_tree.nodes["Background"].inputs[1].default_value = 0.7
    scene.world = world
    light = bpy.data.lights.new("PUBLIC_Gallery_Sun", "SUN")
    light.energy = 2.5
    light.angle = 0.22
    sun = bpy.data.objects.new(light.name, light)
    scene.collection.objects.link(sun)
    sun.rotation_euler = (0.55, -0.55, -0.42)
    scene.render.engine = "CYCLES"
    scene.cycles.samples = samples
    scene.cycles.use_denoising = True
    scene.cycles.device = "CPU"
    try:
        prefs = bpy.context.preferences.addons["cycles"].preferences
        prefs.compute_device_type = "OPTIX"
        prefs.get_devices()
        for device in prefs.devices:
            device.use = device.type == "OPTIX"
        if any(d.use for d in prefs.devices):
            scene.cycles.device = "GPU"
    except Exception:
        pass
    scene.view_settings.view_transform = "AgX"
    scene.view_settings.exposure = 0.4
    scene.render.use_compositing = False
    scene.render.film_transparent = False
    scene.render.image_settings.file_format = "PNG"
    scene.render.resolution_percentage = 100


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="render_output")
    parser.add_argument("--views", default=",".join(VIEWS))
    parser.add_argument("--width", type=int, default=1600)
    parser.add_argument("--samples", type=int, default=24)
    args = parser.parse_args(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else [])
    output = Path(args.output).resolve()
    output.mkdir(parents=True, exist_ok=True)
    scene = bpy.context.scene
    overview_camera(scene)
    setup_lighting(scene, args.samples)
    for name in args.views.split(","):
        if name not in VIEWS:
            raise ValueError(f"Unknown view: {name}")
        camera = bpy.data.objects.get(VIEWS[name])
        if camera is None or scene.objects.get(camera.name) is None:
            raise ValueError(f"Camera not present in active scene: {VIEWS[name]}")
        scene.camera = camera
        camera.data.clip_end = 5000
        scene.render.resolution_x = args.width
        scene.render.resolution_y = round(args.width * 0.75)
        scene.render.filepath = str(output / f"{name}.png")
        bpy.ops.render.render(write_still=True)
        print("PUBLIC_RENDER_DONE", name, flush=True)


if __name__ == "__main__":
    main()
