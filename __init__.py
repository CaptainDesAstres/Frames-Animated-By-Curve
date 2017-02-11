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
		'''the function that draw the addon UI'''
		layout = self.layout
		
		# A field to select the frames to use (or the directory containing it)
		# A field to set the first and last frames to use from source
		# A field to remind the extension of the frames
		# A field to choose the object wich the curve is assigned to
		# A field to choose the F-Curve
		# A field to remind F-Curve min and max value 
		# A field to set the min F-Curve Value to assigne to the first frames
		# A field to set the max F-Curve Value to assigne to the last frames
		# A field to choose between Round Floor and Ceil rounding method
		# A field to set the name of the sub directory name to use as destination
		# A checkbox to set if user want to make real copy of the frame file rather than link
		# A button to refresh display
		# A button to run the script


def register():
	'''addon register'''
	bpy.utils.register_class(FramesAnimatedByCurvePanel)
	print("Frames Animated By Curve is enable")


def unregister():
	'''addon unregister'''
	bpy.utils.unregister_class(FramesAnimatedByCurvePanel)
	print("Frames Animated By Curve is disable")

