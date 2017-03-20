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
from math import ceil, floor, radians
from mathutils import Euler, Vector
from uuid import uuid4

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



class CtFRefreshClipMiniMaxi(bpy.types.Operator):
	'''operator to initialize or refresh CtF info of a movie clip'''
	bl_idname = "ctf.refresh_movieclip_mini_maxi"
	bl_label= "get movieclip amplitude curve mini and maxi value"
	bl_options = {'INTERNAL'}
	
	def execute(self, context):
		'''get movieclip amplitude curve mini and maxi value'''
		clip = context.space_data.clip
		
		fCurve = getFCurveByDataPath(clip, 'CtF.amplitude')
		if(fCurve is None):
			m = M = clip.CtF.amplitude
		else:
			clip.CtF.mini, clip.CtF.maxi = getCurveLimit(fCurve)
		
		# update curves
		update_curves(clip.CtF, context)
		
		return {'FINISHED'}



class CtFRefreshSceneMiniMaxi(bpy.types.Operator):
	'''operator to initialize or refresh CtF info of the scene'''
	bl_idname = "ctf.refresh_scene_mini_maxi"
	bl_label= "get scene amplitude curve mini and maxi value"
	bl_options = {'INTERNAL'}
	
	def execute(self, context):
		'''get scene amplitude curve mini and maxi value'''
		scene = context.scene
		
		fCurve = getFCurveByDataPath(scene, 'CtF.amplitude')
		if(fCurve is None):
			m = M = scene.CtF.amplitude
		else:
			scene.CtF.mini, scene.CtF.maxi = getCurveLimit(fCurve)
		
		# update curves
		update_curves(scene.CtF, context)
		
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
		
		# allocate an uid to the clip
		if(clip.CtF.uid == '' ):
			clip.CtF.uid = str(uuid4())
		
		
		return {'FINISHED'}



class CtFSimpleTrackCurvesRefresh(bpy.types.Operator):
	'''operator to initialize or refresh CtF info of a movie clip'''
	bl_idname = "ctf.simple_track_curves_refresh"
	bl_label= "refresh movieclip curves"
	bl_options = {'INTERNAL'}
	
	def execute(self, context):
		'''refresh clip curves'''
		update_curves(context.space_data.clip.CtF, context)
		return {'FINISHED'}




class CtFMultiTrackCurvesRefresh(bpy.types.Operator):
	'''operator to initialize or refresh CtF info of the scene'''
	bl_idname = "ctf.multi_track_curves_refresh"
	bl_label= "refresh multi track curves"
	bl_options = {'INTERNAL'}
	
	def execute(self, context):
		'''refresh scene curves'''
		update_curves(context.scene.CtF, context)
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
	ob = self.id_data
	
	# initialize animation data if required
	if ob.animation_data is None:
		ob.animation_data_create()
	
	if ob.animation_data.action is None:
		ob.animation_data.action = bpy.data.actions.new( 
									name= ob.name+'Action')
	
	# update amplitude net curve
	amplitude_net_curve = self.update_net_amplitude_curve( ob, context )
	
	# update peaks curve
	peaks_curve = self.update_peaks_curve(ob, context, amplitude_net_curve)
	
	#update combination curve
	combination_curve = self.update_combination_curve(
											ob, 
											context, 
											amplitude_net_curve,
											peaks_curve
											)
	
	if(type(ob) is bpy.types.MovieClip ):
		# update output curve
		self.update_output_curve(ob, context, combination_curve)
	




