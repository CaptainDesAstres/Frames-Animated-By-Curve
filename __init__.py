bl_info = {
    "name": "Frames Animated By Curve",
    "author": "Captain DesAstres",
    "version": (0, 1),
    "blender": (2, 78, 0),
    "location": "Movie Clip Editor -> Tools",
    "description": "A Blender plugin who take a short animation of a simple move to make a bigger one, using a F-Curve.",
    "wiki_url": "https://github.com/CaptainDesAstres/Frames-Animated-By-Curve",
    "category": "Animation"}


import bpy, os, shutil, platform

# Add to scene type a property to define if script does real file copy
if platform.system().lower() in ['linux', 'unix']:
	d = False
else:
	d = True
bpy.types.Scene.CtFRealCopy = bpy.props.BoolProperty(
		name="Make real copy file", 
		description="Do Frames Animated By Curve add-on make real file copy rather than symbolic link. (symbolic link are only avaible on unix/linux system)",
		default = d)



class CtFRefresh(bpy.types.Operator):
	'''operator to initialize or refresh CtF info of a movie clip'''
	bl_idname = "ctf.refresh"
	bl_label= "refresh MovieClip CtF Attribute"
	bl_options = {'INTERNAL'}
	
	def execute(self, context):
		'''refresh CtF info of a movie clip'''
		bpy.ops.clip.reload()# reload source file
		clip = context.space_data.clip
		
		# get source path and extension
		clip.CtF.path, name = os.path.split(bpy.path.abspath(clip.filepath))
		clip.CtF.path += '/'
		name, clip.CtF.ext = os.path.splitext( name )
		
		# get file naming prefix, suffix and length
		l = len(name)
		n = l-1
		while ( not name[n].isdigit() and n > 0 ):
			n -= 1
		clip.CtF.suffix = name[n+1:l]
		clip.CtF.prefix = name[0:n].rstrip('0123456789')
		clip.CtF.numberSize = l - len(clip.CtF.suffix)-len(clip.CtF.prefix)
		
		# Get clip length and first and last frame number
		clip.CtF.first = int(name[len(clip.CtF.suffix):n+1])
		clip.CtF.size = clip.frame_duration
		clip.CtF.last = clip.CtF.first + clip.CtF.size -1
		
		# adapt CtF.end property if needed
		if(not clip.CtF.init or clip.CtF.end > clip.CtF.size):
			clip.CtF.end = clip.CtF.size
			clip.CtF.init = True
		
		return {'FINISHED'}


def getFCurveByDataPath(ob, path):
	'''Return object fcurve corresponding to datapath or None'''
	
	if(ob.animation_data is None):
		return None
	
	for curve in ob.animation_data.action.fcurves:
		if curve.data_path == path:
			return curve
	return None

def getCurveLimit(curve):
	'''return curve min and max values'''
	m = M = curve.evaluate(1)
	s, e = curve.range()
	
	if s < bpy.context.scene.frame_start:
		s = bpy.context.scene.frame_start
	
	if e > bpy.context.scene.frame_end:
		e = bpy.context.scene.frame_end
	
	for i in range(int(s)-1, int(e)+1):
		val = curve.evaluate(i)
		if val < m:
			m = val
		if val > M:
			M = val
	return (m,M)

def set_end_frame(self, context):
	'''check that start and end frame are valid when changing end frame settings'''
	# check end isn't over clip size
	if self.end > self.size:
		self.end = self.size
	
	# check start isn't over end
	if self.start >= self.end:
		if self.end > 0:
			self['start'] = self.end - 1
		else:
			self['start'] = 0
			self['end'] = 1


def set_start_frame(self, context):
	'''check that start and end frame are valid when changing start frame settings'''
	# check start isn't under 0
	if self.start < 0:
		self.start = 0
	
	# check start isn't over end
	if self.start >= self.end:
		if self.start < self.size:
			self['end'] = self.start + 1
		else:
			self['start'] = self.size - 1
			self['end'] = self.size



def set_mini(self, context):
	'''check that maxi value are greater than maxi value when editing mini value'''
	if self.mini > self.maxi:
		self['maxi'] = self.mini



def set_maxi(self, context):
	'''check that maxi value are greater than maxi value when editing maxi value'''
	if self.mini > self.maxi:
		self['mini'] = self.maxi


