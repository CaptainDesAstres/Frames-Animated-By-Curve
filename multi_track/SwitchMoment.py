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
	switch_at_peaks_values = bpy.props.BoolProperty(
		name = 'At X peaks values',
		description = 'Track is switch each time peaks curve pass through designated values.',
		default = False,
		options = {'LIBRARY_EDITABLE'},
		update = update_switch_curve
		)
	
	peaks_values = bpy.props.StringProperty(
		name = 'peaks values',
		description = 'The values to use to trigger a switch. Use only numerical value separated by «;» .',
		default = '0',
		update = update_switch_curve
		)
	
	
	
	# switch each teime amplitude pass through X value
	switch_at_amplitude_values = bpy.props.BoolProperty(
		name = 'At X amplitude (net) values',
		description = 'Track is switch each time amplitude (net) curve pass through designated values.',
		default = False,
		options = {'LIBRARY_EDITABLE'},
		update = update_switch_curve
		)
	
	amplitude_values = bpy.props.StringProperty(
		name = 'amplitude values',
		description = 'The values of amplitude who trigger a switch. Use only numerical value separated by «;» .',
		default = '0',
		update = update_switch_curve
		)
	
	
	
	# switch each teime combination curve pass through X value
	switch_at_combination_values = bpy.props.BoolProperty(
		name = 'At X combination values',
		description = 'Track is switch each time combination curve pass through designated values.',
		default = False,
		options = {'LIBRARY_EDITABLE'},
		update = update_switch_curve
		)
	
	combination_values = bpy.props.StringProperty(
		name = 'combination values',
		description = 'The values of combination who trigger a switch. Use only numerical value separated by «;» .',
		default = '0',
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
		
		# create keyframe at animation first frame
		curve.keyframe_points.insert( scene.frame_start, 0 )
		curve.keyframe_points[-1].interpolation = 'CONSTANT'
		
		# create a keyframe at each manual switching keyframe
		if self.switch_mode == 'manual' and self.switch_at_perfect_frame:
			manual_switch = get_fcurve_by_data_path(scene, 
									'curve_to_frame.manual_switch')
			if manual_switch is not None:
				for KF in manual_switch.keyframe_points:
					curve.keyframe_points.insert( 
						KF.co[0],
						0
						)
					
					curve.keyframe_points[-1].interpolation = 'CONSTANT'
		
		# create a key frame at each custom moments
		if self.switch_mode != 'manual' and self.switch_at_custom_keyframe:
			custom = get_fcurve_by_data_path( scene, 
									'curve_to_frame.custom_keyframe')
			if custom is not None:
				for KF in custom.keyframe_points:
					curve.keyframe_points.insert( 
						KF.co[0],
						0
						)
					
					curve.keyframe_points[-1].interpolation = 'CONSTANT'
		
		# create a keyframe at each peaks start
		if self.switch_at_peaks_keyframes:
			peaks = get_fcurve_by_data_path( scene, 
									'curve_to_frame.peaks')
			
			if peaks is not None:
				for KF in peaks.keyframe_points:
					curve.keyframe_points.insert( 
						KF.co[0],
						0
						)
					
					curve.keyframe_points[-1].interpolation = 'CONSTANT'
			
		elif self.switch_at_peaks:
			peaks_start = get_fcurve_by_data_path( scene, 
									'curve_to_frame.peaks_start')
			
			if peaks_start is not None:
				for KF in peaks_start.keyframe_points:
					curve.keyframe_points.insert( 
						KF.co[0],
						0
						)
					
					curve.keyframe_points[-1].interpolation = 'CONSTANT'
		
		return curve




