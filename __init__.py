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
from math import ceil, floor

# Add to scene type a property to define if script does real file copy
if platform.system().lower() in ['linux', 'unix']:
	bpy.types.Scene.CtFRealCopy = bpy.props.BoolProperty(
		name="Make real copy file", 
		description="Do Frames Animated By Curve add-on make \
				real file copy rather than symbolic link.",
		options = {'LIBRARY_EDITABLE'},
		default = False)
else:
	bpy.types.Scene.CtFRealCopy = bpy.props.BoolProperty(
		name="Make real copy file", 
		description="You must keep this enable as your system \
				don't implement symbolic link. disable at your one risk!",
		options = {'LIBRARY_EDITABLE'},
		default = True)



class CtFRefreshMiniMaxi(bpy.types.Operator):
	'''operator to initialize or refresh CtF info of a movie clip'''
	bl_idname = "ctf.refresh_mini_maxi"
	bl_label= "get curve mini and maxi value has mini/maxi settings"
	bl_options = {'INTERNAL'}
	
	def execute(self, context):
		'''get curve mini and maxi value has mini/maxi settings'''
		clip = context.space_data.clip
		
		fCurve = getFCurveByDataPath(clip, 'CtF.amplitude')
		if(fCurve is None):
			m = M = self.curve
		else:
			clip.CtF.mini, clip.CtF.maxi = getCurveLimit(fCurve)
		
		# update curves
		update_curves(clip.CtF, context)
		
		return {'FINISHED'}



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



class CtFCurvesRefresh(bpy.types.Operator):
	'''operator to initialize or refresh CtF info of a movie clip'''
	bl_idname = "ctf.curves_refresh"
	bl_label= "refresh peaks"
	bl_options = {'INTERNAL'}
	
	def execute(self, context):
		'''refresh clip peaks'''
		update_curves(context.space_data.clip.CtF, context)
		return {'FINISHED'}


def getFCurveByDataPath(ob, path):
	'''Return object fcurve corresponding to datapath or None'''
	
	if(ob.animation_data is None or ob.animation_data.action is None):
		return None
	
	for curve in ob.animation_data.action.fcurves:
		if curve.data_path == path:
			return curve
	return None


def checkCtFDriver(ob):
	'''check the object have no driver on property used by the addon'''
	if(		ob.animation_data is None
			or ob.animation_data.drivers is None):
		return False
	
	for driver in ob.animation_data.drivers:
		if( driver.data_path.startswith('CtF.') ):
			return True
	
	return False


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
	'''check that start and end frame are valid when 
			changing end frame settings'''
	# check end isn't over clip size
	if self.end > self.size:
		self.end = self.size
	
	# check start isn't over end
	if self.start >= self.end:
		if self.end > 1:
			self['start'] = self.end - 1
		else:
			self['start'] = 1
			self['end'] = 2
	


def set_start_frame(self, context):
	'''check that start and end frame are valid 
			when changing start frame settings'''
	# check start isn't under 0
	if self.start < 1:
		self.start = 1
	
	# check start isn't over end
	if self.start >= self.end:
		if self.start < self.size:
			self['end'] = self.start + 1
		else:
			self['start'] = self.size - 1
			self['end'] = self.size
	



def set_mini(self, context):
	'''check that maxi value are greater than maxi value 
			when editing mini value'''
	if self.mini > self.maxi:
		self['maxi'] = self.mini
	



def set_maxi(self, context):
	'''check that maxi value are greater than maxi value
			when editing maxi value'''
	if self.mini > self.maxi:
		self['mini'] = self.maxi
	


