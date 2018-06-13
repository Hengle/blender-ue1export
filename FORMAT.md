The following is an unofficial spec of James Schmaltz's little monstrosity of
a mesh format that was first made in 1995, back when Unreal Engine was still in
its very early stages, and hasn't changed at all ever since.

A lot of things are "unused", but there are cases where they contain some data
that I cannot identify. Still, it's not used at all by the engine when
importing meshes, so it doesn't really matter.

Everything is in little endian, btw. stdint.h types are used to describe sizes
in most cases, because I like using them.

### DATAFILE

File that contains triangle data.

#### Header (48 bytes)

* Number of Polygons (uint16_t): total count of polys
* Number of Vertices (uint16_t): total count of vertices in one frame
* Bogus Rotation (uint16_t): unused
* Bogus Frame (uint16_t): unused
* Bogus Normal (uint32_t[3]): unused
* Fix Scale (uint32_t): unused
* Unused (uint32_t[3]): unused (duh)
* Padding (12 bytes): just zeroes

#### Poly (16 bytes)

* Vertex Indices (uint16_t[3]): vertices that make up this poly, in CCW order
* Poly Type / Flags (uint8_t): render style and flags
  * Types:
    * 0: normal
    * 1: two-sided
    * 2: two-sided translucent
    * 3: two-sided masked
    * 4: two-sided modulated
  * Flags:
    * 0x08: weapon triangle (see notes)
    * 0x10: unlit (draws fullbright)
    * 0x20: curvy (unknown original use, in Unreal v227 uses facet normal
      rather than smoothed vertex normals, this is used for example in the
      Wooden Box and Steel Box meshes)
    * 0x40: environment map (pseudo-cubemap shiny surface)
    * 0x80: no smooth (texture is not interpolated in this poly)
* Poly Color (uint8_t): Unused
* UV Coords (uint8_t[3][2]): Texture coords for each vertex in 0,255 range
* Texture Number (uint8_t): Material index, UE1 supports 0-8 range
* Flags (uint8_t): Unused, redundant

Notes about "Weapon Triangle" flag:

* Weapon's 3rd person mesh is attached to the midpoint of vertices 0 and 2 in
  the poly.
* Unit vector from 2 to 0 determines the Z axis for the weapon, Y comes from
  the facet normal of the poly, and then X is calculated from the cross
  product of the two.
* Previously I theorized that the vertices were used for computing euler
  angles. pitch and angle would come from a unit vector from 0 to 1, then the
  vector from 2 to 0 would be used to calculate roll, but nope, that's not the
  case.
* Umodel strips the weapon triangle on mesh extraction. It is however preserved
  by both UTPT and Unreal v227's updated editor. I may write a tool myself for
  extracting meshes someday.

### ANIVFILE

File that contains all the vertex positions for each frame of animation.

#### Header (4 bytes)

* Number of Frames (uint16_t): total count of frames in the anivfile
* Frame Size (uint16_t): size of one frame in bytes. Can be used to determine
  vertex format (either standard, where framesize = numverts × 4, or deus ex,
  where framesize = numverts × 8)

#### Animation Frame (variable size)

Each animation frame is an array containing n vertices, where n is the number
of vertices specified in the datafile.

Vertex structure varies with format:

* Standard format (uint32_t): 11 bits X, 11 bits Y, 10 bits Z (including
  signs for each). UE1 seems to process the numbers as-is, with X and Y being
  in the range -1024,1023 and Z being in the range -512,511. This is why so
  many model definitions in Unreal/UT tend to have a meshmap scale in Z that is
  double as much as X or Y
* Deus Ex format (int16_t[4]): 16 bits for X, Y and Z, plus padding. Only Deus
  Ex supports this, trying to use a mesh of this format in any other UE1 title
  will have catastrophic effects. This format is currently not supported in
  GZDoom
