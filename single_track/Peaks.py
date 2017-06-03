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



