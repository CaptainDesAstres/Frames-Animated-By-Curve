from .SwitchMoment import SwitchMoment
import bpy
from functions import *
from random import randint

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
		tracks_count = len(self.tracks)
		if tracks_count <= 1:
			for KF in generated_switch.keyframe_points:
				KF.co[1] = 0
		elif self.switch_mode == 'manual':
			self.generate_manual_switch(generated_switch)
		elif self.switch_mode == 'random':
			self.generate_random_switch(generated_switch)
		elif self.switch_mode == 'random_forced':
			self.generate_random_switch(generated_switch, True)
		elif self.switch_mode == 'cyclic':
			self.generate_cyclic_switch(generated_switch)
		
		
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
				'Track are randomly choosen',				1),
			
			('random_forced',		'Ramdomly (never the same)',
				'Track are randomly choosen and script make sure that the track is never 2 time the same',				2),
			
			('cyclic',		'cyclically',
				'Track is changed according to a cycle',				3)
			
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
	
	# cyclic mode
	cyclic_mode = bpy.props.EnumProperty(
		name = '',
		description = 'Define the cycle mode.',
		default = 'ascending',
		items = [
#			(identifier,			name,
#				description, number)
			
			('ascending',		'In ascending order',
				'Use the first track, then the second, then the third, and so on until the last track, then restart from the first…',				0),
			
			('descending',		'In descending order',
				'Use the last track, then the previous, then the previous, and so on until the first one, then restart from the last…',				1),
			
			('asc_desc',		'In ascending then descending order',
				'Use ascending order until the last track then descending order until the first one and so on…',				2),
			
			('custom',		'In custom order',
				'Use a custom order',				3)
			
			],
		options = {'LIBRARY_EDITABLE'},
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
		tracks_count = len(self.tracks)
		# get manual curve
		manual = get_fcurve_by_data_path(self.id_data, 
									'curve_to_frame.manual_switch')
		
		if manual is None:
			for KF in generated.keyframe_points:
				KF.co[1] = self.manual_switch % tracks_count
		else:
			for KF in generated.keyframe_points:
				KF.co[1] = manual.evaluate(KF.co[0]) % tracks_count
	
	
	
	
	
	def generate_random_switch( self, generated, never_the_same = False ):
		'''ramdomly generate final switch curve.'''
		tracks_count = len(self.tracks)-1
		
		if never_the_same:
			cur = prev = -1
			for KF in generated.keyframe_points:
				while cur == prev:
					cur = randint( 0, tracks_count )
				prev = KF.co[1] = cur
			
		else:
			for KF in generated.keyframe_points:
				KF.co[1] = randint( 0, tracks_count )
	
	
	
	
	
	def generate_cyclic_switch( self, generated ):
		'''generate final switch curve acconding to a cycle.'''
		# get cycle
		count = len(self.tracks)
		asc = list(range( 0, count ))
		if self.cyclic_mode == 'ascending':
			cycle = asc
		elif self.cyclic_mode == 'descending':
			cycle = asc
			cycle.reverse()
		elif self.cyclic_mode == 'asc_desc':
			cycle = list(asc)
			asc.reverse()
			cycle += asc[1:-1]
		elif self.cyclic_mode == 'custom':
			cycle = asc
		
		# generate switch curve
		i = 0
		cycle_length = len(cycle)
		for KF in generated.keyframe_points:
			KF.co[1] = cycle[i]
			i += 1
			i = i % cycle_length






