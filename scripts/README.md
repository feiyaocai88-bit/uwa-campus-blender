# Scene utilities

Use **Blender 5.2 LTS** and the `UWA_Campus.blend` from the release. These scripts operate on an existing scene; they are not a complete build-from-scratch pipeline.

Run from a terminal, substituting the path to your Blender executable:

```sh
blender -b UWA_Campus.blend -t 2 --python-exit-code 1 --python scripts/validate_release.py -- --output publication_validation.json
blender -b UWA_Campus.blend -t 2 --python scripts/render_gallery.py -- --output render_output --views hero_overview,winthrop,reid,ezone
```

`validate_release.py` checks packed libraries and images, font portability, required collection presence, scene size and the default overview camera. It writes JSON and raises an error if any check fails. It does not repeat the historical geometry audit.

`render_gallery.py` sets temporary lighting and camera selection for rendering. It does not save the scene. It prefers an available OptiX GPU and otherwise uses the CPU. `--samples` and `--width` control rendering cost. The default views also include the Sunken Garden and both Winthrop busts. The Music, Hackett and Irwin gallery views are retained from the original R25 review renders.

To change a model, work on a copy of the `.blend`, retain the source credits for reused components, and report the object or collection name with a camera view when proposing a correction.
