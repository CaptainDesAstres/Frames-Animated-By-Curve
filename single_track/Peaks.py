import bpy
from functions import *


class Peaks():
	'''A class containing all properties and methods
		associates with peaks feature of 
		Curve To Frame addon'''
	
	def update_curves( self, context ):
		'''method that must be over ride: update curve when settings have been changed'''
		type(self).update_curves( self, context )
	
	
	
	
	#################################
	##       rate Properties       ##
	#################################
	
	# peaks per minute settings
	rate = bpy.props.FloatProperty(
				name = "rate",
				description = "peaks rate",
				default = 0)
	
	
	rate_unit = bpy.props.EnumProperty(
				name = 'Peaks rate unit',
				description = 'which unit is usedd to define Peaks Rate',
				default = 'frame',
				items = [
		#			(identifier,			name,
		#				description, number)
					
					('frame',		'Frames',
						'Peaks rate is define in terms of \
						peaks frame length.',				0),
					
					('ppm',		'Peaks Per Minute',
						'Peaks rate is define in terms of number \
						of peaks per minute.',		1),
					
					],
				options = {'LIBRARY_EDITABLE'},
				update = update_curves
				)
	
	
	# automatically use constant for rate curve interpolation
	auto_constant = bpy.props.BoolProperty(
				name="constant", 
				description="While animating rate value in «Peaks Per Minute» rate unit:\n it's highly recommanded to use constant interpolation for all keyframe.\n This option automatically do the convertion.",
				options = {'LIBRARY_EDITABLE'},
				default = True)
	
	
	
	#################################
	##   synchronize Properties    ##
	#################################
	# synchronize peak with amplitude bounce
	synchronized = bpy.props.BoolProperty(
				name="Sync to amplitude", 
				description="Peaks timing are synchronized with amplitude varying around 0.",
				options = {'LIBRARY_EDITABLE'},
				default = False)
	
	
	# anticipate amplitude rebounce when synchronized
	anticipate = bpy.props.FloatProperty(
				name = "anticipate",
				description = "With sync to amplitude, start peaks a little before amplitude rise over 0. \n0 mean the peaks will start exactly when amplitude start to be over 0.\n1 mean the peaks end exactly when amplitude start to be over 0.",
				default = 0,
				min = 0,
				max=1)
	
	
	# accuracy of peak synchronisation
	accuracy = bpy.props.FloatProperty(
				name = "accuracy",
				description = "gap between two evaluation when rate is less or equal to 0",
				options = {'LIBRARY_EDITABLE'},
				default = 0.1,
				min = 0.0001,
				max = 1)
	
	
	
	##############################
	##  peaks shape properties  ##
	##############################
	# a property to use as shape to make the peaks
	peaks_shape = bpy.props.FloatProperty(
				name = "Peaks shapes",
				description = "Use to edit the peaks shapes",
				min = 0,
				max = 1)
	
	
	# a property to change the part of peaks_shapes to use
	peaks_shape_range_start = bpy.props.IntProperty(
				name = "Start",
				description = "Use to set the peaks shape starting frame",
				min = 0)
	
	
	peaks_shape_range_end = bpy.props.IntProperty(
				name = "End",
				description = "Use to set the peaks shape ending frame",
				min = 1,
				default = 2)
	
	
	
	##############################
	##     output property      ##
	##############################
	# peaks curve obtain by applying settings
	peaks = bpy.props.FloatProperty(
				name = "peaks",
				description = "Only to visualize the peaks curve. \
							Can't be edit manually: use rate settings.",
				default = 1,
				min = 0,
				max = 1)
	
	peaks_start = bpy.props.BoolProperty(
				name = "peaks start",
				description = "Show when peaks start. \
							Must no be manually edited.",
				default = False)
	
	
	
	def init_peaks_shape_curve( self ):
		'''restore object default peaks shape curve'''
		ob = self.id_data
		
		# erase previous curve
		curve = get_fcurve_by_data_path( ob, 'curve_to_frame.peaks_shape' )
		if curve is not None:
			ob.animation_data.action.fcurves.remove(curve)
		
		# initialize peaks shape curve and settings
		if ob.animation_data is None:
			ob.animation_data_create()
		
		if ob.animation_data.action is None:
			ob.animation_data.action = bpy.data.actions.new( 
						name= ob.name+'Action')
		
		ob.animation_data.action.fcurves.new( 'curve_to_frame.peaks_shape' )
		curve = get_fcurve_by_data_path( ob, 'curve_to_frame.peaks_shape' )
		
		# set default profile
		curve.keyframe_points.insert( 0 , 0 )
		curve.keyframe_points[-1].interpolation = 'LINEAR'
		curve.keyframe_points.insert( 1 , 1 )
		curve.keyframe_points[-1].interpolation = 'LINEAR'
		curve.keyframe_points.insert( 2 , 0 )
		curve.keyframe_points[-1].interpolation = 'LINEAR'
		
		# erase range start/end curve
		curve = get_fcurve_by_data_path( ob, 'curve_to_frame.peaks_shape_range_start' )
		if curve is not None:
			ob.animation_data.action.fcurves.remove(curve)
		self.peaks_shape_range_start = 0
		
		curve = get_fcurve_by_data_path( ob, 'curve_to_frame.peaks_shape_range_end' )
		if curve is not None:
			ob.animation_data.action.fcurves.remove(curve)
		self.peaks_shape_range_end = 2
	
	
	
	
	
	def check_and_get_peaks_shapes( self ):
		'''get all peaks shapes and check them'''
		ob = self.id_data
		# get shape curve
		shape_curve = get_fcurve_by_data_path( ob, 
				'curve_to_frame.peaks_shape' )
		if shape_curve is None:
			self.init_peaks_shape_curve()
			shape_curve = get_fcurve_by_data_path( ob, 'curve_to_frame.peaks_shape' )
		
		# get shape range start settings/curve
		start = self.peaks_shape_range_start
		start_curve = get_fcurve_by_data_path( ob, 
				'curve_to_frame.peaks_shape_range_start' )
		
		# get shape range end settings/curve
		end = self.peaks_shape_range_end
		end_curve = get_fcurve_by_data_path( ob, 
				'curve_to_frame.peaks_shape_range_end' )
		
		# get all keyframe time for start curve
		keys = [0]
		if start_curve is not None:
			for k in start_curve.keyframe_points:
				k.interpolation = 'CONSTANT'
				keys.append(k.co[0])
		# get all keyframe time for end curve
		if end_curve is not None:
			for k in end_curve.keyframe_points:
				k.interpolation = 'CONSTANT'
				keys.append(k.co[0])
		
		# avoid useless double and sort
		keys.sort()
		for k in list(keys):
			if keys.count(k) > 1:
				keys.remove(k)
		
		shapes = {}
		for fr in keys:
			# get end and start value at this frame
			if start_curve is not None:
				start = start_curve.evaluate(fr)
			if end_curve is not None:
				end = end_curve.evaluate(fr)
			
			# avoid end greater than start situation
			if end <= start:
				return 'Error at frame '+str(fr)+': \nPeaks shape range is set to start at frame '+str(start)+' and end at frame '+str(end)+': \nend frame MUST BE GREATER than start frame!'
			
			# do needed operation if it's a new range
			r = (start, end)
			if r not in shapes.keys():
				# add to range list
				keyframes = []
				length = end - start
				
				# get keyframe between this range
				for k in shape_curve.keyframe_points:
					fr = k.co[0]
					if fr >= start and fr <= end:
						keyframes.append(k)
				
				# check there is a keyframe corresponding to start/end frame
				if keyframes[0].co[0] != start:
					return 'Error at frame '+str(fr)+': \nPeaks Shape range is set to start at frame '+str(start)+' \nbut peaks shape curve have no keyframe at this position.'
				start = keyframes[0]
				
				if keyframes[-1].co[0] != end:
					return 'Error at frame '+str(fr)+': \nPeaks Shape range is set to end at frame '+str(end)+' \nbut peaks shape curve have no keyframe at this position.'
				end = keyframes[-1]
				
				# check if first and last keyframe have the same value
				if end.co[1] != start.co[1]:
					return 'Error at frame '+str(int(fr))+':\nPeaks Shape range is set to start at frame '+str(int(start.co[0]))+' and end at frame '+str(int(end.co[0]))+' \nbut corresponding peaks shape curve keyframe at those positions didn\'t have the same value \n(respectivly '+str(start.co[1])+' and '+str(end.co[1])+').'
				
				# copy keyframe and normalize settings
				KFInfoList = []
				prev = start.co[0]
				for k in keyframes:
					KF = {}
					# get frame
					KF['frame'] = (k.co[0]-prev) / length
					prev = k.co[0]
					
					# get value
					KF['value'] = k.co[1]
					
					# get interpolation
					KF['interpolation'] = k.interpolation
					
					# get easing
					KF['easing'] = k.easing
					
					# get left X and Y
					y = k.handle_left[1] - k.co[1]
					x = ( k.handle_left[0] - k.co[0] ) / length
					KF['left'] = ( x, y )
					
					# get right X and Y
					y = k.handle_right[1] - k.co[1]
					x = ( k.handle_right[0] - k.co[0] ) / length
					KF['right'] = ( x, y )
					
					KFInfoList.append(KF)
				
				# copy first keyframe into last keyframe
				last = KFInfoList[0].copy()
				last['frame'] = KFInfoList[-1]['frame']
				last['left'] = KFInfoList[-1]['left']
				KFInfoList[-1] = last
				
				shapes[r] = KFInfoList
		
		return shapes
	
	
	
	
	
	def update_peaks_curve(self, 
					context, 
					amplitude_net_curve, 
					shapes ):
		'''Update peaks curve with current settings'''
		ob = self.id_data
		# remove old peaks
		peaks_curve = get_fcurve_by_data_path(ob, 'curve_to_frame.peaks')
		if peaks_curve is not None:
			hide = peaks_curve.hide
			ob.animation_data.action.fcurves.remove(peaks_curve)
		else:
			hide = True
		
		# create new peaks
		ob.animation_data.action.fcurves.new('curve_to_frame.peaks')
		peaks_curve = get_fcurve_by_data_path(ob, 'curve_to_frame.peaks')
		
		
		# remove old peaks start keyframe
		peaks_start_curve = get_fcurve_by_data_path(ob,
						'curve_to_frame.peaks_start')
		if peaks_start_curve is not None:
			ob.animation_data.action.fcurves.remove(peaks_start_curve)
		
		# create new peaks start keyframe
		ob.animation_data.action.fcurves.new('curve_to_frame.peaks_start')
		peaks_start_curve = get_fcurve_by_data_path(ob,
						'curve_to_frame.peaks_start')
		
		
		# get rate curve and default value
		rate_curve = get_fcurve_by_data_path(ob, 'curve_to_frame.rate')
		rate_value = ob.curve_to_frame.rate
		
		# convert rate_curve to constant interpolation
		if ob.curve_to_frame.auto_constant and rate_curve is not None:
			for k in rate_curve.keyframe_points:
				k.interpolation = 'CONSTANT'
		
		# get scene start/end frame
		start = context.scene.frame_start
		end = context.scene.frame_end
		
		
		if rate_curve is None and rate_value <= 0:
			if rate_value == 0:
				# 0 valued flat peaks curve
				peaks_curve.keyframe_points.insert(0, 0)
			else:
				# 1 valued flat peaks curve
				peaks_curve.keyframe_points.insert(0, 1)
		else:
			# rate_curve is animated
			if ob.curve_to_frame.synchronized:
				ob.curve_to_frame.generate_synchronized_peaks( context,
						peaks_curve, peaks_start_curve, shapes, rate_curve, amplitude_net_curve,
						start, end
						)
			else:
				ob.curve_to_frame.generate_peaks_curve_segment( context,
						peaks_curve, peaks_start_curve, shapes, rate_curve, start, end
						)
		
		# prevent curve edition
		peaks_curve.lock = True
		peaks_curve.hide = hide
		peaks_start_curve.lock = True
		peaks_start_curve.hide = True
		
		return peaks_curve
	
	
	
	
	
	def generate_synchronized_peaks(
				self,
				context,
				peaks_curve,
				peaks_start_curve,
				shapes,
				rate_curve,
				amplitude_net_curve,
				start,
				end
				):
		'''generate the peaks curve when synchronized with amplitude'''
		ob = self.id_data
		# get first segment starting frame
		seg_start = start
		amplitude = amplitude_net_curve.evaluate(seg_start)
		if amplitude == 0:
			anticipate = True
		else:
			anticipate = False
		
		
		while( seg_start < end ):
			amplitude = amplitude_net_curve.evaluate(seg_start)
			if amplitude == 0:
				k = peaks_curve.keyframe_points.insert( seg_start, 0 )
				k.interpolation = 'CONSTANT'
				while amplitude == 0 and seg_start <= end:
					seg_start += ob.curve_to_frame.accuracy
					amplitude = amplitude_net_curve.evaluate(seg_start)
			
			seg_end = seg_start
			while amplitude != 0 and seg_end <= end:
				seg_end += ob.curve_to_frame.accuracy
				amplitude = amplitude_net_curve.evaluate(seg_end)
			
			seg_start = ob.curve_to_frame.generate_peaks_curve_segment( 
							context, peaks_curve, peaks_start_curve, shapes, rate_curve,
							seg_start, seg_end, anticipate )
			anticipate = True
	
	
	
	
	
	def generate_anticipated_peaks(
				self,
				shape,
				start,
				rate,
				peaks_curve,
				peaks_start_curve
				):
		'''generate anticipated peaks keyframe'''
		ob = self.id_data
		# get anticipate settings
		anticipate_curve = get_fcurve_by_data_path( ob, 
				'curve_to_frame.anticipate' )
		if anticipate_curve is None:
			anticipate = ob.curve_to_frame.anticipate
		else:
			anticipate = anticipate_curve.evaluate(start)
		
		# init frame and shape key
		shape_key = 0
		frame = start
		frame -= anticipate * rate
		
		# don't start peaks before last peaks_curve keyframe
		frame = max(frame, peaks_curve.keyframe_points[-1].co[0] + 0.01 )
		
		KF = shape[shape_key]
		l = len(shape)-1
		peaks_start_curve.keyframe_points.insert( frame, -1 )
		while(shape_key < l):
			# insert anticipated keyframe
			keyframe = peaks_curve.keyframe_points.insert( frame, KF['value'])
			
			# set handle and interpolation settings
			keyframe.handle_left_type = 'FREE'
			keyframe.handle_left[0] = keyframe.co[0] \
																+ KF['left'][0] * rate
			keyframe.handle_left[1] = keyframe.co[1] \
																+ KF['left'][1]
			
			keyframe.handle_right_type = 'FREE'
			keyframe.handle_right[0] = keyframe.co[0] \
																+ KF['right'][0] * rate
			keyframe.handle_right[1] = keyframe.co[1] \
																+ KF['right'][1]
			
			keyframe.interpolation = KF['interpolation']
			keyframe.easing = KF['easing']
			
			# next keyframe
			shape_key += 1
			KF = shape[shape_key]
			frame += KF['frame'] * rate
		
		return frame, shape_key
	
	
	
	
	
	def generate_peaks_curve_segment(
						self,
						context,
						peaks_curve,
						peaks_start_curve,
						shapes,
						rate_curve,
						start,
						end,
						anticipate = False
						):
		'''generate a segment of peaks curve'''
		ob = self.id_data
		# get frame rate and start/end frame
		fps = context.scene.render.fps
		
		# get peaks shape range start/end curve
		shape_start_curve =  get_fcurve_by_data_path( ob, 
				'curve_to_frame.peaks_shape_range_start' )
		shape_end_curve = get_fcurve_by_data_path( ob, 
				'curve_to_frame.peaks_shape_range_end' )
		
		# get default rate
		rate = ob.curve_to_frame.rate
		if rate_curve is not None:
			rate = rate_curve.evaluate( start )
		
		# get real starting frame
		frame = start
		if rate <= 0:
			anticipate = False
			frame, current_shape, shape_KF, rate =\
						ob.curve_to_frame.generate_no_peaks_segment( rate_curve,
								peaks_curve, shape_start_curve, shape_end_curve,
								shapes, frame, end )
			if frame >= end:
				return frame
		
		# convert rate if in ppm
		if ob.curve_to_frame.rate_unit == 'ppm':
			rate = fps * 60 / rate
		
		# get peaks shape start range
		if shape_start_curve is None:
			shape_start = ob.curve_to_frame.peaks_shape_range_start
		else:
			shape_start = shape_start_curve.evaluate( start )
		
		# get peaks shape end range
		if shape_end_curve is None:
			shape_end = ob.curve_to_frame.peaks_shape_range_end
		else:
			shape_end = shape_end_curve.evaluate( start )
		
		# initial range and key frame
		current_shape = ( shape_start, shape_end )
		shape_key = 0
		
		# generate anticipated keyframe
		if anticipate:
			frame, shape_key = ob.curve_to_frame.generate_anticipated_peaks(
							shapes[current_shape],
							frame, rate, peaks_curve, peaks_start_curve
							)
		
		# get shape keyframe
		shape_KF = shapes[current_shape][shape_key]
		
		# generate the segment
		peaks_start_curve.keyframe_points.insert( frame, -1 )
		while( True ):
			# insert keyframe
			keyframe = peaks_curve.keyframe_points.insert( frame,
					shape_KF['value'] )
			
			# set left handle of keyframe
			keyframe.handle_left_type = 'FREE'
			keyframe.handle_left[0] = keyframe.co[0] \
																+ shape_KF['left'][0] * rate
			keyframe.handle_left[1] = keyframe.co[1] \
																+ shape_KF['left'][1]
			
			if frame >= end :
				return frame + 0.01
			
			# get rate value
			if rate_curve is not None:
				rate = rate_curve.evaluate( frame )
				if rate > 0 and ob.curve_to_frame.rate_unit == 'ppm':
					rate = fps * 60 / rate
			
			# peaks end instructions
			shape_key += 1
			if shape_key == len(shapes[current_shape]):
				peaks_start_curve.keyframe_points.insert( frame, -1 )
				shape_key = 1
				# get new range
				if shape_start_curve is not None:
					shape_start = shape_start_curve.evaluate( frame )
				if shape_end_curve is not None:
					shape_end = shape_end_curve.evaluate( frame )
				current_shape = ( shape_start, shape_end )
				shape_KF = shapes[current_shape][0]
				
				# add a keyframe if new peaks keyframe value different 
				#    from the last of the previous peaks
				if( shape_KF['value'] != keyframe.co[1] ):
					frame += 0.01
					keyframe.interpolation = 'LINEAR'
					
					keyframe = peaks_curve.keyframe_points.insert(
							frame, shape_KF['value'] )
			
			# set right handle of keyframe
			keyframe.handle_right_type = 'FREE'
			keyframe.handle_right[0] = keyframe.co[0] \
																+ shape_KF['right'][0] * rate
			keyframe.handle_right[1] = keyframe.co[1] \
																+ shape_KF['right'][1]
			
			# set right interpolation and easing
			keyframe.interpolation = shape_KF['interpolation']
			keyframe.easing = shape_KF['easing']
			
			if rate <= 0:
				frame, current_shape, shape_KF, rate =\
							ob.curve_to_frame.generate_no_peaks_segment( rate_curve,
									peaks_curve, shape_start_curve, shape_end_curve,
									shapes, frame, end )
				if frame >= end:
					return frame
			else:
				# get next shape keyframe
				shape_KF = shapes[current_shape][shape_key]
				frame += shape_KF['frame'] * rate
		return frame
	
	
	
	
	
	def generate_no_peaks_segment( 
					self,
					rate_curve,
					peaks_curve,
					shape_start_curve,
					shape_end_curve,
					shapes,
					frame,
					end ):
		'''generate flat peaks curve segment when rate <= 0'''
		ob = self.id_data
		
		shape_start = self.peaks_shape_range_start
		shape_end = self.peaks_shape_range_end
		
		rate = rate_curve.evaluate( frame )
		while rate <= 0:
			frame += ob.curve_to_frame.accuracy
			
			if rate == 0:
				keyframe = peaks_curve.keyframe_points.insert( frame, 0 )
				test = True
			else:
				keyframe = peaks_curve.keyframe_points.insert( frame, 1 )
				test = False
			
			keyframe.interpolation = 'CONSTANT'
			
			rate = rate_curve.evaluate( frame )
			while( rate <= 0 and ((rate == 0) == test) and frame <= end ):
				frame += ob.curve_to_frame.accuracy
				rate = rate_curve.evaluate( frame )
			
			if rate > 0 and ob.curve_to_frame.rate_unit == 'ppm':
				rate = fps * 60 / rate
			
			# start a new peaks
			shape_key = 0
			
			# get new range
			if shape_start_curve is not None:
				shape_start = shape_start_curve.evaluate( frame )
			if shape_end_curve is not None:
				shape_end = shape_end_curve.evaluate( frame )
			current_shape = ( shape_start, shape_end )
			
			shape_KF = shapes[current_shape][shape_key]
			
			return frame, current_shape, shape_KF, rate



