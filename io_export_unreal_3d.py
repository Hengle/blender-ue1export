# Unreal Engine 1.x vertex mesh exporter for Blender
# (C)2018 Marisa Kirisame, UnSX Team
# Released under the GNU General Public License version 3 (or later)

bl_info = {
	"name": "Unreal .3D",
	"author": "Marisa Kirisame",
	"version": (1, 0, 0),
	"blender": (2, 7, 0),
	"location": "File > Export > Unreal model (.3d)",
	"description": "Export to Unreal Engine 1.x vertex mesh format (.3d)",
	"warning": "Make sure to check console output for important warnings",
	"wiki_url": "https://github.com/OrdinaryMagician/blender-ue1export/",
	"tracker_url": "https://github.com/OrdinaryMagician/blender-ue1export/issues/",
	"category": "Import-Export"}

import bpy, struct, math, os, time

default_deusex = False
default_dump = False

class ue1vert:
	xyz = []

	def __init__(self):
		self.xyz = [0,0,0]

	def Save(self, file):
		packvert = (((self.xyz[2]>>6)&0x3FF)<<22)|(((self.xyz[1]>>5)&0x7FF)<<11)|((self.xyz[0]>>5)&0x7FF)
		data = struct.pack("<1I",packvert)
		file.write(data)

class ue1dxvert:
	xyz = []

	def __init__(self):
		self.xyz = [0,0,0]

	def Save(self, file):
		data = struct.pack("<3H2x",self.xyz[0],self.xyz[1],self.xyz[2])
		file.write(data)

class ue1frame:
	verts = []

	def __init__(self):
		self.verts = []

	def Save(self, file):
		for v in self.verts:
			v.Save(file)

class ue1anivfile:
	numframes = 0
	framesize = 0
	frames = []


	def __init__(self):
		self.numframes = 0
		self.framesize = 0
		self.frames = []

	def Save(self, file):
		data = struct.pack("<2H",self.numframes,self.framesize)
		file.write(data)
		for f in self.frames:
			f.Save(file)

class ue1poly:
	vertices = []
	ptype = 0
	uv = []
	texnum = 0

	def __init__(self):
		self.vertices = [0,0,0]
		self.ptype = 0
		self.uv = [[0,0],[0,0],[0,0]]
		self.texnum = 0

	def Save(self, file):
		data = struct.pack("<3H1B1x7B1x",self.vertices[0],self.vertices[1],self.vertices[2],self.ptype,self.uv[0][0],self.uv[0][1],self.uv[1][0],self.uv[1][1],self.uv[2][0],self.uv[2][1],self.texnum)
		file.write(data)

class ue1datafile:
	numpolys = 0
	numverts = 0
	polys = []

	def __init__(self):
		self.numpolys = 0
		self.numverts = 0
		self.polys = []

	def Save(self, file):
		data = struct.pack("<2H44x",self.numpolys,self.numverts)
		file.write(data)
		for p in self.polys:
			p.Save(file)

class ue1settings:
	def __init__(self,savepath,deusex,dump):
		self.savepath = savepath
		self.deusex = deusex
		self.dump = dump

