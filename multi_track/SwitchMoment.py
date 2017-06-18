import bpy
from functions import *

class SwitchMoment:
	'''a class regrouping all settings and method
			about track switching'''
	
	def update_switch_curve( self, context ):
		'''update switching curve. must be rewrite in Switch class.'''
		type(self).update_switch_curve( self, context )
	
	
	####################
	##   Properties   ##
	####################
	# switch exactly when track is manually change
	switch_at_perfect_frame = bpy.props.BoolProperty(
		name = 'At perfect frame',
		description = 'Switch at the exact frame where you decide.',
		default = True,
		options = {'LIBRARY_EDITABLE'},
		update = update_switch_curve
		)
	
	
	
	# switch at custom moment
	switch_at_custom_keyframe = bpy.props.BoolProperty(
		name = 'At custom moment',
		description = 'Manually define the moments to switch.',
		default = False,
		options = {'LIBRARY_EDITABLE'},
		update = update_switch_curve
		)
	# settings to define the custom keyframe position
	custom_keyframe = bpy.props.IntProperty(
		name = 'Custom moment',
		description = 'Add keyframe to define the moments to switch',
		min = 0,
		max = 0,
		update = update_switch_curve
		)
	
	
	
	# switch at each peaks
	switch_at_peaks = bpy.props.BoolProperty(
		name = 'At each peaks',
		description = 'Track is switch after each peak.',
		default = False,
		options = {'LIBRARY_EDITABLE'},
		update = update_switch_curve
		)
	
	
	
	# switch at each peaks
	switch_at_peaks_keyframes = bpy.props.BoolProperty(
		name = 'At each peaks keyframe',
		description = 'Track is switch after each keyframe in peaks curve.',
		default = False,
		options = {'LIBRARY_EDITABLE'},
		update = update_switch_curve
		)
	
	
	
	# switch each teime peaks pass through X value
	switch_when_peaks_get_over = bpy.props.BoolProperty(
		name = 'Peaks get over:',
		description = 'switch track when peaks curve get over designated values.',
		default = False,
		options = {'LIBRARY_EDITABLE'},
		update = update_switch_curve
		)
	
	peaks_over_trigger_values = bpy.props.StringProperty(
		name = '',
		description = 'The values to use for «When peaks get over:» option. Use only numerical value separated by «;» .',
		default = '0.5',
		update = update_switch_curve
		)
	
	switch_when_peaks_get_under = bpy.props.BoolProperty(
		name = 'Peaks get under:',
		description = 'switch track when peaks curve get under designated values.',
		default = False,
		options = {'LIBRARY_EDITABLE'},
		update = update_switch_curve
		)
	
	peaks_under_trigger_values = bpy.props.StringProperty(
		name = '',
		description = 'The values to use for «When peaks get under:» option. Use only numerical value separated by «;» .',
		default = '0.5',
		update = update_switch_curve
		)
	
	
	
	# switch each teime amplitude pass through X value
	switch_when_amplitude_get_over = bpy.props.BoolProperty(
		name = 'Amplitude (net) get over:',
		description = 'Switch track when amplitude (net) curve get over designated values.',
		default = False,
		options = {'LIBRARY_EDITABLE'},
		update = update_switch_curve
		)
	
	amplitude_over_trigger_values = bpy.props.StringProperty(
		name = '',
		description = 'The values to use for «When amplitude (net) get over:» option. Use only numerical value separated by «;» .',
		default = '0.5',
		update = update_switch_curve
		)
	
	switch_when_amplitude_get_under = bpy.props.BoolProperty(
		name = 'Amplitude (net) get under:',
		description = 'switch track when amplitude (net) curve get under designated values.',
		default = False,
		options = {'LIBRARY_EDITABLE'},
		update = update_switch_curve
		)
	
	amplitude_under_trigger_values = bpy.props.StringProperty(
		name = '',
		description = 'The values to use for «When amplitude (net) get under:» option. Use only numerical value separated by «;» .',
		default = '0.5',
		update = update_switch_curve
		)
	
	
	
	# switch each teime combination pass through X value
	switch_when_combination_get_over = bpy.props.BoolProperty(
		name = 'Combination get over:',
		description = 'switch track when combination curve get over designated values.',
		default = False,
		options = {'LIBRARY_EDITABLE'},
		update = update_switch_curve
		)
	
	combination_over_trigger_values = bpy.props.StringProperty(
		name = '',
		description = 'The values to use for «When combination get over:» option. Use only numerical value separated by «;» .',
		default = '0.5',
		update = update_switch_curve
		)
	
	switch_when_combination_get_under = bpy.props.BoolProperty(
		name = 'Combination get under:',
		description = 'switch track when combination curve get under designated values.',
		default = False,
		options = {'LIBRARY_EDITABLE'},
		update = update_switch_curve
		)
	
	combination_under_trigger_values = bpy.props.StringProperty(
		name = '',
		description = 'The values to use for «When combination get under:» option. Use only numerical value separated by «;» .',
		default = '0.5',
		update = update_switch_curve
		)
	
	
	
	
	# value evaluation gap
	values_evaluation_accuracy = bpy.props.FloatProperty(
		name = 'Evaluation accuracy',
		description = 'Gap between two evaluation of peaks/amplitude/combination values.',
		default = 0.1,
		min = 0.001,
		update = update_switch_curve
		)
	
	# Introduce a minimal gap between two switching moment
	minimal_switch_gap_option = bpy.props.BoolProperty(
		name = 'Switching minimal gap:',
		description = 'Do not switch more than once by this gap time.',
		default = True,
		options = {'LIBRARY_EDITABLE'},
		update = update_switch_curve
		)
	
	minimal_switch_gap = bpy.props.FloatProperty(
		name = '',
		description = 'Minimal Gap between two track switch.',
		default = 1,
		min = 0,
		update = update_switch_curve
		)
	
	
	####################
	##   Methods      ##
	####################
	
	def get_generated_switch_curve_with_keyframes( self ):
		'''generate keyframe of generated_switch curve and return the curve'''
		scene = self.id_data
		
		# get and initialize generated_switch curve
		curve = get_fcurve_by_data_path( scene, 
								'curve_to_frame.generated_switch')
		if curve is not None:
			hide = curve.hide
			scene.animation_data.action.fcurves.remove(curve)
		else:
			hide = True
		scene.animation_data.action.fcurves.new(
									'curve_to_frame.generated_switch')
		curve = get_fcurve_by_data_path(scene, 
									'curve_to_frame.generated_switch')
		curve.hide = hide
		curve.lock = True
		
		# create switch moment at animation first frame
		curve.keyframe_points.insert( scene.frame_start, 0 )
		
		# create a switch moment at each manual switching keyframe
		if self.switch_mode == 'manual' and self.switch_at_perfect_frame:
			manual_switch = get_fcurve_by_data_path(scene, 
									'curve_to_frame.manual_switch')
			if manual_switch is not None:
				for KF in manual_switch.keyframe_points:
					curve.keyframe_points.insert( 
						KF.co[0],
						0
						)
		
		# create a switch moment at each custom moments
		if self.switch_mode != 'manual' and self.switch_at_custom_keyframe:
			custom = get_fcurve_by_data_path( scene, 
									'curve_to_frame.custom_keyframe')
			if custom is not None:
				for KF in custom.keyframe_points:
					curve.keyframe_points.insert( 
						KF.co[0],
						0
						)
		
		if self.switch_at_peaks_keyframes:
			# create a switch moment at each peaks start
			peaks = get_fcurve_by_data_path( scene, 
									'curve_to_frame.peaks')
			
			if peaks is not None:
				for KF in peaks.keyframe_points:
					curve.keyframe_points.insert( 
						KF.co[0],
						0
						)
			
		elif self.switch_at_peaks:
			# create a switch moment at each peaks keyframe
			peaks_start = get_fcurve_by_data_path( scene, 
									'curve_to_frame.peaks_start')
			
			if peaks_start is not None:
				for KF in peaks_start.keyframe_points:
					curve.keyframe_points.insert( 
						KF.co[0],
						0
						)
		
		accuracy = self.values_evaluation_accuracy
		
		# switch when peaks curve get over values
		if self.switch_when_peaks_get_over:
			# get peaks curve
			peaks = get_fcurve_by_data_path( scene, 
									'curve_to_frame.peaks')
			
			if peaks is not None:
				# do the loop test for each peaks trigger values
				for v in self.peaks_over_trigger_values.split(';'):
					try:
						value = float(v)
						
						frame = scene.frame_start
						previous = 0
						# add a switch moment when peaks curve get over trigger value
						while frame < scene.frame_end:
							current = peaks.evaluate(frame)
							if previous < value and current >= value:
								curve.keyframe_points.insert( 
										frame,
										0
										)
							previous = current
							frame += accuracy
						
					except ValueError:
						pass
		
		
		
		# avoid too closed switch moment
		if self.minimal_switch_gap_option:
			i = 1
			prev = curve.keyframe_points[0]
			minimal_gap = self.minimal_switch_gap
			
			while i < len(curve.keyframe_points):
				KF = curve.keyframe_points[i]
				if KF.co[0]-prev.co[0] < minimal_gap:
					curve.keyframe_points.remove(KF)
				else:
					prev = KF
					i += 1
		
		# convert switch moment keyframe in constant interpolation
		for KF in curve.keyframe_points:
			KF.interpolation = 'CONSTANT'
		
		return curve




