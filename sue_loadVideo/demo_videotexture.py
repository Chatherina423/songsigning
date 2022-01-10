# import sys 
# sys.path.append('/Users/hsuehtil/Dropbox/BlenderToolbox/cycles')
# from include import *
import os
import bpy
import numpy as np
import bmesh

class colorObj(object):
    def __init__(self, RGBA = (144.0/255, 210.0/255, 236.0/255, 1), \
    H = 0.5, S = 1.0, V = 1.0,\
    B = 0.0, C = 0.0):
        self.H = H # hue
        self.S = S # saturation
        self.V = V # value
        self.RGBA = RGBA
        self.B = B # birghtness
        self.C = C # contrast

def blenderInit(resolution_x, resolution_y, numSamples = 128, exposure = 1.5, useBothCPUGPU = False):
	# clear all
	bpy.ops.wm.read_homefile()
	bpy.ops.object.select_all(action = 'SELECT')
	bpy.ops.object.delete() 
	# use cycle
	bpy.context.scene.render.engine = 'CYCLES'
	bpy.context.scene.render.resolution_x = resolution_x 
	bpy.context.scene.render.resolution_y = resolution_y 
	# bpy.context.scene.cycles.film_transparent = True
	bpy.context.scene.render.film_transparent = True
	bpy.context.scene.cycles.samples = numSamples 
	bpy.context.scene.cycles.max_bounces = 6
	bpy.context.scene.cycles.film_exposure = exposure
	bpy.data.scenes[0].view_layers['View Layer']['cycles']['use_denoising'] = 1

	# set devices
	cyclePref  = bpy.context.preferences.addons['cycles'].preferences
	cyclePref.compute_device_type = 'CUDA'
	for dev in cyclePref.devices:
		if dev.type == "CPU" and useBothCPUGPU is False:
			dev.use = False
		else:
			dev.use = True
	bpy.context.scene.cycles.device = 'GPU'

	for dev in cyclePref.devices:
		print (dev)
		print (dev.use)

	return 0

def setMat_videotexture(mesh, texturePath, meshColor):
    mat = bpy.data.materials.new('MeshMaterial')
    mesh.data.materials.append(mat)
    mesh.active_material = mat
    mat.use_nodes = True
    tree = mat.node_tree

    # set principled BSDF
    PRI = tree.nodes["Principled BSDF"]
    PRI.inputs['Roughness'].default_value = 1.0
    PRI.inputs['Sheen Tint'].default_value = 0

    TI = tree.nodes.new('ShaderNodeTexImage')
    absTexturePath = os.path.abspath(texturePath)
    TI.image = bpy.data.images.load(absTexturePath)
    TI.image_user.use_auto_refresh = True

    bpy.data.materials["MeshMaterial"].node_tree.nodes["Image Texture"].image_user.use_auto_refresh = True


    # set color using Hue/Saturation node
    HSVNode = tree.nodes.new('ShaderNodeHueSaturation')
    HSVNode.inputs['Saturation'].default_value = meshColor.S
    HSVNode.inputs['Value'].default_value = meshColor.V
    HSVNode.inputs['Hue'].default_value = meshColor.H

    # set color brightness/contrast
    BCNode = tree.nodes.new('ShaderNodeBrightContrast')
    BCNode.inputs['Bright'].default_value = meshColor.B
    BCNode.inputs['Contrast'].default_value = meshColor.C

    tree.links.new(TI.outputs['Color'], HSVNode.inputs['Color'])
    tree.links.new(HSVNode.outputs['Color'], BCNode.inputs['Color'])
    tree.links.new(BCNode.outputs['Color'], PRI.inputs['Base Color'])


def readOBJ(filePath, location, rotation_euler, scale):
	x = rotation_euler[0] * 1.0 / 180.0 * np.pi 
	y = rotation_euler[1] * 1.0 / 180.0 * np.pi 
	z = rotation_euler[2] * 1.0 / 180.0 * np.pi 
	angle = (x,y,z)

	prev = []
	for ii in range(len(list(bpy.data.objects))):
		prev.append(bpy.data.objects[ii].name)
	bpy.ops.import_scene.obj(filepath=filePath, split_mode='OFF')
	after = []
	for ii in range(len(list(bpy.data.objects))):
		after.append(bpy.data.objects[ii].name)
	name = list(set(after) - set(prev))[0]
	mesh = bpy.data.objects[name]

	mesh.location = location
	mesh.rotation_euler = angle
	mesh.scale = scale
	bpy.context.view_layer.update()

	return mesh 

outputPath = './demo_videotexture.png'

# # init blender
imgRes_x = 720  # increase this for paper figures
imgRes_y = 720  # increase this for paper figures
numSamples = 50 # usually increase it to >200 for paper figures
exposure = 1.0
blenderInit(imgRes_x, imgRes_y, numSamples, exposure)

# read mesh 
meshPath = 'UV_grid.obj'
location = (0.92,0.2,0)
rotation = (90, 0,0)
scale = (1.5,1.5,1.5)
mesh = readOBJ(meshPath, location, rotation, scale)

# # set shading
bpy.ops.object.shade_smooth()
# bpy.ops.object.shade_flat()

# # subdivision
# level = 2
# subdivision(mesh, level)

# # set material
# colorObj(RGBA, H, S, V, Bright, Contrast)
useless = (0,0,0,1)
meshColor = colorObj(useless, 0.5, 1.0, 1.0, 0.0, 0.0)
texturePath = './test_video.mp4' 
# using relative path gives us weired bug...
setMat_videotexture(mesh, texturePath, meshColor)

# # # set invisible plane (shadow catcher)
# groundCenter = (0,0,0)
# shadowDarkeness = 0.7
# groundSize = 20
# invisibleGround(groundCenter, groundSize, shadowDarkeness)

# # # set camera
# camLocation = (1.9,2,2.2)
# lookAtLocation = (0,0,0.5)
# focalLength = 45
# cam = setCamera(camLocation, lookAtLocation, focalLength)

# # # set sunlight
# lightAngle = (-15,-34,-155) 
# strength = 2
# shadowSoftness = 0.1
# sun = setLight_sun(lightAngle, strength, shadowSoftness)

# # # set ambient light
# ambientColor = (0.2,0.2,0.2,1)
# setLight_ambient(ambientColor)

# # save blender file
bpy.ops.wm.save_mainfile(filepath='./test.blend')

# # save rendering
# renderImage(outputPath, cam)