def set_peak_interpolation(keyframe, clip, left_ref, right_ref):
	'''set peaks keyframe interpolation depending on settings'''
	# get keyframe frame
	frame = keyframe.co[0]
	
	# get top «same» settings
	curve = getFCurveByDataPath(clip, 'CtF.top_interpolation_same')
	if curve is None:
		same = clip.CtF.top_interpolation_same
	else:
		same = curve.evaluate(frame)
	
	# determine wich interpolation settings to use
	if (keyframe.co[1] != 1 or same):
		kind = 'main'
	else:
		kind = 'top'
	
	
	# get interpolation mode:
	curve = getFCurveByDataPath(clip, 'CtF.'+kind+'_interpolation')
	if curve is None:
		enum = clip.CtF.bl_rna.properties[kind+'_interpolation'].enum_items
		interpolation = enum.find( clip.CtF.path_resolve(kind+'_interpolation') )
	else:
		interpolation = curve.evaluate(frame)
	
	if interpolation == 0:
		# linear interpolation
		keyframe.interpolation = 'LINEAR'
	elif interpolation >=3:
		# easing interpolation
		if interpolation == 3:
			keyframe.interpolation = 'SINE'
		elif interpolation == 4:
			keyframe.interpolation = 'QUAD'
		elif interpolation == 5:
			keyframe.interpolation = 'CUBIC'
		elif interpolation == 6:
			keyframe.interpolation = 'QUART'
		elif interpolation == 7:
			keyframe.interpolation = 'QUINT'
		elif interpolation == 8:
			keyframe.interpolation = 'EXPO'
		elif interpolation == 9:
			keyframe.interpolation = 'CIRC'
		
		# get easing setting
		curve = getFCurveByDataPath(clip, 'CtF.'+kind+'_easing')
		if curve is None:
			enum = clip.CtF.bl_rna.properties[kind+'_easing'].enum_items
			easing = enum.find( clip.CtF.path_resolve(kind+'_easing') )
		else:
			easing = curve.evaluate(frame)
		
		# set keyframe easing mode
		if easing == 0:
			keyframe.easing = 'AUTO'
		elif easing == 1:
			keyframe.easing = 'EASE_IN_OUT'
		elif easing == 2:
			keyframe.easing = 'EASE_IN'
		elif easing == 3:
			keyframe.easing = 'EASE_OUT'
		
	else:
		# Bezier interpolation
		keyframe.interpolation = 'BEZIER'
		
		if interpolation == 1:
			# interpolation Bezier Auto
			keyframe.handle_left_type = 'AUTO_CLAMPED'
			keyframe.handle_right_type = 'AUTO_CLAMPED'
		else:
			# interpolation Bezier Free handle
			keyframe.handle_left_type = 'FREE'
			keyframe.handle_right_type = 'FREE'
		
		
		# get left handle length
		curve = getFCurveByDataPath(clip, 'CtF.'+kind+'_left_length')
		if curve is None:
			left_length =  clip.CtF.path_resolve(kind+'_left_length')
		else:
			left_length = curve.evaluate(frame)
		
		# get left handle angle
		curve = getFCurveByDataPath(clip, 'CtF.'+kind+'_left_angle')
		if curve is None:
			left_angle = clip.CtF.path_resolve(kind+'_left_angle')
		else:
			left_angle = curve.evaluate(frame)
		
		
		# get right auto setting
		curve = getFCurveByDataPath(clip, 'CtF.'+kind+'_right_auto')
		if curve is None:
			right_auto = clip.CtF.path_resolve(kind+'_right_auto')
		else:
			right_auto = curve.evaluate(frame)
		
		
		if right_auto:
			# auto set right length and angle
			right_length = left_length
			right_angle = left_angle
		else:
			# get right handle length
			curve = getFCurveByDataPath(clip, 'CtF.'+kind+'_right_length')
			if curve is None:
				right_length = clip.CtF.path_resolve(kind+'_right_length')
			else:
				right_length = curve.evaluate(frame)
			
			# get right handle angle
			curve = getFCurveByDataPath(clip, 'CtF.'+kind+'_right_angle')
			if curve is None:
				right_angle = clip.CtF.path_resolve(kind+'_right_angle')
			else:
				right_angle = curve.evaluate(frame)
		
		# apply reference length
		left_length *= -left_ref
		right_length *= right_ref
		
		# convert angle to radians
		if (keyframe.co[1] == 1 ):
			left_angle = radians(left_angle)
			right_angle = -radians(right_angle) # invert rotation
		else:
			left_angle = -radians(left_angle) # invert rotation
			right_angle = radians(right_angle)
		
		
		# compute and set left handle vector
		vector = Vector( ( left_length, 0, 0 ) )
		vector.rotate( Euler( ( 0, 0, left_angle ) ) )
		vector.resize(2)
		vector.x += frame
		vector.y += keyframe.co[1]
		keyframe.handle_left = vector
		
		# compute and set right handle vector
		vector = Vector( ( right_length, 0, 0 ) )
		vector.rotate( Euler( ( 0, 0, right_angle ) ) )
		vector.resize(2)
		vector.x += frame
		vector.y += keyframe.co[1]
		keyframe.handle_right = vector
		




class Track(bpy.types.PropertyGroup):
	''' managing CtF track Identification'''
	name = bpy.props.StringProperty()
	uid = bpy.props.StringProperty()
	
	
	
	def draw ( self, layout ):
		'''draw Track info and settings'''
		return
	
	
	
	def get( self, scene, rename = False):
		'''return the movie clip corresponding to this track'''
		track = bpy.data.movieclips[ self.name ]
		if track.CtF.uid == self.uid:
			return track
		
		for track in scene.movieclips:
			if track.CtF.uid == self.uid:
				
				if rename:
					try:
						self.name = track.name
					except AttributeError:
						print('Track renaming error on '+self.name)
				
				return track
		
		return None




