from .SwitchMoment import SwitchMoment
import bpy

class Switch(SwitchMoment):
	'''a class regrouping all settings and method
			about track switching'''
	
	def update_switch_curve( self, context ):
		'''update switching curve'''
		scene = self.id_data
		# ensure scene have animation data
		if scene.animation_data is None:
			scene.animation_data_create()
		if scene.animation_data.action is None:
			scene.animation_data.action = bpy.data.actions.new( 
						name= scene.name+'Action')
		
		# refresh and get keyframe curve
		generated_switch = self.get_generated_switch_curve_with_keyframes()
		
		# generate switch from settings
		if self.switch_mode == 'manual':
			self.generate_manual_switch(generated_switch)
	
	
	
	
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
	
	
	
	generated_switch = bpy.props.IntProperty(
		options = {'HIDDEN'} )
	
	
	####################
	##   Methods      ##
	####################
	def generate_manual_switch( self, generated ):
		'''generate final switch curve in manual mode.'''
		
		
	






