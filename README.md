# UE1 vertex mesh export plugin for Blender

This is a plugin for Blender 2.7.9+ that exports an anivfile/datafile pair for
use in Unreal Engine 1.x games (or in GZDoom, since it also supports the format
now, thanks to me).

### Important information

* UE1 uses left-hand coordinates, with X as forward, Z as up and Y as right.
  Y will be inverted on export, so you don't need to mirror it.
* Your model should be contained within (-1,1) across all axes, otherwise
  things will break.
* The limit of vertices is 16383 if exporting in standard format, 8191 if
  exporting in Deus Ex format.
* The limit of triangles and frames is 65535 for both.
* UE1 supports only up to 9 individual materials, GZDoom only up to 32.
* (Remember to remove unused materials, as they still add up to the previous
  limit)

## The big TODO list

* Automatically offset/scale models before export to fit the limits.
* Support for face types (currently you need to set those with UnrealFX)
* Properly handle multiple objects with individual materials (currently the
  exporter doesn't difference between material indices of separate objects).
* Produce a "ready-to-use" .uc file with #exec directives containing all the
  needed offsets and scales on import, an "All" anim sequence containing all
  exported frames, and also texture imports and meshmap assignments for all
  materials.
* Import plugin?
