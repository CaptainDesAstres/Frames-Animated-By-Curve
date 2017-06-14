from .SwitchMoment import SwitchMoment
import bpy
from functions import *

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
		elif self.switch_mode == 'ramdom':
			self.generate_random_switch(generated_switch)
		
		
		# erase useless keyframe
		avoid_useless_keyframe( generated_switch )
	
	
	
	
	####################
	##   Properties   ##
	####################
	# track switching mode property
	switch_mode = bpy.props.EnumProperty(
		name = 'Switch mode',
		description = 'Define how to switch between tracks.',
		default = 'manual',
		items = [
#			(identifier,			name,
#				description, number)
			
			('manual',		'Manually',
				'You set tracks manually',				0),
			
			('random',		'Ramdomly',
				'Track are randomly choosen',				1)
			
			],
		options = {'LIBRARY_EDITABLE'},
		update = update_switch_curve
		)
	
	# manual switch settings
	manual_switch = bpy.props.IntProperty(
		name = 'Track',
		description = 'Track to use.',
		default = 0,
		update = update_switch_curve
		)
	
	
	# final switching curve
	generated_switch = bpy.props.IntProperty(
		options = {'HIDDEN'} )
	
	
	####################
	##   Methods      ##
	####################
	def generate_manual_switch( self, generated ):
		'''generate final switch curve in manual mode.'''
		# get manual curve
		manual = get_fcurve_by_data_path(self.id_data, 
									'curve_to_frame.manual_switch')
		
		if manual is None:
			for KF in generated.keyframe_points:
				KF.co[1] = self.manual_switch
		else:
			for KF in generated.keyframe_points:
				KF.co[1] = manual.evaluate(KF.co[0])
	
	
	
	
	
	def generate_random_switch( self, generated ):
		'''ramdomly generate final switch curve.'''
		






