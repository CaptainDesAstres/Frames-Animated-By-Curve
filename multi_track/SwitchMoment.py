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
	
	switch_at_perfect_frame = bpy.props.BoolProperty(
		name = 'Frame perfect',
		description = 'Switch at the exact frame where you decide.',
		default = True,
		options = {'LIBRARY_EDITABLE'},
		update = update_switch_curve
		)
	
	
	
	
	generated_keyframe = bpy.props.BoolProperty(
		options = {'HIDDEN', 'ANIMATABLE'} )
	
	####################
	##   Methods      ##
	####################
	
	def update_switch_keyframe_curve( self ):
		'''update generated_keyframe curve'''
		scene = self.id_data
		# get and initialize generated_keyframe curve
		curve = get_fcurve_by_data_path( scene, 
								'curve_to_frame.generated_keyframe')
		if curve is not None:
			scene.animation_data.action.fcurves.remove(curve)
		scene.animation_data.action.fcurves.new(
									'curve_to_frame.generated_keyframe')
		curve = get_fcurve_by_data_path(scene, 
									'curve_to_frame.generated_keyframe')
		
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