def print_ue1(data,aniv,dump):
	if dump == True:
		print("-- DATAFILE --")
		print("Num Polys: " + str(data.numpolys))
		print("Num Verts: " + str(data.numverts))
	htexnum = 0
	minv = [math.inf,math.inf,math.inf]
	maxv = [-math.inf,-math.inf,-math.inf]
	for p,dp in enumerate(data.polys):
		if dump == True:
			print(" Poly " + str(p) + ":")
			print("  Vertices: " + str(dp.vertices[0]) + " / " + str(dp.vertices[1]) + " / " + str(dp.vertices[2]))
			print("  Type: " + str(dp.ptype))
			print("  UVs: " + str(dp.uv[0][0]) + "," + str(dp.uv[0][1]) + " / " + str(dp.uv[1][0]) + "," + str(dp.uv[1][1]) + " / " + str(dp.uv[2][0]) + "," + str(dp.uv[2][1]))
			print("  Tex Num: " + str(dp.texnum))
		if dp.texnum > htexnum:
			htexnum = dp.texnum
	if dump == True:
		print("-- ANIVFILE --")
		print("Num Frames: " + str(aniv.numframes))
		print("Frame Size: " + str(aniv.framesize))
	for f,af in enumerate(aniv.frames):
		if dump == True:
			print(" Frame " + str(f) + ":")
		for v,fv in enumerate(af.verts):
			if dump == True:
				print("  " + str(v) + ": " + str(fv.xyz[0]) + "," + str(fv.xyz[1]) + "," + str(fv.xyz[2]))
			if fv.xyz[0] < minv[0]:
				minv[0] = fv.xyz[0]
			if fv.xyz[1] < minv[1]:
				minv[1] = fv.xyz[1]
			if fv.xyz[2] < minv[2]:
				minv[2] = fv.xyz[2]
			if fv.xyz[0] > maxv[0]:
				maxv[0] = fv.xyz[0]
			if fv.xyz[1] > maxv[1]:
				maxv[1] = fv.xyz[1]
			if fv.xyz[2] > maxv[2]:
				maxv[2] = fv.xyz[2]
	if data.numpolys > 65535:
		print("WARNING: more than 65535 polygons (" + str(data.numpolys) + ")")
	if data.numverts > 65535:
		print("WARNING: more than 65535 vertices (" + str(data.numverts) + ")")
	if htexnum > 8:
		print("WARNING: material index above 8 detected (" + str(htexnum) + ")")
	if aniv.numframes > 65535:
		print("WARNING: more than 65535 frames (" + str(aniv.numframes) + ")")
	if aniv.framesize > 65535:
		print("WARNING: frame size above 65535 (" + str(aniv.framesize) + ")")
	if minv[0] < -32768:
		print("WARNING: minimum X bounds below -32768 (" + str(minv[0]) + ")")
	if minv[1] < -32768:
		print("WARNING: minimum Y bounds below -32768 (" + str(minv[1]) + ")")
	if minv[2] < -32768:
		print("WARNING: minimum Z bounds below -32768 (" + str(minv[2]) + ")")
	if maxv[0] > 32767:
		print("WARNING: maximum X bounds above 32767 (" + str(maxv[0]) + ")")
	if maxv[1] > 32767:
		print("WARNING: maximum Y bounds above 32767 (" + str(maxv[1]) + ")")
	if maxv[2] > 32767:
		print("WARNING: maximum Z bounds above 32767 (" + str(maxv[2]) + ")")