class CtF(bpy.types.PropertyGroup):
	''' class containang all MovieClip Property design form CtF addon'''
	
	# flag to know if CtF have been initialize on this MovieClip
	init = bpy.props.BoolProperty(default = False)
	
	path = bpy.props.StringProperty() # The sources directory path
	prefix = bpy.props.StringProperty() # the source name prefix
	suffix = bpy.props.StringProperty() # the source name suffix
	numberSize = bpy.props.IntProperty() # the source name frame number size in char
	first = bpy.props.IntProperty() # the first frame number (in source file name)
	last = bpy.props.IntProperty() # the last frame number (in source file name)
	size = bpy.props.IntProperty() # number of frame of the sequence
	ext = bpy.props.StringProperty() # extension of source file
	
	# Property for frame animation curve
	curve = bpy.props.FloatProperty(
		name = 'curve',
		description = 'The curve used to determined the frame of the Movie clip to display at each frame',
		default = 0.0
		)
	
	# min value associated to the first frames
	mini = bpy.props.FloatProperty(
		name = 'Mini',
		description = 'the minimal value of the curve, all smaller value will display the first frame',
		default = 0.0,
		update = set_mini
		)
	
	# max value associated to the last frames
	maxi = bpy.props.FloatProperty(
		name = 'maxi',
		description = 'the maximal value of the curve, all bigger value will display the last frame',
		default = 1.0,
		update = set_maxi
		)
	
	# Rounding method
	rounding = bpy.props.EnumProperty(
		name = 'Rounding method',
		description = 'the rounding method use by the script to round the float value extract from the curve into a integer value corresponding to a frame',
		default = 'round',
		items = [
			#(identifier,	name, 		description, 					icon, number)
			('round',		'round',	'the closest integer.'),
			('ceil',		'ceil',		'the closest greater integer'),
			('floor',		'floor',		'the closest smaller integer')
			]
		)
	
	# destination sub directory name
	destination = bpy.props.StringProperty(
		name = "Destination subdirectory",
		description = "The name of the directory (create in the source directory) where generated file gone be.",
		default = "CtFOutput" )
	
	# first frame of the clip to use
	start = bpy.props.IntProperty(
		name = "First frame",
		description = "first frame that Frames Animated By Curve add-on must take in count",
		default = 0,
		min = 0,
		update = set_start_frame)
	
	# last frame of the clip to use
	end = bpy.props.IntProperty(
		name = "Last frame",
		description = "last frame that Frames Animated By Curve add-on must take in count",
		update = set_end_frame)
	
	
	def getFrameName(self, n):
		'''return the file name of a frame'''
		return	(	self.prefix +
					str(n).rjust(self.numberSize, '0')+
					self.suffix + self.ext	)
		
	
	
	def draw(self, context, layout, clip):
		'''draw the CtF panel'''
		
		if(clip.source != 'SEQUENCE'):
			# Display an error message, requesting for a sequence of images
			row = layout.row()
			row.label( text="Current movie can't be use by addon.",
				 icon="ERROR"  )
			row = layout.row()
			row.label( text="Only images sequence are accept." )
			
		elif(not self.init):
			# ask to initialize CtF on thes MovieClip
			row = layout.row()
			row.operator(
				"ctf.refresh",
				text="initialize MovieClip info")
			
		else:
			# Display the directory path
			row = layout.row()
			row.label( text = "Frame Directory path:" )
			row = layout.row()
			row.label( text= self.path )
			
			# Display frame extension
			row = layout.row()
			col = row.column()
			col.label( text="File type: "+self.ext )
			
			# Display first to last accepted frame name range
			col = row.column()
			col.label( text="Valid frames: "+self.getFrameName(self.first)+' to '\
				+self.getFrameName(self.last) )
			
			# Display Start/End settings
			layout.separator()
			row = layout.row()
			col = row.column()
			col.prop(self, "start")
			col = row.column()
			col.prop(self, "end")
			
			# A float field to animated with a curve
			layout.separator()
			row = layout.row()
			col = row.column()
			col.prop(self, "curve")
			
			# A field to remind F-Curve min and max value
			fCurve = getFCurveByDataPath(clip, 'CtF.curve')
			if(fCurve is None):
				m = M = self.curve
			else:
				m, M = getCurveLimit(fCurve)
			m = round(m*1000)/1000
			M = round(M*1000)/1000
			col = row.column()
			col.label( text = "(Goes from "+str(m)+" to "+str(M)+')' )
			
			# A field to set the min F-Curve Value to assigne to the first frames
			row = layout.row()
			col = row.column()
			col.prop(self, "mini")
			
			# A field to set the max F-Curve Value to assigne to the last frames
			col = row.column()
			col.prop(self, "maxi")
			
			# A field to choose between Round Floor and Ceil rounding method
			layout.separator()
			row = layout.row()
			col = row.column()
			col.prop(self, "rounding")
			
			# A field to set the name of the sub directory name to use as destination
			col = row.column()
			col.prop(self, "destination")
			
			# A checkbox to get real frame file copy
			row = layout.row()
			col = row.column()
			col.prop(context.scene, "CtFRealCopy")
			
			# the button to run the script
			col = row.column()
			col.operator(
				"curve.toframe",
				text="run")


class CurveToFrame(bpy.types.Operator):
	'''the operaton to execute add on feature'''
	bl_idname = "curve.toframe"
	bl_label= "Frames Animated By Curve"
	bl_options = {'INTERNAL'}
	
	def execute(self, context):
		bpy.ops.ctf.refresh()
		clip = context.space_data.clip
		
		# check output method
		if(context.scene.CtFRealCopy):
			output = shutil.copyfile
		else:
			if(platform.system().lower() in ['linux', 'unix']):
				output = os.symlink
		
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

