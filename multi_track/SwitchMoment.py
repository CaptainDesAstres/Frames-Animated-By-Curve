import bpy

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




