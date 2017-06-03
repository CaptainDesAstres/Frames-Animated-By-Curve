import bpy
from math import ceil, floor
from functions import *


class Amplitude():
	'''A class containing all properties and methods
		associates with amplitude feature of 
		Curve To Frame addon'''
	
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
		name = 'Maxi',
		description = 'the maximal value of the amplitude\
						 curve. All bigger value will display \
						the last frame. This property is useless \
						when amplitude is ignored.',
		default = 1.0,
		update = set_maxi
		)
	
	
	
	
	
	
	def update_net_amplitude_curve( self, clip, context ):
		'''update clip amplitude net curve'''
		# determine frame working space and frame step
		frame = start = floor(context.scene.frame_start - 5)
		end = ceil(context.scene.frame_end + 5)
		
		# get and erase amplitude_net fcurve
		amplitude_net_curve = get_fcurve_by_data_path(clip, 
										'curve_to_frame.amplitude_net')
		if amplitude_net_curve is not None:
			hide = amplitude_net_curve.hide
			clip.animation_data.action.fcurves.remove(amplitude_net_curve)
		else:
			hide = True
		clip.animation_data.action.fcurves.new('curve_to_frame.amplitude_net')
		amplitude_net_curve = get_fcurve_by_data_path(clip,
										'curve_to_frame.amplitude_net')
		
		# get amplitude fcurve
		raw_curve = get_fcurve_by_data_path(clip, 'curve_to_frame.amplitude')
		raw_value = clip.curve_to_frame.amplitude
		
		# get mini and maxi fcurve
		mini_curve = get_fcurve_by_data_path(clip, 'curve_to_frame.mini')
		mini_value = clip.curve_to_frame.mini
		maxi_curve = get_fcurve_by_data_path(clip, 'curve_to_frame.maxi')
		maxi_value = clip.curve_to_frame.maxi
		
		# generate amplitude_net curve
		while( frame <= end ):
			# get mini value at this frame
			if mini_curve is not None:
				mini_value = mini_curve.evaluate(frame)
			
			# get maxi value at thes frame
			if maxi_curve is not None:
				maxi_value = max ( maxi_curve.evaluate(frame), mini_value )
			
			# get amplitude raw value
			if raw_curve is not None:
				raw_value = raw_curve.evaluate(frame)
			
			#compute net value
			if raw_value >= maxi_value:
				net_amplitude_value = 1
			elif raw_value <= mini_value:
				net_amplitude_value = 0
			else:
				net_amplitude_value = ( raw_value - mini_value )\
										/( maxi_value - mini_value )
			
			# create keyframe
			amplitude_net_curve.keyframe_points.insert(frame,
								net_amplitude_value)
			
			frame += 1
		
		#erase keyframe on flat section
		avoid_useless_keyframe( amplitude_net_curve )
		
		# prevent curve edition
		amplitude_net_curve.lock = True
		amplitude_net_curve.hide = hide
		
		return amplitude_net_curve
	
