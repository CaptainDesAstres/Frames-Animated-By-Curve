import bpy
from functions import *

class Combination():
	'''A class containing all properties and methods
		relative to combination settings for 
		Curve To Frame addon'''
	
	def update_curves( self, context ):
		'''method that must be over ride: update curve when settings have been changed'''
	
	
	
	######################################
	##     combination settings         ##
	######################################
	
	# method used to combine amplitude and peaks curve
	combination_mode = bpy.props.EnumProperty(
		name = 'combination mode',
		description = 'the way to combine amplitude and peaks curve',
		default = 'ignore_peaks',
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
	
	
	
	# combination of net amplitude and peaks curves
	combination = bpy.props.FloatProperty(
		name = "combination",
		description = "Only to visualize the combination of \
					peaks and amplitude curve curve. Can't \
					be edit manually: use rate and amplitude settings.",
		default = 0,
		min = 0,
		max = 1)
	
	
	
	
	
	def update_combination_curve(
						self,
						clip, 
						context, 
						amplitude_net_curve,
						peaks_curve):
		'''update clip combination curve'''
		# get combination mode curve
		combination_enum = clip.curve_to_frame.bl_rna.\
													properties['combination_mode'].enum_items
		combination_mode = combination_enum.find( clip.curve_to_frame.combination_mode )
		combination_mode_curve = get_fcurve_by_data_path(clip, 
								'curve_to_frame.combination_mode')
		
		# get and initialize combination curve
		combination_curve = get_fcurve_by_data_path(clip, 
								'curve_to_frame.combination')
		if combination_curve is not None:
			hide = combination_curve.hide
			clip.animation_data.action.fcurves.remove(combination_curve)
		else:
			hide = True
		clip.animation_data.action.fcurves.new(
									'curve_to_frame.combination')
		combination_curve = get_fcurve_by_data_path(clip, 
									'curve_to_frame.combination')
		
		# get rate curve
		rate_curve = get_fcurve_by_data_path(clip, 'curve_to_frame.rate')
		
		# loop only on peak curve keyframe
		for keyframe in peaks_curve.keyframe_points:
			# get peaks keyframe value and frame
			frame = keyframe.co[0]
			value = max( min(1, keyframe.co[1]), 0 )
			
			# get combination_mode at this frame
			if combination_mode_curve is not None:
				combination_mode = combination_mode_curve.evaluate(frame)
			
			# generate keyframe
			if combination_mode != 3 : # «combination mode == multiply or clamp
				value = value * amplitude_net_curve.evaluate(frame)
			
			if combination_mode != 4 :
				combination_curve.keyframe_points.insert(frame, value)
				combination_curve.keyframe_points[-1].interpolation = 'LINEAR'
		
		
		# loop for all frame
		end = max(	peaks_curve.keyframe_points[-1].co[0], 
					context.scene.frame_end )
		frame = start = context.scene.frame_start
		while frame <= end:
			# get combination_mode at this frame
			if combination_mode_curve is not None:
				combination_mode = combination_mode_curve.evaluate(frame)
			
			if combination_mode == 0 : # combination mode is «multiply»
				value = max( min( 1, peaks_curve.evaluate(frame) ), 0 )\
						* amplitude_net_curve.evaluate(frame)
				combination_curve.keyframe_points.insert(frame, value)
			elif combination_mode == 2: # combination mode is «clamp_curve»
				combination_curve.keyframe_points.insert(
						frame,
						max(
							min (
									amplitude_net_curve.evaluate(frame),
									peaks_curve.evaluate(frame),
									1
									),
							0
						)
					)
			elif combination_mode == 4: 
				# combination mode is «ignore peaks»
				combination_curve.keyframe_points.insert(
							frame,
							amplitude_net_curve.evaluate(frame)
							)
			
			combination_curve.keyframe_points[-1].interpolation = 'LINEAR'
			
			# next frame
			frame += 1
		
		#erase keyframe on flat section
		avoid_useless_keyframe( combination_curve )
		
		# prevent curve edition
		combination_curve.lock = True
		combination_curve.hide = hide
		
		return combination_curve
	
	
	
	
	
	
