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

# Add to scene type a property to define if script does real file copy
bpy.types.Scene.CtFRealCopy = bpy.props.BoolProperty(
		name="Make real copy file", 
		description="Do Frames Animated By Curve add-on make real file copy rather than link",
		default = False)



class CtFRefresh(bpy.types.Operator):
	bl_idname = "ctf.refresh"
	bl_label= "refresh MovieClip CtF Attribute"
	bl_options = {'INTERNAL'}
	
	def execute(self, context):
		bpy.ops.clip.reload()
		clip = context.space_data.clip
		
		clip.CtF.path, clip.CtF.firstName = os.path.split(bpy.path.abspath(clip.filepath))
		clip.CtF.path += '/'
		clip.CtF.firstName, clip.CtF.ext = os.path.splitext( clip.CtF.firstName )
		
		# Get the last frame name and the clip size
		clip.CtF.size = clip.frame_duration
		nameLen = len(clip.CtF.firstName)
		
		if(not clip.CtF.init):
			clip.CtF.end = clip.CtF.size
			clip.CtF.init = True
		
		last = int(clip.CtF.firstName) + clip.CtF.size - 1
		clip.CtF.lastName = ('0'*(nameLen - len(str(last)) ))+str(last)
		
		return {'FINISHED'}


def set_end_frame(self, context):
	'''check that start and end frame are valid when changing end frame settings'''
	if self.end > self.size:
		self.end = self.size
	
	if self.start >= self.end:
		if self.end > 0:
			self['start'] = self.end - 1
		else:
			self['start'] = 0
			self['end'] = 1


def set_start_frame(self, context):
	'''check that start and end frame are valid when changing start frame settings'''
	if self.start < 0:
		self.start = 0
	
	if self.start >= self.end:
		if self.start < self.size:
			self['end'] = self.start + 1
		else:
			self['start'] = self.size - 1
			self['end'] = self.size


class CtF(bpy.types.PropertyGroup):
	''' class containang all MovieClip Property design form CtF addon'''
	
	init = bpy.props.BoolProperty(default = False)
	path = bpy.props.StringProperty()
	firstName = bpy.props.StringProperty()
	lastName = bpy.props.StringProperty()
	size = bpy.props.IntProperty()
	ext = bpy.props.StringProperty()
	
	# first frame property
	start = bpy.props.IntProperty(
		name = "First frame",
		description = "first frame that Frames Animated By Curve add-on must take in count",
		default = 0,
		min = 0,
		update = set_start_frame)
	
	# last frame property
	end = bpy.props.IntProperty(
		name = "Last frame",
		description = "last frame that Frames Animated By Curve add-on must take in count",
		update = set_end_frame)
	
	
	def draw(self, context, layout, clip):
		'''a method to draw the panel'''
		
		if(self.path == ''):
			row = layout.row()
			row.operator(
				"ctf.refresh",
				text="initialize MovieClip info")
		elif(self.ext in ['.bmp', '.dpx', '.rgb', '.png', '.jpg', '.jpeg', '.jp2',
						'.j2c', '.tga', '.exr', '.cin', '.hdr', '.tif']\
						and type(self.firstName) is str\
						and self.firstName.isdecimal() ) :
			
			# Display the directory path
			row = layout.row()
			row.label( text = "Frame Directory path:" )
			row = layout.row()
			row.label( text= self.path )
			
			# Display frame extension
			row = layout.row()
			row.label( text="File type: "+self.ext )
			
			
			# Display first to last accepted frame name range
			row = layout.row()
			row.label( text="Valid frames: "+self.firstName+self.ext+' to '\
				+self.lastName+self.ext )
			
			# Display Start/End settings
			row = layout.row()
			row.prop(self, "start")
			row = layout.row()
			row.prop(self, "end")
			
			# A checkbox to get real frame file copy
			row = layout.row()
			row.prop(context.scene, "CtFRealCopy")
			
			# the button to run the script
			row = layout.row()
			row.operator(
				"curve.toframe",
				text="run")
			
			# A field to choose the object wich the curve is assigned to
			# A field to choose the F-Curve
			# A field to remind F-Curve min and max value 
			# A field to set the min F-Curve Value to assigne to the first frames
			# A field to set the max F-Curve Value to assigne to the last frames
			# A field to choose between Round Floor and Ceil rounding method
			# A field to set the name of the sub directory name to use as destination
			
		else:
			# Display an error message, request for a sequence of images
			row = layout.row()
			row.label( text="Current movie can't be use by addon.",
				 icon="ERROR"  )
			row = layout.row()
			row.label( text="Only images sequence are accept." )
			row = layout.row()
			row.label( text="Only decimal character are accept in file name." )
			row = layout.row()
			row.operator(
				"ctf.refresh",
				text="Refresh MovieClip info")


class CurveToFrame(bpy.types.Operator):
	bl_idname = "curve.toframe"
	bl_label= "Frames Animated By Curve"
	bl_options = {'INTERNAL'}
	
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
			clip = context.space_data.clip
			
			# draw panel
			clip.CtF.draw(context, layout, clip)
			
		else:
			# Display a request for a movie clip
			row = layout.row()
			row.label( text="select/load an images sequence in Movie Editor.",
					 icon="ERROR" )
			row = layout.row()
			row.operator(
				"ctf.refresh",
				text="Refresh MovieClip info")
		


def register():
	'''addon register'''
	bpy.utils.register_class(CtFRefresh)
	bpy.utils.register_class(CtF)
	bpy.types.MovieClip.CtF = bpy.props.PointerProperty(type=CtF)
	bpy.utils.register_class(CurveToFrame)
	bpy.utils.register_class(FramesAnimatedByCurvePanel)
	print("Frames Animated By Curve is enable")


def unregister():
	'''addon unregister'''
	bpy.utils.unregister_class(CtFRefresh)
	bpy.utils.unregister_class(CtF)
	bpy.utils.unregister_class(FramesAnimatedByCurvePanel)
	bpy.utils.unregister_class(CurveToFrame)
	print("Frames Animated By Curve is disable")

