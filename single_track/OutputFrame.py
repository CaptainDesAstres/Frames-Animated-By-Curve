from functions import *
import bpy
from math import ceil, floor


class OutputFrame():
	'''A class containing all properties and
		methods relative to output frames for 
		Curve To Frame addon'''
	
	#################################################
	##     output settings                         ##
	#################################################
	
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
	
	
	
	
	
	def update_output_curve(self, clip, context, combination_curve):
		'''update output curve'''
		# get and initialize output curve
		output_curve = get_fcurve_by_data_path(clip, 'curve_to_frame.output')
		if output_curve is not None:
			hide = output_curve.hide
			clip.animation_data.action.fcurves.remove(output_curve)
		else:
			hide = True
		clip.animation_data.action.fcurves.new('curve_to_frame.output')
		output_curve = get_fcurve_by_data_path(clip, 'curve_to_frame.output')
		
		# get start and end curve
		start_curve = get_fcurve_by_data_path(clip, 'curve_to_frame.start')
		end_curve = get_fcurve_by_data_path(clip, 'curve_to_frame.end')
		
		# generate first keyframe
		start = context.scene.frame_start
		output_curve.keyframe_points.insert( start - 1, 0 )
		output_curve.keyframe_points[-1].interpolation = 'LINEAR'
		
		# get rounding method
		if(clip.curve_to_frame.rounding == 'round'):
			rounding = round
		elif(clip.curve_to_frame.rounding == 'floor'):
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
				start_value = clip.curve_to_frame.start
			
			# check start_value
			if start_value < 1 :
				start_value = 1
			elif start_value > clip.curve_to_frame.size:
				start_value = clip.curve_to_frame.size
			
			# get end value at this frame
			if end_curve is not None:
				end_value = end_curve.evaluate(frame)
			else:
				end_value = clip.curve_to_frame.end
			
			# check end_value
			if end_value < start_value :
				end_value = start_value
			elif end_value > clip.curve_to_frame.size:
				end_value = clip.curve_to_frame.size
			
			# generate keyframe
			output_frame = rounding(
					clip.curve_to_frame.first + start_value - 1 
					+ combination_curve.evaluate(frame)
					* (end_value - start_value)
					)
			output_curve.keyframe_points.insert( frame, output_frame )
			
			# next frame
			frame += 1
		
		# generate last keyframe
		output_curve.keyframe_points.insert( frame , 0 )
		output_curve.keyframe_points[-1].interpolation = 'LINEAR'
		
		#erase keyframe on flat section
		avoid_useless_keyframe( output_curve )
		
		# prevent curve edition
		output_curve.lock = True
		output_curve.hide = hide