class CtF(bpy.types.PropertyGroup):
	''' class containing all MovieClip Property 
			design form CtF addon'''
	
	# flag to know if CtF have been initialize on this MovieClip
	init = bpy.props.BoolProperty(default = False)
	uid = bpy.props.StringProperty( default = '' )
	
	#################################################
	##     clip settings                           ##
	#################################################
	
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
	
	#################################################
	##     amplitude settings                      ##
	#################################################
	# amplitude property
	amplitude = bpy.props.FloatProperty(
		name = 'amplitude (raw)',
		description = 'Determined the frame of the Movie \
								clip to use at each frame',
		default = 0.0
		)
	
	# amplitude after applying min and max value
	amplitude_net = bpy.props.FloatProperty(
		name = 'amplitude (net)',
		description = 'show the apply of mini and maxi to \
							amplitude raw. Can\'t be edit.',
		)
	
	# method used to combine amplitude and peaks curve
	combination_mode = bpy.props.EnumProperty(
		name = 'combination mode',
		description = 'the way to combine amplitude and peaks curve',
		default = 'multiply',
		items = [
#			(identifier,			name,
#				description, number)
			
			('multiply',		'Peaks Curve Multiplied by amplitude',
				'peaks is multiplied by \
				amplitude percentage of maxi',				0),
			
			('clamp_key',		'Peaks Keyframe Clamped to amplitude',
				'peaks keyframe is clamped by amplitude',		1),
			
			('clamp_curve',		'Peaks Curve Clamped to amplitude',
				'all peaks value is clamped by amplitude',		2),
			
			('ignore_amplitude',			'Only use peaks curve',
				'Only use peaks curve',			3),
			
			('ignore_peaks',			'Only use amplitude curve',
				'Only use amplitude curve',			4)
			
			],
		update = update_curves
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
	
	#################################################
	##     peaks settings                          ##
	##       count and synchronization             ##
	#################################################
	
	# peaks per minute settings
	ppm = bpy.props.FloatProperty(
		name = "ppm",
		description = "peaks per minute",
		default = 0)
	
	# automatically use constant for ppm curve interpolation
	auto_constant = bpy.props.BoolProperty(
		name="constant", 
		description="While animating pmm value, it's highly recommanded to use constant interpolation for all keyframe. This option automatically do the convertion.",
		options = {'LIBRARY_EDITABLE'},
		default = True)
	
	# synchronize peak with amplitude bounce
	synchronized = bpy.props.BoolProperty(
		name="Sync to amplitude", 
		description="Peaks timing are synchronized with amplitude varying around 0.",
		options = {'LIBRARY_EDITABLE'},
		default = False)
	
	# accuracy of peak synchronisation
	accuracy = bpy.props.FloatProperty(
		name = "accuracy",
		description = "gap between two evaluation of ppm to check if ppm<=0",
		options = {'LIBRARY_EDITABLE'},
		default = 0.1,
		min = 0.00001,
		max = 1)
	
	# anticipate amplitude rebounce when synchronized
	anticipate = bpy.props.FloatProperty(
		name = "anticipate",
		description = "With sync to amplitude, start peaks a little before amplitude rise over 0. \n0 mean the peaks will start exactly when amplitude start to be over 0.\n1 mean the peaks zenit will be exactly when amplitude start to be over 0.",
		default = 1,
		min = 0,
		max = 1)
	
	# peaks curve obtain by applying settings
	peaks = bpy.props.FloatProperty(
		name = "peaks",
		description = "Only to visualize the peaks curve. \
					Can't be edit manually: use ppm settings.",
		default = 1,
		min = 0,
		max = 1)
	
	#################################################
	##     peaks settings                          ##
	##       main interpolation settings           ##
	#################################################
	# interpolation mode
	interpolation_enum = [
#			(identifier,			name,
#				description, icon, number)
			
			('linear',		'Linear',
				'Straight-line interpolation',
				'IPO_LINEAR',			0),
			
			('bezier auto',		'Bezier (Auto Handle)',
				'Bezier interpolation with handle automatically set',
				'IPO_BEZIER',			1),
			
			('bezier free',		'Bezier (Free Handle)',
				'Bezier interpolation with free handle',
				'IPO_BEZIER',			2),
			
			('sinusoidal',		'Sinusoidal',
				'Sinusoidal easing',
				'IPO_SINE',			3),
			
			('quad',		'Quadratic',
				'Quadratic easing',
				'IPO_QUAD',			4),
			
			('cubic',		'Cubic',
				'Cubic easing',
				'IPO_CUBIC',			5),
			
			('quartic',		'Quartic',
				'Quartic easing',
				'IPO_QUART',			6),
			
			('quintic',		'Quintic',
				'Quintic easing',
				'IPO_QUINT',			7),
			
			('exponential',		'Exponential',
				'Exponential easing',
				'IPO_EXPO',			8),
			
			('circular',		'Circular',
				'Circular easing',
				'IPO_CIRC',			9)
			
			]
	main_interpolation =  bpy.props.EnumProperty(
		name = 'Interpolation',
		description = 'Peaks keyframe interpolation mode',
		default = 'linear',
		items = interpolation_enum,
		update = update_curves
		)
	
	
	# easing mode (not for Bezier/linear interpolation)
	easing_enum = [
#			(identifier,			name,
#				description, icon, number)
			
			('auto',		'Automatic easing',
				'Automatic easing',
				'IPO_EASE_IN_OUT',			0),
			
			('in&out',		'Ease In & Out',
				'Ease In & Out',
				'IPO_EASE_IN_OUT',			1),
			
			('in',		'Ease In',
				'Ease In',
				'IPO_EASE_IN',			2),
			
			('out',		'Ease Out',
				'Ease Out',
				'IPO_EASE_OUT',			3),
			
			]
	main_easing = bpy.props.EnumProperty(
		name = 'Easing',
		description = 'Easing of interpolation mode',
		default = 'auto',
		items = easing_enum,
		update = update_curves
		)
	
	# left handle size and angle
	main_left_length = bpy.props.FloatProperty(
		name = "L length",
		description = "Length of left handle relative to half the distance with previous keyframe.",
		default = 1,
		min = 0)
	
	main_left_angle = bpy.props.FloatProperty(
		name = "L angle",
		description = "left handle angle, relative to x axis:\n0: point to the left\n90: point to x axis",
		default = 0,
		min = 0,
		max = 90)
	
	
	# right handle free mode, size and angle
	main_right_auto = bpy.props.BoolProperty(
		name="Auto right handle", 
		description="Right handle have the same angle and length that the left one.",
		default = True,
		update = update_curves)
	
	main_right_length = bpy.props.FloatProperty(
		name = "R length",
		description = "Length of right handle relative to half the distance with next keyframe.",
		default = 1,
		min = 0)
	
	main_right_angle = bpy.props.FloatProperty(
		name = "R angle",
		description = "right handle angle, relative to x axis:\n0: point to the right\n90: point to x axis",
		default = 0,
		min = 0,
		max = 90)
	
	
	
	
	
	#################################################
	##     peaks settings                          ##
	##       top peak interpolation settings       ##
	#################################################
	# top peak interpolation independent
	top_interpolation_same = bpy.props.BoolProperty(
		name="Apply to top peaks", 
		description="apply the same interpolation settings to top and bottom peaks.",
		default = True,
		update = update_curves)
	
	# top peak interpolation mode
	top_interpolation =  bpy.props.EnumProperty(
		name = 'Interpolation (top peak)',
		description = 'keyframe interpolation mode (top peak)',
		default = 'linear',
		items = interpolation_enum,
		update = update_curves
		)
	
	
	# top peak easing mode (not for Bezier/linear interpolation)
	top_easing = bpy.props.EnumProperty(
		name = 'Easing (top peak)',
		description = 'Easing of interpolation mode (top peak)',
		default = 'auto',
		items = easing_enum,
		update = update_curves
		)
	
	
	# left handle size and angle
	top_left_length = bpy.props.FloatProperty(
		name = "L length (top peak)",
		description = "Length of left handle relative to half the distance with previous keyframe.",
		default = 1,
		min = 0)
	
	top_left_angle = bpy.props.FloatProperty(
		name = "L angle (top peak)",
		description = "left handle angle, relative to x axis:\n0: point to the left\n90: point to x axis",
		default = 0,
		min = 0,
		max = 90)
	
	
	# right handle free mode, size and angle
	top_right_auto = bpy.props.BoolProperty(
		name="Auto right handle (top peak)", 
		description="Right handle have the same angle and length that the left one.",
		default = True,
		update = update_curves)
	
	top_right_length = bpy.props.FloatProperty(
		name = "R length (top peak)",
		description = "Length of right handle relative to half the distance with next keyframe.",
		default = 1,
		min = 0)
	
	top_right_angle = bpy.props.FloatProperty(
		name = "R angle (top peak)",
		description = "right handle angle, relative to x axis:\n0: point to the right\n90: point to x axis",
		default = 0,
		min = 0,
		max = 90)
	
	
	
	
	
	#################################################
	##     output settings                         ##
	#################################################
	# combination of net amplitude and peaks curves
	combination = bpy.props.FloatProperty(
		name = "combination",
		description = "Only to visualize the combination of \
					peaks and amplitude curve curve. Can't \
					be edit manually: use ppm and amplitude settings.",
		default = 0,
		min = 0,
		max = 1)
	
	# output frame curve
	output = bpy.props.IntProperty(
		name = "output frame",
		description = "Only to visualize the output frames. \
						Can't be edit manually.")
	
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
	
	# output path
	output_path = bpy.props.StringProperty(
		name = "output",
		description = "Output directory path.",
		default = '//',
		subtype = 'DIR_PATH')
	
	
	
	#################################################
	##     Tracks managing                         ##
	#################################################
	track_add = bpy.props.StringProperty(
		name = "Add",
		description = "Add tracks to the list",
		default = '')
	
	tracks = bpy.props.CollectionProperty(
		type=Track,
		options = {'LIBRARY_EDITABLE'} )
	
	
	
	
	
	def getFrameName(self, n):
		'''return the file name of a frame'''
		return	(	self.prefix +
					str(int(n)).rjust(self.numberSize, '0')+
					self.suffix + self.ext	)
	
	
	
	def draw_clip_load_error(self, layout, clip):
		'''draw movieclip load error if required'''
		if(clip.source != 'SEQUENCE'):
			# Display an error message, requesting for a sequence of images
			row = layout.row()
			row.label( text="Current movie can't be use by addon.",
				 icon="ERROR"  )
			row = layout.row()
			row.label( text="Only images sequence are accept." )
			
			return True
			
		elif(not self.init):
			# ask to initialize CtF on thes MovieClip
			row = layout.row()
			row.operator(
				"ctf.refresh",
				text="initialize MovieClip info")
			
			return True
			
		return False
		
	
	
	
	def draw_movieclip_settings(self, layout):
		'''draw Movie info & settings in the panel'''
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
	
	
	
	def draw_amplitude( 
						self,
						layout, 
						ob, 
						refresh_curve, 
						refresh_mini_maxi):
		'''draw amplitude settings into the panel'''
		# A float amplitude field
		layout.separator()
		row = layout.row()
		col = row.column()
		col.prop(self, "amplitude")
		
		# A field to remind F-Curve min and max value
		fCurve = getFCurveByDataPath(ob, 'CtF.amplitude')
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
		if(self.combination_mode == 'ignore_amplitude'):
			col.enabled = False
		
		# A button to get curve min max value
		col = row.column()
		col.operator(refresh_mini_maxi,
					icon='FILE_REFRESH',
					text = '')
		# display net amplitude value
		col = row.column()
		col.enabled = False
		col.prop(self, "amplitude_net")
		col = row.column()
		col.operator(
			refresh_curve,
			text='',
			icon='FILE_REFRESH')
	
	
	
	def draw_peaks(self, layout, refresh_curve):
		'''draw peaks rythm settings into the panel'''
		# a button to activate and set peaks per minute feature
		layout.separator()
		row = layout.row()
		col = row.column()
		col.prop(self, "ppm")
		col = row.column()
		col.prop(self, "auto_constant")
		col = row.column()
		col.prop(self, "accuracy")
		
		row = layout.row()
		col = row.column()
		col.prop(self, "synchronized")
		col = row.column()
		if (not self.synchronized):
			col.enabled = False
		col.prop(self, "anticipate")
		col = row.column()
		col.enabled = False
		col.prop(self, "peaks")
		col = row.column()
		col.operator(
			refresh_curve,
			text='',
			icon='FILE_REFRESH')
	
	
	
	def draw_interpolation_main( self, layout ):
		'''draw peaks interpolation settings (main) into the panel'''
		# keyframes interpolation mode
		layout.separator()
		row = layout.row()
		col = row.column()
		col.prop(self, "main_interpolation", text = '')
		
		# easing mode
		col = row.column()
		col.prop(self, "main_easing", text = '')
		if(self.main_interpolation in [
						'linear',
						'bezier auto',
						'bezier free'] 
						):
			col.enabled = False
		
		# Right auto
		col = row.column()
		col.prop(self, "main_right_auto")
		if (self.main_interpolation != 'bezier free'):
			col.enabled = False
		
		if (self.main_interpolation == 'bezier free'):
			# Left length
			row = layout.row()
			col = row.column()
			col.prop(self, "main_left_length")
			
			# left angle
			col = row.column()
			col.prop(self, "main_left_angle")
			
			if not self.main_right_auto:
				# Right length
				row = layout.row()
				col = row.column()
				col.prop(self, "main_right_length")
				
				# Right angle
				col = row.column()
				col.prop(self, "main_right_angle")
	
	
	
	def draw_interpolation_top( self, layout ):
		'''draw peaks interpolation settings (top) into the panel'''
		# top peak interpolation same as main
		row = layout.row()
		col = row.column()
		col.prop(self, "top_interpolation_same", text = 'Same')
		
		if not self.top_interpolation_same:
			# keyframes interpolation mode
			col = row.column()
			col.prop(self, "top_interpolation", text = '')
			
			# easing mode
			col = row.column()
			col.prop(self, "top_easing", text = '')
			if(self.top_interpolation in [
							'linear',
							'bezier auto',
							'bezier free'] 
							):
				col.enabled = False
			
			# Right auto
			col = row.column()
			col.prop(self, "top_right_auto")
			if (self.top_interpolation != 'bezier free'):
				col.enabled = False
			
			if (self.top_interpolation == 'bezier free'):
				# Left length
				row = layout.row()
				col = row.column()
				col.prop(self, "top_left_length")
				
				# left angle
				col = row.column()
				col.prop(self, "top_left_angle")
				
				if not self.top_right_auto:
					# Right length
					row = layout.row()
					col = row.column()
					col.prop(self, "top_right_length")
					
					# Right angle
					col = row.column()
					col.prop(self, "top_right_angle")
	
	
	
	def draw_combination_and_output( 
						self, 
						layout, 
						refresh_curve, 
						no_output=False ):
		'''draw combination and output settings and value into the panel'''
		# combination mode field
		layout.separator()
		row = layout.row()
		row.prop(self, 'combination_mode')
		
		# visualize combination of peaks and amplitude curve
		row = layout.row()
		col = row.column()
		col.enabled = False
		col.prop(self, "combination")
		
		# visualize output frame
		if not no_output:
			col = row.column()
			col.enabled = False
			col.prop(self, "output")
		
		# refresh curve
		col = row.column()
		col.operator(
			refresh_curve,
			text='',
			icon='FILE_REFRESH')
	
	
	
	def draw_output( self, layout, scene, clip ):
		'''draw rounding & output settings into the panel'''
		warning = False
		# A field to choose between Round Floor and 
		# Ceil rounding method
		layout.separator()
		row = layout.row()
		col = row.column()
		col.prop(self, "rounding")
		
		# A checkbox to get real frame file copy
		col = row.column()
		
		if(not scene.CtFRealCopy \
				and platform.system().lower() not in ['linux', 'unix']):
			col.prop( scene, "CtFRealCopy", icon='ERROR' )
			warning = True
			
		else:
			col.prop( scene, "CtFRealCopy" )
		
		# A field to set the output path
		row = layout.row()
		col = row.column()
		col.prop(self, "output_path")
		path = bpy.path.abspath(self.output_path )
		
		
		return warning
	
	
	
	def draw_run_button( self, layout, ob, warning ):
		'''check situation and draw run button into panel'''
		if(checkCtFDriver(ob)):
			# check no driver is use on CtF property
			row = layout.row()
			row.label(text='This function can\'t be used with driver!', 
						icon='ERROR')
		elif(warning):
			# check there is no warning
			row = layout.row()
			row.operator(
				"curve.toframe",
				text="ignore warning and run at my one risk",
				icon = 'ERROR')
		else:
			# draw standart run button
			row = layout.row()
			row.operator(
				"curve.toframe",
				text="run")
	
	
	
	
	
	def panel_simple(self, context, layout, clip):
		'''draw the CtF panel'''
		# draw movieclip load error if required
		error = self.draw_clip_load_error( layout, clip )
		refresh_curve = "ctf.simple_track_curves_refresh"
		refresh_mini_maxi = "ctf.refresh_movieclip_mini_maxi"
		if not error:
			# draw Movie info & settings
			self.draw_movieclip_settings( layout )
			
			# draw amplitude settings
			self.draw_amplitude( layout, clip, 
								refresh_curve, refresh_mini_maxi )
			
			# draw peaks rythm settings
			self.draw_peaks(layout, refresh_curve )
			
			# draw peaks interpolation main settings
			self.draw_interpolation_main( layout )
			
			# draw peaks interpolation top settings
			self.draw_interpolation_top( layout )
			
			# draw combination node settings and combination and output value
			self.draw_combination_and_output( layout, refresh_curve )
			
			# draw output and rounding settings
			warning = self.draw_output( layout, context.scene, clip )
			
			# draw run button or error message
			self.draw_run_button( layout, clip, warning )
			
			
	
	
	
	def update_net_amplitude_curve( self, clip, context ):
		'''update clip amplitude net curve'''
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
		
		return amplitude_net_curve
	
	
	
	
	def update_peaks_curve(self, clip, context, amplitude_net_curve):
		'''update clip peaks curve'''
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
		# get anticipate curve and default value
		anticipate_curve = getFCurveByDataPath(clip, 'CtF.anticipate')
		anticipate_value = clip.CtF.anticipate
		value = 0
		if ppm_curve is None and clip.CtF.ppm <= 0:
			if clip.CtF.ppm == 0:
				# ppm isn't animate and is equal to 0, peaks always equal 0
				peaks_curve.keyframe_points.insert(0, 0)
			else:
				# ppm isn't animate and is equal to 0, peaks always equal 1
				peaks_curve.keyframe_points.insert(0, 1)
		else:
			# convert all ppm keyframe into constant keyframe
			if ppm_curve is not None and clip.CtF.auto_constant:
				for k in ppm_curve.keyframe_points:
					k.interpolation = 'CONSTANT'
			
			peak = False # did the keyframe is inside a started peak?
			no_amplitude = False
			while(frame < end):
				# get amplitude net value
				amplitude_net = amplitude_net_curve.evaluate(frame)
				
				# get ppm value at this frame
				if ppm_curve is not None:
					ppm_value = ppm_curve.evaluate(frame)
				
				if ppm_value > 0:
					if( clip.CtF.synchronized and no_amplitude):
						if(amplitude_net == 0):
							# finish last peak if needed
							if(peaks_curve.keyframe_points[-1].co[1] == 1):
								peaks_curve.keyframe_points.insert(frame, value)
								peaks_curve.keyframe_points[-1]\
										.interpolation = 'CONSTANT'
								peak = False
							#continue loop
							value = 0
							frame += clip.CtF.accuracy
						else:
							# get anticipate value at this frame
							if anticipate_curve is not None:
								anticipate_value = anticipate_curve\
														.evaluate(frame)
							
							# get interval at this frame
							interval = 60 / ppm_value * fps / 2
							
							# add first peak starting keyframe
							# compute starting frame
							starting_frame = frame - interval * anticipate_value
							last_KF = peaks_curve.keyframe_points[-1].co[0]
							
							# if the starting keyframe must be before
							# the previous keyframe, then previous
							# keyframe is considered as starting keyframe
							if( last_KF > starting_frame ):
								value = peaks_curve.keyframe_points[-1].co[1]
								if value == 0:
									value = 1
								else:
									value = 0
								
								# set keyframe interpolation
								right = interval / 2
								if len(peaks_curve.keyframe_points) > 1:
									left = (last_KF - 
												peaks_curve.keyframe_points[-2].co[0] ) / 2
								else:
									left = right
								set_peak_interpolation(
										peaks_curve.keyframe_points[-1],
										clip,
										left, right)
							else:
								frame = starting_frame
							
							peaks_curve.keyframe_points.insert(frame, value)
							
							# set keyframe interpolation
							left = right = interval / 2
							set_peak_interpolation(
									peaks_curve.keyframe_points[-1],
									clip,
									left, right)
							
							# next frame
							frame += interval
							
							# invert value
							if value == 0:
								value = 1
							else:
								value = 0
							peak = True
					else:
						# add keyframe
						peaks_curve.keyframe_points.insert(frame, value)
						
						# set keyframe interpolation
						interval = 60 / ppm_value * fps / 2
						right = interval / 2
						if len(peaks_curve.keyframe_points) > 1:
							left = (frame - peaks_curve.keyframe_points[-2].co[0]) / 2
						else:
							left = right
						set_peak_interpolation(
								peaks_curve.keyframe_points[-1], 
								clip,
								left, right )
						
						# next frame
						if amplitude_net == 0:
							frame += clip.CtF.accuracy
						else:
							frame += interval
						
						# invert value
						if value == 0:
							value = 1
						else:
							value = 0
						peak = True
				elif(peak):# ppm<=0 but peak == True
					# add keyframe
					if ppm_value == 0:
						if value == 0:
							peaks_curve.keyframe_points.insert(frame, 0)
						value = 0
					else: # (ppm<0)
						if value == 1:
							peaks_curve.keyframe_points.insert(frame, 1)
						value = 1
					
					peaks_curve.keyframe_points[-1].interpolation = 'CONSTANT'
					
					# next frame
					frame += clip.CtF.accuracy
					peak = False
				else:# ppm<=0 and not in a peak
					if ppm_value == 0 and value == 1:
						peaks_curve.keyframe_points.insert(frame, 0)
						peaks_curve.keyframe_points[-1].interpolation = 'CONSTANT'
						value = 0
					if ppm_value < 0 and value == 0:
						peaks_curve.keyframe_points.insert(frame, 1)
						peaks_curve.keyframe_points[-1].interpolation = 'CONSTANT'
						value = 1
					frame += clip.CtF.accuracy
				no_amplitude = (amplitude_net == 0)
			
			# add last keyframe
			peaks_curve.keyframe_points.insert(frame, value)
			# set keyframe interpolation
			if len(peaks_curve.keyframe_points) > 1:
				left = (frame - peaks_curve.keyframe_points[-2].co[0]) / 2
			else:
				left = interval / 2
			right = left
			set_peak_interpolation( 
					peaks_curve.keyframe_points[-1], 
					clip,
					left, right )
		
		# prevent curve edition
		peaks_curve.lock = True
		peaks_curve.hide = hide
		
		return peaks_curve
	
	
	
	def update_combination_curve(
						self,
						clip, 
						context, 
						amplitude_net_curve,
						peaks_curve):
		'''update clip combination curve'''
		# get combination mode curve
		combination_enum = clip.CtF.bl_rna.\
													properties['combination_mode'].enum_items
		combination_mode = combination_enum.find( clip.CtF.combination_mode )
		combination_mode_curve = getFCurveByDataPath(clip, 
								'CtF.combination_mode')
		
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
		
		# get ppm curve
		ppm_curve = getFCurveByDataPath(clip, 'CtF.ppm')
		
		if ppm_curve is None and clip.CtF.ppm <= 0:
			if clip.CtF.ppm < 0:# peak == 1 (constant)
				for keyframe in amplitude_net_curve.keyframe_points:
					combination_curve.keyframe_points.insert(
												keyframe.co[0],
												keyframe.co[1]
												)
			else:# peak == 0 (constant)
				for keyframe in amplitude_net_curve.keyframe_points:
					combination_curve.keyframe_points.insert(
												keyframe.co[0],
												0
												)
		else:
			# loop only on peak curve keyframe
			for keyframe in peaks_curve.keyframe_points:
				# get peaks keyframe value and frame
				frame = keyframe.co[0]
				value = keyframe.co[1]
				
				# get combination_mode at this frame
				if combination_mode_curve is not None:
					combination_mode = combination_mode_curve.evaluate(frame)
				
				# generate keyframe
				if combination_mode != 3 : # «combination mode == multiply or clamp
					value = value * amplitude_net_curve.evaluate(frame)
				
				if combination_mode != 4 :
					combination_curve.keyframe_points.insert(frame, value)
			
			
			# loop for all frame
			end = max(	peaks_curve.keyframe_points[-1].co[0], 
						context.scene.frame_end )
			frame = start = context.scene.frame_start
			while frame <= end:
				# get combination_mode at this frame
				if combination_mode_curve is not None:
					combination_mode = combination_mode_curve.evaluate(frame)
				
				if combination_mode == 0 : # combination mode is «multiply»
					value = peaks_curve.evaluate(frame)\
							* amplitude_net_curve.evaluate(frame)
					combination_curve.keyframe_points.insert(frame, value)
				elif combination_mode == 2: # combination mode is «clamp_curve»
					if( combination_curve.evaluate(frame) 
						> amplitude_net_curve.evaluate(frame) ):
						combination_curve.keyframe_points.insert(
								frame,
								amplitude_net_curve.evaluate(frame)
								)
				elif combination_mode == 4: 
					# combination mode is «ignore peaks»
					combination_curve.keyframe_points.insert(
								frame,
								amplitude_net_curve.evaluate(frame)
								)
				
				# next frame
				frame += 1
		
		
		# prevent curve edition
		combination_curve.lock = True
		combination_curve.hide = hide
		
		return combination_curve
	
	
	
	
	def update_output_curve(self, clip, context, combination_curve):
		'''update output curve'''
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
		start = context.scene.frame_start
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
	
	
	
	
	def panel_multi(self, context, layout):
		'''draw the CtF panel'''
		
		refresh_curve = "ctf.multi_track_curves_refresh"
		refresh_mini_maxi = "ctf.refresh_scene_mini_maxi"
		
		# draw amplitude settings
		self.draw_amplitude( layout, context.scene, 
							refresh_curve, refresh_mini_maxi )
		
		# draw peaks rythm settings
		self.draw_peaks(layout, refresh_curve )
		
		# draw peaks interpolation main settings
		self.draw_interpolation_main( layout )
		
		# draw peaks interpolation top settings
		self.draw_interpolation_top( layout )
		
		# draw combination node settings and combination and output value
		self.draw_combination_and_output( layout, refresh_curve, True )
		
		# draw output and rounding settings
		#warning = self.draw_output( layout, context.scene )
		
		# draw run button or error message
		#self.draw_run_button( layout, clip, warning )
	
	
	
	
	def get_valid_tracks():
		'''return a list of all movieclip that can be used as track'''
		tracks = []
		
		for t in bpy.data.movieclips:
			if t.type.source == 'SEQUENCE':
				tracks.append(t)
		
		return tracks
	
	
	
	
	def panel_tracks( self, layout, context ):
		'''draw the tracks panel content'''
		



def backup_output( path, level, maximum ):
	'''backup output directory'''
	# get backup path
	if level != 0:
		backup = path+'.backup'+str(level)
	else:
		backup = path
	
	# check older backup
	if os.path.exists( backup ):
		backup_output( path, level+1, maximum )
	else:
		return
	
	# erase too old backup
	if level >= maximum:
		shutil.rmtree(backup)
	else:
		# increment the backup
		shutil.move(
								backup,
								path+'.backup'+str(level+1)
								)
	




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
		
		# get output path
		dst = bpy.path.abspath( settings.output_path )
		if(dst[-1] != '/'):
			dst += '/'
		dst += clip.name+'.CtF_output'
		
		# check output path exist, is writable and empty
		if( os.path.exists( dst ) ):
			# check path access
			if(os.access(dst, os.W_OK)):
				# backup old output
				backup_n = context.user_preferences.filepaths.save_version
				backup_output( dst, 0, backup_n )
			else:
				# report error then quit 
				self.report(	{'ERROR'},
								'Output path : no write permission' )
				return {'CANCELLED'}
		dst += '/'
		# create new output directory
		try:
			os.mkdir(dst)
		except OSError as e:
			self.report({'ERROR'}, 
					'Unable to create the output path directory:'+e.strerror)
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
			# frame into the output path
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



class OneTrackPanel(bpy.types.Panel):
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
			clip.CtF.panel_simple(context, layout, clip)
			
		else:
			# Display a request for a movie clip
			row = layout.row()
			row.label( text="select/load an images sequence \
					in Movie Editor.", icon="ERROR" )
			row = layout.row()
			row.operator(
				"ctf.refresh",
				text="Refresh MovieClip info")
		





class MultiTracksPanel(bpy.types.Panel):
	'''class of the panel who contains addon multi track control'''
	bl_space_type = "CLIP_EDITOR"
	bl_region_type = "TOOLS"
	bl_label = "Multi Track Amplitude & Peaks Settings"
	bl_category = "Curve Anim"
	
	def draw(self, context):
		'''the function that draw the addon UI'''
		layout = self.layout
		context.scene.CtF.panel_multi( context, layout)
		





class TracksPanel(bpy.types.Panel):
	'''class of the panel who contains addon multi track control'''
	bl_space_type = "CLIP_EDITOR"
	bl_region_type = "TOOLS"
	bl_label = "Tracks"
	bl_category = "Curve Anim"
	
	def draw(self, context):
		'''the function that draw the addon UI'''
		context.scene.CtF.panel_tracks( self.layout, context )
		



def register():
	'''addon register'''
	bpy.utils.register_class(CtFRefresh)
	bpy.utils.register_class(Track)
	bpy.utils.register_class(CtFRefreshClipMiniMaxi)
	bpy.utils.register_class(CtFRefreshSceneMiniMaxi)
	bpy.utils.register_class(CtFSimpleTrackCurvesRefresh)
	bpy.utils.register_class(CtFMultiTrackCurvesRefresh)
	bpy.utils.register_class(CtF)
	bpy.types.MovieClip.CtF = bpy.props.PointerProperty(type=CtF)
	bpy.types.Scene.CtF = bpy.props.PointerProperty(type=CtF)
	bpy.utils.register_class(CurveToFrame)
	bpy.utils.register_class(OneTrackPanel)
	bpy.utils.register_class(MultiTracksPanel)
	bpy.utils.register_class(TracksPanel)
	print("Frames Animated By Curve is enabled")


def unregister():
	'''addon unregister'''
	bpy.utils.unregister_class(CtFRefresh)
	bpy.utils.unregister_class(Track)
	bpy.utils.unregister_class(CtFRefreshClipMiniMaxi)
	bpy.utils.unregister_class(CtFRefreshSceneMiniMaxi)
	bpy.utils.unregister_class(CtFSimpleTrackCurvesRefresh)
	bpy.utils.unregister_class(CtFMultiTrackCurvesRefresh)
	bpy.utils.unregister_class(CtF)
	bpy.utils.unregister_class(OneTrackPanel)
	bpy.utils.unregister_class(MultiTracksPanel)
	bpy.utils.unregister_class(CurveToFrame)
	bpy.utils.unregister_class(TracksPanel)
	print("Frames Animated By Curve is disabled")

