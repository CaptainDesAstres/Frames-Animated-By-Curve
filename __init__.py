bl_info = {
    "name": "Frames Animated By Curve",
    "author": "Captain DesAstres",
    "version": (0, 1),
    "blender": (2, 78, 0),
    "location": "Movie Clip Editor -> Tools",
    "description": "A Blender plugin who take a short animation of a simple move to make a bigger one, using a F-Curve.",
    "wiki_url": "https://github.com/CaptainDesAstres/Frames-Animated-By-Curve",
    "category": "Animation"}


import bpy

class FramesAnimatedByCurvePanel(bpy.types.Panel):
	'''class of the panel who contains addon control'''
	bl_space_type = "CLIP_EDITOR"
	bl_region_type = "TOOLS"
	bl_label = "Frames Animated By Curve"
	bl_category = "Curve Anim"
	
	def draw(self, context):
		layout = self.layout


def register():
	'''addon register'''
	bpy.utils.register_class(FramesAnimatedByCurvePanel)
	print("Frames Animated By Curve is enable")


def unregister():
	'''addon unregister'''
	bpy.utils.unregister_class(FramesAnimatedByCurvePanel)
	print("Frames Animated By Curve is disable")