def update_curves(self, context):
	'''update curve when settings have been changed'''
	clip = context.space_data.clip
	#############################################
	##    update amplification net curve        ##
	#############################################
	# determine frame working space and frame step
	frame = start = floor(context.scene.frame_start - 5)
	end = ceil(context.scene.frame_end + 5)
	
	# get and erase amplitude_net fcurve
	amplitude_net_curve = getFCurveByDataPath(clip, 
									'CtF.amplitude_net')
	if amplitude_net_curve is not None:
		hide = amplitude_net_curve.hide
		clip.animation_data.action.fcurves.remove(amplitude_net_curve)
	else:
		hide = True
	clip.animation_data.action.fcurves.new('CtF.amplitude_net')
	amplitude_net_curve = getFCurveByDataPath(clip,
									'CtF.amplitude_net')
	
	# get amplitude fcurve
	raw_curve = getFCurveByDataPath(clip, 'CtF.amplitude')
	raw_value = clip.CtF.amplitude
	
	# get mini and maxi fcurve
	mini_curve = getFCurveByDataPath(clip, 'CtF.mini')
	mini_value = clip.CtF.mini
	maxi_curve = getFCurveByDataPath(clip, 'CtF.maxi')
	maxi_value = clip.CtF.maxi
	
	# generate amplitude_net curve
	while( frame <= end ):
		# get mini value at this frame
		if mini_curve is not None:
			mini_value = mini_curve.evaluate(frame)
		
		# get maxi value at thes frame
		if maxi_curve is not None:
			maxi_value = maxi_curve.evaluate(frame)
		
		# get amplitude raw value
		if raw_curve is not None:
			raw_value = raw_curve.evaluate(frame)
		
		#compute net value
		if raw_value <= mini_value:
			net_amplitude_value = 0
		elif raw_value >= maxi_value:
			net_amplitude_value = 1
		else:
			net_amplitude_value = ( raw_value - mini_value )\
									/( maxi_value - mini_value )
		
		# create keyframe
		amplitude_net_curve.keyframe_points.insert(frame,
							net_amplitude_value)
		
		frame += 1
	
	# prevent curve edition
	amplitude_net_curve.lock = True
	amplitude_net_curve.hide = hide
	
	
	#############################################
	##       update peaks curve                ##
	#############################################
	# remove old peaks
	peaks_curve = getFCurveByDataPath(clip, 'CtF.peaks')
	if peaks_curve is not None:
		hide = peaks_curve.hide
		clip.animation_data.action.fcurves.remove(peaks_curve)
	else:
		hide = True
	
	# create new peaks
	clip.animation_data.action.fcurves.new('CtF.peaks')
	peaks_curve = getFCurveByDataPath(clip, 'CtF.peaks')
	
	# get frame rate and start/end frame
	fps = context.scene.render.fps
	frame = start = context.scene.frame_start
	end = context.scene.frame_end
	
	# get ppm curve and default value
	ppm_curve = getFCurveByDataPath(clip, 'CtF.ppm')
	ppm_value = clip.CtF.ppm
	value = 0
	if ppm_curve is None and clip.CtF.ppm <= 0:
		# ppm isn't animate and is equal to 0, peaks always equal 1
		peaks_curve.keyframe_points.insert(0, 1)
	else:
		while(frame < end):
			# get ppm value at this frame
			if ppm_curve is not None:
				ppm_value = ppm_curve.evaluate(frame)
			
			if(ppm_value > 0):
				# add keyframe
				peaks_curve.keyframe_points.insert(frame, value)
				peaks_curve.keyframe_points[-1].interpolation = 'LINEAR'
				
				# next frame
				interval = 60 / ppm_value * fps / 2
				frame += interval
				
				# invert value
				if value == 0:
					value = 1
				else:
					value = 0
			else:
				value = 0
				frame += 0.01
		
		# add last keyframe
		peaks_curve.keyframe_points.insert(frame, value)
		peaks_curve.keyframe_points[-1].interpolation = 'LINEAR'
	
	# prevent curve edition
	peaks_curve.lock = True
	peaks_curve.hide = hide
	
	
	#############################################
	##       update combined curve             ##
	#############################################
	
	# get amplitude mode curve
	amp_mode = clip.CtF['amplitude_mode']
	amp_mode_curve = getFCurveByDataPath(clip, 
							'CtF.amplitude_mode')
	
	# get and initialize combination curve
	combination_curve = getFCurveByDataPath(clip, 
							'CtF.combination')
	if combination_curve is not None:
		hide = combination_curve.hide
		clip.animation_data.action.fcurves.remove(combination_curve)
	else:
		hide = True
	clip.animation_data.action.fcurves.new(
								'CtF.combination')
	combination_curve = getFCurveByDataPath(clip, 
								'CtF.combination')
	
	if ppm_curve is None and clip.CtF.ppm <= 0:
		for keyframe in amplitude_net_curve.keyframe_points:
			combination_curve.keyframe_points.insert(
										keyframe.co[0],
										keyframe.co[1]
										)
	else:
		# loop only on peak curve keyframe
		for keyframe in peaks_curve.keyframe_points:
			# get peaks keyframe value and frame
			frame = keyframe.co[0]
			value = keyframe.co[1]
			
			# get amplitude_mode at this frame
			if amp_mode_curve is not None:
				amp_mode = amp_mode_curve.evaluate(frame)
			
			# generate keyframe
			if amp_mode != 3 : # «amplitude mode == multiply or clamp
				value = value * amplitude_net_curve.evaluate(frame)
			combination_curve.keyframe_points.insert(frame, value)
		
		
		# loop for all frame
		end = frame # consider peaks last keyframe as end 
		frame = start
		while frame <= end:
			# get peaks value
			value = peaks_curve.evaluate(frame)
			
			# get amplitude_mode at this frame
			if amp_mode_curve is not None:
				amp_mode = amp_mode_curve.evaluate(frame)
			
			if amp_mode == 0 : # amplitude mode is «multiply»
				value = value * amplitude_net_curve.evaluate(frame)
			
			# generate keyframe if amplitude mode 
			# is not «ignore» or «clamp_key»
			if amp_mode not in [ 1, 3]:
				combination_curve.keyframe_points.insert(frame, value)
			
			# next frame
			frame += 1
	
	# prevent curve edition
	combination_curve.lock = True
	combination_curve.hide = hide
	
	
	#############################################
	##    update output frame curve            ##
	#############################################
	# get and initialize output curve
	output_curve = getFCurveByDataPath(clip, 'CtF.output')
	if output_curve is not None:
		hide = output_curve.hide
		clip.animation_data.action.fcurves.remove(output_curve)
	else:
		hide = True
	clip.animation_data.action.fcurves.new('CtF.output')
	output_curve = getFCurveByDataPath(clip, 'CtF.output')
	
	# get start and end curve
	start_curve = getFCurveByDataPath(clip, 'CtF.start')
	end_curve = getFCurveByDataPath(clip, 'CtF.end')
	
	# generate first keyframe
	output_curve.keyframe_points.insert( start - 1, 0 )
	output_curve.keyframe_points[-1].interpolation = 'LINEAR'
	
	# get rounding method
	if(clip.CtF.rounding == 'round'):
		rounding = round
	elif(clip.CtF.rounding == 'floor'):
		rounding = floor
	else:
		rounding = ceil
	
	# generate a keyframe at each frame 
	frame = start
	end = context.scene.frame_end
	while frame <= end:
		# get start value at this frame
		if start_curve is not None:
			start_value = start_curve.evaluate(frame)
		else:
			start_value = clip.CtF.start
		
		# check start_value
		if start_value < 1 :
			start_value = 1
		elif start_value > clip.CtF.size:
			start_value = clip.CtF.size
		
		# get end value at this frame
		if end_curve is not None:
			end_value = end_curve.evaluate(frame)
		else:
			end_value = clip.CtF.end
		
		# check end_value
		if end_value < start_value :
			end_value = start_value
		elif end_value > clip.CtF.size:
			end_value = clip.CtF.size
		
		# generate keyframe
		output_frame = rounding(
				clip.CtF.first + start_value - 1 
				+ combination_curve.evaluate(frame)
				* (end_value - start_value)
				)
		output_curve.keyframe_points.insert( frame, output_frame )
		
		
		# next frame
		frame += 1
	
	# generate last keyframe
	output_curve.keyframe_points.insert( frame , 0 )
	output_curve.keyframe_points[-1].interpolation = 'LINEAR'
	
	# prevent curve edition
	output_curve.lock = True
	output_curve.hide = hide


