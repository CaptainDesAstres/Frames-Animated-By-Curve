from .SwitchMoment import SwitchMoment
import bpy

class Switch(SwitchMoment):
	'''a class regrouping all settings and method
			about track switching'''
	
	def update_switch_curve( self, context ):
		'''update switching curve'''
		ob = self.id_data
		# ensure scene have animation data
		if ob.animation_data is None:
			ob.animation_data_create()
		if ob.animation_data.action is None:
			ob.animation_data.action = bpy.data.actions.new( 
						name= ob.name+'Action')
		
		self.update_switch_keyframe_curve()
		
	
	
	
	
	####################
	##   Properties   ##
	####################
	
	switch_mode = bpy.props.EnumProperty(
		name = 'Switch mode',
		description = 'Define how to switch between tracks.',
		default = 'manual',
		items = [
#			(identifier,			name,
#				description, number)
			
			('manual',		'Manually',
				'You set tracks manually',				0)
			
			],
		options = {'LIBRARY_EDITABLE'},
		update = update_switch_curve
		)
	
	
	manual_switch = bpy.props.IntProperty(
		name = 'Track',
		description = 'Track to use.',
		default = 0,
		update = update_switch_curve
		)
	
