bl_info = {
    "name": "Frames Animated By Curve",
    "author": "Captain DesAstres",
    "version": (0, 1),
    "blender": (2, 78, 0),
    "location": "Movie Clip Editor -> Tools",
    "description": "A Blender plugin who take a short animation of a simple move to make a bigger one, using a F-Curve.",
    "wiki_url": "https://github.com/CaptainDesAstres/Frames-Animated-By-Curve",
    "category": "Animation"}


import bpy, os

class CurveToFrame(bpy.types.Operator):
	bl_idname = "curve.toframe"
	bl_label= "Frames Animated By Curve"
	
	def execute(self, context):
		print("Frames Animated By Curve have been executed")
		return {'FINISHED'}



class FramesAnimatedByCurvePanel(bpy.types.Panel):
	'''class of the panel who contains addon control'''
	bl_space_type = "CLIP_EDITOR"
	bl_region_type = "TOOLS"
	bl_label = "Frames Animated By Curve"
	bl_category = "Curve Anim"
	
	def draw(self, context):
		'''the function that draw the addon UI'''
		layout = self.layout
		
		# check if there is a movie clip set
		if(context.space_data.clip is not None):
			firstFile = context.space_data.clip.filepath
			first, ext = os.path.basename( firstFile ).split('.')
			
			# Check farme format
			if ext in ['bmp', 'dpx', 'rgb', 'png', 'jpg', 
						'jpeg', 'jp2', 'j2c', 'tga', 'exr', 'cin', 'hdr', 'tif']\
						and type(first) is str\
						and first.isdecimal() :
				# Display the first frame path
				row = layout.row()
				row.label( text="First frame path:" )
				row = layout.row()
				row.label( text= firstFile )
				
				# Display frame extension
				row = layout.row()
				row.label( text="File type: "+ext )
				
				# Get and display the last frame name
				
			else:
				# Display an error message, request for a sequence of images
				row = layout.row()
				row.label( text="Current movie can't be use by addon.",
					 icon="ERROR"  )
				row = layout.row()
				row.label( text="Only images sequence are accept." )
				row = layout.row()
				row.label( text="Only decimal character are accept in file name." )
				
		else:
			# Display a request for a movie clip
			row = layout.row()
			row.label( text="select/load an images sequence in Movie Editor.",
					 icon="ERROR" )
		
		
		
		
		# the button to run the script
		row = layout.row()
		row.operator(
			"curve.toframe",
			text="run")
		
		# A field to set the first and last frames to use from source
		# A field to choose the object wich the curve is assigned to
		# A field to choose the F-Curve
		# A field to remind F-Curve min and max value 
		# A field to set the min F-Curve Value to assigne to the first frames
		# A field to set the max F-Curve Value to assigne to the last frames
		# A field to choose between Round Floor and Ceil rounding method
		# A field to set the name of the sub directory name to use as destination
		# A checkbox to set if user want to make real copy of the frame file rather than link


def register():
	'''addon register'''
	bpy.utils.register_class(CurveToFrame)
	bpy.utils.register_class(FramesAnimatedByCurvePanel)
	print("Frames Animated By Curve is enable")


def unregister():
	'''addon unregister'''
	bpy.utils.unregister_class(FramesAnimatedByCurvePanel)
	bpy.utils.unregister_class(CurveToFrame)
	print("Frames Animated By Curve is disable")