def save_ue1(settings):
	starttime = time.clock()
	print("=== BEGIN UE1 MESH EXPORT ===")
	bpy.ops.object.mode_set(mode='OBJECT')
	aniv = ue1anivfile()
	data = ue1datafile()
	aniv.numframes = (bpy.context.scene.frame_end+1)-bpy.context.scene.frame_start
	global actobject
	actobject = bpy.context.scene.objects.active
	selobjects = bpy.context.selected_objects
	vlist = []
	for obj in selobjects:
		if obj.type == 'MESH':
			bpy.context.scene.frame_set(bpy.context.scene.frame_start)
			tmpconv = obj.data.copy()
			scene = bpy.context.scene
			scene.objects.active = obj
			bpy.ops.object.mode_set(mode='EDIT')
			bpy.ops.mesh.select_all(action='SELECT')
			bpy.ops.mesh.quads_convert_to_tris()
			bpy.ops.object.mode_set(mode='OBJECT')
			scene.objects.active = actobject
			nobj = obj.to_mesh(bpy.context.scene, True, 'PREVIEW')
			obj.data = tmpconv
			tmpconv = []
			UVImg = nobj.tessface_uv_textures[0]
			coords = UVImg.data
			j = 0
			localvlist = []
			for f,face in enumerate(nobj.tessfaces):
				fcoords = coords[j]
				j += 1
				poly = ue1poly()
				# TODO poly types
				poly.ptype = 0
				poly.texnum = face.material_index
				for v,vert_index in enumerate(face.vertices):
					poly.uv[2-v][0] = int(min(max(fcoords.uv[v][0]*255,0),255))
					poly.uv[2-v][1] = int(min(max((1.0-fcoords.uv[v][1])*255,0),255))
					match = 0
					match_index = 0
					for i,vi in enumerate(vlist):
						if vi == vert_index:
							match = 1
							match_index = i
					if match == 0:
						vlist.append(vert_index)
						localvlist.append(vert_index)
						poly.vertices[2-v] = data.numverts
						data.numverts += 1
					else:
						poly.vertices[2-v] = match_index
				data.polys.append(poly)
				data.numpolys += 1
			for frame in range(bpy.context.scene.frame_start,bpy.context.scene.frame_end+1):
				bpy.context.scene.frame_set(frame)
				tmpconv = obj.data.copy()
				scene = bpy.context.scene
				scene.objects.active = obj
				bpy.ops.object.mode_set(mode='EDIT')
				bpy.ops.mesh.select_all(action='SELECT')
				bpy.ops.mesh.quads_convert_to_tris()
				bpy.ops.object.mode_set(mode='OBJECT')
				scene.objects.active = actobject
				fobj = obj.to_mesh(bpy.context.scene, True, 'PREVIEW')
				obj.data = tmpconv
				tmpconv = []
				nframe = ue1frame()
				if obj.parent == "True":
					if obj.parent.name == "Armature":
						if obj.find_armature() != NULL:
							skel_loc = obj.parent.location
							nframe.localOrigin = obj.location-skel_loc
							my_matrix = obj.matrix_world*obj.matrix_parent_inverse
				else:
					nframe.localOrigin = obj.location
					my_matrix = obj.matrix_world
				for vi in localvlist:
					vert = fobj.vertices[vi]
					if settings.deusex == True:
						nvert = ue1dxvert()
					else:
						nvert = ue1vert()
					nxyz = my_matrix*vert.co
					nvert.xyz[0] = int(nxyz[0]*32768)
					nvert.xyz[1] = -int(nxyz[1]*32768)
					nvert.xyz[2] = int(nxyz[2]*32768)
					nframe.verts.append(nvert)
				aniv.frames.append(nframe)
				bpy.data.meshes.remove(fobj)
			bpy.data.meshes.remove(nobj)
			obj = []
	if settings.deusex == True:
		aniv.framesize = data.numverts*8
	else:
		aniv.framesize = data.numverts*4
	if bpy.context.selected_objects:
		print_ue1(data,aniv,settings.dump)
		anivfile = open(settings.savepath + "_a.3d", "wb")
		datafile = open(settings.savepath + "_d.3d", "wb")
		aniv.Save(anivfile)
		data.Save(datafile)
		anivfile.close()
		datafile.close()
		print("UE1 mesh saved to " + settings.savepath)
		elapsedtime = round(time.clock()-starttime,6)
		print("Elapsed " + str(elapsedtime) + " seconds")
	else:
		print("Select an object to export!")

from bpy.props import *

class ExportUE1(bpy.types.Operator):
	'''Export to .3d'''
	bl_idname = "export.3d"
	bl_label = 'Export Unreal .3D'

	filepath = StringProperty(subtype='FILE_PATH',name="File Path",description="Filepath for exporting",maxlen=1024,default="")
	ue1deusex = BoolProperty(name="Deus Ex format",description="Use Deus Ex high precision vertex format",default=default_deusex)
	ue1dump = BoolProperty(name="Dump model to console",description="Dump full model information to console",default=default_dump)

	def execute(self, context):
		settings = ue1settings(savepath=self.properties.filepath,deusex=self.properties.ue1deusex,dump=self.properties.ue1dump)
		save_ue1(settings)
		return {'FINISHED'}

	def invoke(self, context, event):
		wm = context.window_manager
		wm.fileselect_add(self)
		return {'RUNNING_MODAL'}

	@classmethod
	def poll(cls, context):
		return context.active_object != None

def menu_func(self, context):
	self.layout.operator(ExportUE1.bl_idname,text="Unreal .3D",icon='BLENDER')

def register():
	bpy.utils.register_class(ExportUE1)
	bpy.types.INFO_MT_file_export.append(menu_func)

def unregister():
	bpy.utils.unregister_class(ExportUE1)
	bpy.types.INFO_MT_file_export.remove(menu_func)

if __name__ == "__main__":
	register()
