import bpy
from functions import *


class Peaks():
	'''A class containing all properties and methods
		associates with peaks feature of 
		Curve To Frame addon'''
	
	def update_curves( self, context ):
		'''method that must be over ride: update curve when settings have been changed'''
	
	
	
	
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
	
	
	
	
	
	def check_and_get_peaks_shapes( self ):
		'''get all peaks shapes and check them'''
		# get shape curve
		shape_curve = get_fcurve_by_data_path( self.id_data, 
				'curve_to_frame.peaks_shape' )
		if shape_curve is None:
			self.init_peaks_shape_curve()
			shape_curve = get_fcurve_by_data_path( self.id_data, 'curve_to_frame.peaks_shape' )
		
		# get shape range start settings/curve
		start = self.peaks_shape_range_start
		start_curve = get_fcurve_by_data_path( self.id_data, 
				'curve_to_frame.peaks_shape_range_start' )
		
		# get shape range end settings/curve
		end = self.peaks_shape_range_end
		end_curve = get_fcurve_by_data_path( self.id_data, 
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
				curve_to_frame.generate_sync_peaks_curve( context, ob,
						peaks_curve, shapes, rate_curve, amplitude_net_curve,
						start, end
						)
			else:
				curve_to_frame.generate_peaks_curve_segment( context, ob,
						peaks_curve, shapes, rate_curve, start, end
						)
		
		# prevent curve edition
		peaks_curve.lock = True
		peaks_curve.hide = hide
		
		return peaks_curve



