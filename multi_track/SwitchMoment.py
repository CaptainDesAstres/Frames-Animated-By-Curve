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
		
		# create keyframe at frame 0
		curve.keyframe_points.insert( 0, 0 )
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
		
		return curve




