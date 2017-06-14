import bpy
from functions import *

class SwitchMoment:
	'''a class regrouping all settings and method
			about track switching'''
	
	def update_switch_curve( self, context ):
		'''update switching curve. must be rewrite in Switch class.'''
		return
	
	
	####################
	##   Properties   ##
	####################
	
	switch_at_perfect_frame = bpy.props.BoolProperty(
		name = 'Frame perfect',
		description = 'Switch at the exact frame where you decide.',
		default = True,
		update = update_switch_curve
		)
	
	
	
	
	generated_keyframe = bpy.props.BoolProperty(
		options = {'HIDDEN', 'ANIMATABLE'} )
	
	####################
	##   Methods      ##
	####################
	
	def update_switch_keyframe_curve( self ):
		'''update generated_keyframe curve'''
		ob = self.id_data
		# get and initialize generated_keyframe curve
		curve = get_fcurve_by_data_path( ob, 
								'curve_to_frame.generated_keyframe')
		if curve is not None:
			ob.animation_data.action.fcurves.remove(curve)
		ob.animation_data.action.fcurves.new(
									'curve_to_frame.generated_keyframe')
		curve = get_fcurve_by_data_path(ob, 
									'curve_to_frame.generated_keyframe')
		