class CtF(bpy.types.PropertyGroup):
	''' class containang all MovieClip Property 
			design form CtF addon'''
	
	# flag to know if CtF have been initialize on this MovieClip
	init = bpy.props.BoolProperty(default = False)
	
	path = bpy.props.StringProperty() # The sources directory path
	prefix = bpy.props.StringProperty() # the source name prefix
	suffix = bpy.props.StringProperty() # the source name suffix
	numberSize = bpy.props.IntProperty() # the source name frame number size in char
	first = bpy.props.IntProperty() # the first frame number (in source file name)
	last = bpy.props.IntProperty() # the last frame number (in source file name)
	
	# first frame of the clip to use
	start = bpy.props.IntProperty(
		name = "First frame",
		description = "first frame that Frames Animated \
					By Curve add-on must take in count",
		default = 1,
		min = 1,
		update = set_start_frame)
	
	# last frame of the clip to use
	end = bpy.props.IntProperty(
		name = "Last frame",
		description = "last frame that Frames Animated \
					By Curve add-on must take in count",
		update = set_end_frame)
	
	
	size = bpy.props.IntProperty() # number of frame of the sequence
	ext = bpy.props.StringProperty() # extension of source file
	
	# amplitude property
	amplitude = bpy.props.FloatProperty(
		name = 'amplitude (raw)',
		description = 'Determined the frame of the Movie \
								clip to use at each frame',
		default = 0.0
		)
	amplitude_net = bpy.props.FloatProperty(
		name = 'amplitude (net)',
		description = 'show the apply of mini and maxi to \
							amplitude raw. Can\'t be edit.',
		)
	amplitude_mode = bpy.props.EnumProperty(
		name = 'amplitude mode',
		description = 'the way to use amplitude associated with peaks',
		default = 'multiply',
		items = [
#			(identifier,			name,
#				description, number)
			
			('multiply',		'Peaks Curve Multiplied by amplitude',
				'peaks is multiplied by \
				amplitude percentage of maxi',				0),
			
			('clamp_key',		'Peaks Keyframe Clamped to amplitude',
				'peaks keyframe is clamped by amplitude',		1),
			
#			('clamp_curve',		'Peaks Curve Clamped to amplitude',
#				'all peaks value is clamped by amplitude',		2),
#			
			('ignore',			'Peaks Curve Ignore amplitude',
				'Peaks amplitude are always 1',			3)
			
			]
		)
	
	# min value associated to the first frames
	mini = bpy.props.FloatProperty(
		name = 'Mini',
		description = 'the minimal value of the \
						amplitude curve, all smaller\
						 value will display the first frame',
		default = 0.0,
		update = set_mini
		)
	
	# max value associated to the last frames
	maxi = bpy.props.FloatProperty(
		name = 'maxi',
		description = 'the maximal value of the amplitude\
						 curve. All bigger value will display \
						the last frame. This property is useless \
						when amplitude is ignored.',
		default = 1.0,
		update = set_maxi
		)
	
	# Rounding method
	rounding = bpy.props.EnumProperty(
		name = 'Rounding method',
		description = 'the rounding method use by the \
						script to round the float computed \
						value into a integer value corresponding \
						to a frame',
		options = {'LIBRARY_EDITABLE'},
		default = 'round',
		items = [
			#(identifier,	name, 		description )
			('round',		'round',	'the closest integer.'),
			('ceil',		'ceil',		'the closest greater integer'),
			('floor',		'floor',		'the closest smaller integer')
			]
		)
	
	# destination sub directory name
	destination = bpy.props.StringProperty(
		name = "Destination subdirectory",
		description = "The name of the directory (create \
						in the source directory) where \
						generated file gone be.",
		default = "CtFOutput" )
	
	# peaks per minute settings and curve
	ppm = bpy.props.FloatProperty(
		name = "ppm",
		description = "peaks per minute",
		default = 0,
		min = 0)
	peaks = bpy.props.FloatProperty(
		name = "peaks",
		description = "Only to visualize the peaks curve. \
					Can't be edit manually: use ppm settings.",
		default = 1,
		min = 0,
		max = 1)
	combination = bpy.props.FloatProperty(
		name = "combination",
		description = "Only to visualize the combination of \
					peaks and amplitude curve curve. Can't \
					be edit manually: use ppm and amplitude settings.",
		default = 0,
		min = 0,
		max = 1)
	output = bpy.props.IntProperty(
		name = "output frame",
		description = "Only to visualize the output frames. \
						Can't be edit manually.")
	
	
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
			warning = False
			# Display the directory path
			row = layout.row()
			col = row.column()
			col.label( text = "Frame Directory path:" )
			col = row.column()
			col.operator(
				"ctf.refresh",
				icon = 'FILE_REFRESH',
				text = '')
			row = layout.row()
			row.label( text= self.path )
			
			# Display frame extension
			row = layout.row()
			col = row.column()
			col.label( text="File type: "+self.ext )
			
			# Display first to last accepted frame name range
			col = row.column()
			col.label( text="Valid frames: "\
				+self.getFrameName(self.first)+' to '\
				+self.getFrameName(self.last) )
			
			# Display Start/End settings
			layout.separator()
			row = layout.row()
			col = row.column()
			col.prop(self, "start")
			col = row.column()
			col.prop(self, "end")
			
			# A float amplitude field
			layout.separator()
			row = layout.row()
			col = row.column()
			col.prop(self, "amplitude")
			
			# A field to remind F-Curve min and max value
			fCurve = getFCurveByDataPath(clip, 'CtF.amplitude')
			if(fCurve is None):
				m = M = self.amplitude
			else:
				m, M = getCurveLimit(fCurve)
			m = round(m*1000)/1000
			M = round(M*1000)/1000
			col = row.column()
			col.label( text = "(Goes from "+str(m)\
						+" to "+str(M)+')' )
			
			# A field to set the min F-Curve Value to 
			# assigne to the first frames
			row = layout.row()
			col = row.column()
			col.prop(self, "mini")
			
			# A field to set the max F-Curve Value to 
			# assigne to the last frames
			col = row.column()
			col.prop(self, "maxi")
			if(self.amplitude_mode == 'ignore'):
				col.enabled = False
			
			# A button to get curve min max value
			col = row.column()
			col.operator('ctf.refresh_mini_maxi',
						icon='FILE_REFRESH',
						text = '')
			col = row.column()
			col.enabled = False
			col.prop(self, "amplitude_net")
			col = row.column()
			col.operator(
				"ctf.curves_refresh",
				text='',
				icon='FILE_REFRESH')
			
			# a button to activate and set peaks per minute feature
			layout.separator()
			row = layout.row()
			col = row.column()
			col.prop(self, "ppm")
			col = row.column()
			col.enabled = False
			col.prop(self, "peaks")
			col = row.column()
			col.operator(
				"ctf.curves_refresh",
				text='',
				icon='FILE_REFRESH')
			
			# set combination mode
			layout.separator()
			row = layout.row()
			if getFCurveByDataPath(clip, 'CtF.ppm') is None \
					and clip.CtF.ppm <= 0:
				row.enabled = False
			row.prop(self, 'amplitude_mode')
			
			# visualize combination of peaks and amplitude curve
			row = layout.row()
			col = row.column()
			col.enabled = False
			col.prop(self, "combination")
			
			# visualize output frame
			col = row.column()
			col.enabled = False
			col.prop(self, "output")
			
			# refresh curve
			col = row.column()
			col.operator(
				"ctf.curves_refresh",
				text='',
				icon='FILE_REFRESH')
			
			# A field to choose between Round Floor and 
			# Ceil rounding method
			layout.separator()
			row = layout.row()
			col = row.column()
			col.prop(self, "rounding")
			
			# A checkbox to get real frame file copy
			
			col = row.column()
			if(not context.scene.CtFRealCopy \
					and platform.system().lower() not in\
								['linux', 'unix']):
				col.prop(context.scene, "CtFRealCopy", icon='ERROR')
				warning = True
			else:
				col.prop(context.scene, "CtFRealCopy")
			
			# A field to set the name of the sub 
			# directory name to use as destination
			row = layout.row()
			col = row.column()
			col.prop(self, "destination")
			if(os.path.exists(self.path+self.destination)\
				and os.path.isdir(self.path+self.destination)):
				if(not os.access(self.path+self.destination, os.W_OK)):
					warning = True
					col = row.column()
					col.label(text='no permission', icon='ERROR')
				elif(len(os.listdir(self.path+self.destination))>0):
					warning = True
					col = row.column()
					col.label(text='content could be erased', icon='ERROR')
			
			# the button to run the script
			if(checkCtFDriver(clip)):
				row = layout.row()
				row.label(text='This function can\'t be used with driver!', 
							icon='ERROR')
			elif(warning):
				row = layout.row()
				row.operator(
					"curve.toframe",
					text="ignore warning and run at my one risk",
					icon = 'ERROR')
			else:
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
		settings = clip.CtF
		update_curves(settings, context)
		
		# check output method
		if(context.scene.CtFRealCopy):
			output = shutil.copyfile
		else:
			output = os.symlink
		
		# get destination directory name
		dst = settings.path + settings.destination
		if(dst[-1] != '/'):
			dst += '/'
		
		# check destination directory exist, is writable and purge it
		if( os.path.exists( dst ) ):
			# check destination directory access
			if(os.access(dst, os.W_OK)):
				# clear content
				for f in os.listdir(dst):
					if(	f.endswith(settings.ext)
						and os.path.islink(dst+f)
						or ( os.path.isfile(dst+f)
						and os.access(dst+f, os.W_OK) )
						):
						os.remove(dst+f)
			else:
				# report error then quit 
				self.report(	{'ERROR'},
								'No write access to destination directory' )
				return {'CANCELLED'}
		else:
			# create directory
			try:
				os.mkdir(dst)
			except OSError as e:
				self.report({'ERROR'}, 
						'impossible to create destination\
							 directory :'+e.strerror)
				return {'CANCELLED'}
		
		
		# loop from start frame to end frame
		current = context.scene.frame_current
		for frame in range(
						context.scene.frame_start, 
						context.scene.frame_end + 1):
			# set current frame and update property value
			context.scene.frame_set(frame)
			
			# get output frame
			fr = clip.CtF.output
			
			# copy (or symlink) the corresponding 
			# frame into the destination path
			try:
				output( settings.path + clip.CtF.getFrameName(fr),
						dst + clip.CtF.getFrameName(context.scene.frame_current)
						)
			except OSError as e:
				self.report({'ERROR'}, 
						'error while copying file: '\
							+e.strerror+'. Abort action.')
				context.scene.frame_set(current)
				return {'CANCELLED'}
		
		context.scene.frame_set(current)
		
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
			row.label( text="select/load an images sequence \
					in Movie Editor.", icon="ERROR" )
			row = layout.row()
			row.operator(
				"ctf.refresh",
				text="Refresh MovieClip info")
		


def register():
	'''addon register'''
	bpy.utils.register_class(CtFRefresh)
	bpy.utils.register_class(CtFRefreshMiniMaxi)
	bpy.utils.register_class(CtFCurvesRefresh)
	bpy.utils.register_class(CtF)
	bpy.types.MovieClip.CtF = bpy.props.PointerProperty(type=CtF)
	bpy.utils.register_class(CurveToFrame)
	bpy.utils.register_class(FramesAnimatedByCurvePanel)
	print("Frames Animated By Curve is enabled")


def unregister():
	'''addon unregister'''
	bpy.utils.unregister_class(CtFRefresh)
	bpy.utils.unregister_class(CtFRefreshMiniMaxi)
	bpy.utils.unregister_class(CtFCurvesRefresh)
	bpy.utils.unregister_class(CtF)
	bpy.utils.unregister_class(FramesAnimatedByCurvePanel)
	bpy.utils.unregister_class(CurveToFrame)
	print("Frames Animated By Curve is disabled")

