import bpy, platform
from single_track.panels import Panel as SingleTrackPanel
from functions import *

class ListPanel(bpy.types.Panel):
	'''class of the panel who contains addon multi track control'''
	bl_space_type = "CLIP_EDITOR"
	bl_region_type = "TOOLS"
	bl_label = "Multi track: Tracks list"
	bl_category = "Curve Anim"
	
	def draw(self, context):
		'''the function that draw the addon UI'''
		context.scene.curve_to_frame.draw_track_list_panel( self.layout, context )





class AmplitudePanel(bpy.types.Panel):
	'''class of the panel who contains amplitude and peaks settings control for multi track feature'''
	bl_space_type = "CLIP_EDITOR"
	bl_region_type = "TOOLS"
	bl_label = "Multi track: Amplitude & Peaks Settings"
	bl_category = "Curve Anim"
	
	def draw(self, context):
		'''the function that draw the addon UI'''
		layout = self.layout
		context.scene.curve_to_frame.draw_amplitude_panel( context, layout)





class OutputPanel(bpy.types.Panel):
	'''class of the panel who contains output settings control for multi track feature'''
	bl_space_type = "CLIP_EDITOR"
	bl_region_type = "TOOLS"
	bl_label = "Multi track: Output Settings"
	bl_category = "Curve Anim"
	
	def draw(self, context):
		'''the function that draw the panel'''
		layout = self.layout
		scene = context.scene
		
		scene.curve_to_frame.draw_output( layout, scene )
		
		# draw run button or error message
		#scene.curve_to_frame.draw_run_button( layout )





class SwitchPanel(bpy.types.Panel):
	'''class of the panel who contains tracks switching settings for multi track feature'''
	bl_space_type = "CLIP_EDITOR"
	bl_region_type = "TOOLS"
	bl_category = "Curve Anim"
	bl_label = "Multi track: Track Switch Settings"
	
	def draw(self, context):
		'''the function that draw the panel'''
		layout = self.layout
		
		context.scene.curve_to_frame.draw_switch( layout )





class Panel(SingleTrackPanel):
	'''class containing all needed method to draw panel'''
	
	def draw_track_list_panel( self, layout, context ):
		'''Draw the tracks list Panel'''
		# track adding field
		row = layout.row()
		col = row.column()
		col.prop_search(self, "track_add", bpy.data, "movieclips")
		col = row.column()
		col.operator(
				"clip.open", text='', icon='FILESEL')
		
		# error message if unvalid track
		if self.track_add != '':
			row = layout.row()
			if self.track_add not in bpy.data.movieclips.keys():
				row.label( '  Error: movieclip not found', icon = 'ERROR' )
			else:
				row.label( '  Unvalid choice : only image sequence can be used.',
								icon = 'ERROR' )
		
		# display Tracks list
		row = layout.row()
		col = row.column()
		col.template_list(
				"TrackItem",
				"",
				self,
				"tracks",
				self,
				"selected_track",
				rows=5)
		
		# track list action button
		col = row.column( align=True )
		col.operator("curve_to_frame.tracks_list_action", icon='TRIA_UP', text="").action = 'UP'
		col.operator("curve_to_frame.tracks_list_action", icon='FILE_TICK', text="").action = 'CHECK'
		col.operator("curve_to_frame.tracks_list_action", icon='X', text="").action = 'REMOVE'
		col.operator("curve_to_frame.tracks_list_action", icon='TRIA_DOWN', text="").action = 'DOWN'
		
		# display selected track settings
		if (self.selected_track >= 0 
				and self.selected_track < len(self.tracks) ):
			track = self.tracks[self.selected_track].get(context.scene).curve_to_frame
			
			# Display selected track directory path
			layout.separator()
			row = layout.row()
			row.label( text = "Frame Directory path:" )
			row = layout.row()
			row.label( text= track.path )
			
			# Display selected track source file extension
			row = layout.row()
			col = row.column()
			col.label( text="File type: "+track.ext )
			
			# Display first to last accepted frame name range
			col = row.column()
			col.label( text="Valid frames: "\
				+track.get_frame_name(track.first)+' to '\
				+track.get_frame_name(track.last) )
			
			# Display Start/End settings
			layout.separator()
			row = layout.row()
			col = row.column()
			col.prop(track, "start")
			col = row.column()
			col.prop(track, "end")
	
	
	
	
	
	def draw_amplitude_panel(self, context, layout):
		'''Draw the amplitude panel for multi track'''
		
		refresh_curve = "curve_to_frame.generate_multi_track_curves"
		refresh_mini_maxi = "curve_to_frame.multi_track_get_amplitude_range"
		restore_peak_shape = "curve_to_frame.multi_track_default_peak_shape"
		
		# draw amplitude settings
		self.draw_amplitude( layout,
							refresh_curve, refresh_mini_maxi )
		
		# draw peaks rythm settings
		self.draw_peak(layout, refresh_curve )
		
		# draw peaks profile settings
		self.draw_peak_shape( layout, refresh_curve,
					restore_peak_shape )
		
		# draw combination node settings and combination and output value
		self.draw_combination( layout, refresh_curve, True )
	
	
	
	
	
	def draw_output( self, layout, scene ):
		'''Draw multi track output panel'''
		warning = (not scene.ctf_real_copy \
				and platform.system().lower() not in ['linux', 'unix'])
		
		row = layout.row()
		col = row.column()
		if( check_driver(self.id_data, 'curve_to_frame.' ) ):
			# check no driver is use on curve to frame property
			col.label(text='This function can\'t be used with driver!', 
						icon='ERROR')
		elif(warning):
			# check there is no warning
			col.operator(
				"curve_to_frame.generate_multi_track_curves",
				text="ignore warning and refresh at my one risk",
				icon = 'ERROR')
			
			# A checkbox to get real frame file copy
			col = row.column()
			col.prop( scene, "ctf_real_copy", icon='ERROR' )
			warning = True
		else:
			# draw standart run button
			col.operator(
				"curve_to_frame.generate_multi_track_curves",
				text="Refresh")
			
			# A checkbox to get real frame file copy
			col = row.column()
			col.prop( scene, "ctf_real_copy" )
	
	
	
	
	
	def draw_switch( self, layout ):
		'''Draw multi track switch panel'''
		row = layout.row()
		col = row.column()
		col.prop(self, 'switch_mode')
		
		if self.switch_mode == 'manual':
			col = row.column()
			col.prop(self, 'manual_switch')
		elif self.switch_mode == 'cyclic':
			col = row.column()
			col.prop(self, 'cyclic_mode')
			if self.cyclic_mode == 'custom':
				row = layout.row()
				col = row.column()
				col.prop(self, 'custom_cycle')
				
				if self.get_custom_cycle() is None:
					col = row.column()
					col.label(icon = 'ERROR', text='Unvalid input.')
		
		self.draw_switch_moment( layout )
	
	
	
	
	
	def draw_switch_moment( self, layout ):
		'''Draw the switch moment settings in switch panel'''
		layout.separator()
		row = layout.row()
		row.label(text = 'Switching moment:')
		
		if self.switch_mode == 'manual':
			# switch at perfect frame option when manual switching mode
			row = layout.row()
			row.prop(self, 'switch_at_perfect_frame')
		else:
			# switch at custom instant when no in manual switching mode
			row = layout.row()
			col = row.column()
			col.prop( self, 'switch_at_custom_keyframe' )
			
			col = row.column()
			col.prop( self, 'custom_keyframe' )
			if not self.switch_at_custom_keyframe:
				col.enabled = False
		
		# switch at each peaks starting or keyframe option
		row = layout.row()
		col = row.column()
		col.prop( self, 'switch_at_peaks' )
		col = row.column()
		col.prop( self, 'switch_at_peaks_keyframes' )
		
		layout.separator()
		row = layout.row()
		row.label('Switch when:' )
		
		# switch at peaks value option
		row = layout.row()
		col = row.column()
		col.prop( self, 'switch_when_peaks_get_over' )
		col = row.column()
		col.prop( self, 'peaks_over_trigger_values' )
		if not self.switch_when_peaks_get_over:
			col.enabled = False
		
		row = layout.row()
		col = row.column()
		col.prop( self, 'switch_when_peaks_get_under' )
		col = row.column()
		col.prop( self, 'peaks_under_trigger_values' )
		if not self.switch_when_peaks_get_under:
			col.enabled = False
		
		
		# switch at amplitude value option
		row = layout.row()
		col = row.column()
		col.prop( self, 'switch_when_amplitude_get_over' )
		col = row.column()
		col.prop( self, 'amplitude_over_trigger_values' )
		if not self.switch_when_amplitude_get_over:
			col.enabled = False
		
		row = layout.row()
		col = row.column()
		col.prop( self, 'switch_when_amplitude_get_under' )
		col = row.column()
		col.prop( self, 'amplitude_under_trigger_values' )
		if not self.switch_when_amplitude_get_under:
			col.enabled = False
		
		
		# switch at combination value option
		row = layout.row()
		col = row.column()
		col.prop( self, 'switch_when_combination_get_over' )
		col = row.column()
		col.prop( self, 'combination_over_trigger_values' )
		if not self.switch_when_combination_get_over:
			col.enabled = False
		
		row = layout.row()
		col = row.column()
		col.prop( self, 'switch_when_combination_get_under' )
		col = row.column()
		col.prop( self, 'combination_under_trigger_values' )
		if not self.switch_when_combination_get_under:
			col.enabled = False
		
		
		
		# accuracy settings
		layout.separator()
		row = layout.row()
		row.prop( self, 'values_evaluation_accuracy' )
		
		# switch minimal gap
		row = layout.row()
		col = row.column()
		col.prop( self, 'maximal_switch_gap_option' )
		col = row.column()
		col.prop( self, 'maximal_switch_gap' )
		if not self.maximal_switch_gap_option:
			col.enabled = False
		col = row.column()
		col.prop( self, 'maximal_switch_gap_proportional_option' )
		if not self.maximal_switch_gap_option:
			col.enabled = False
		
		# switch minimal gap
		row = layout.row()
		col = row.column()
		col.prop( self, 'minimal_switch_gap_option' )
		col = row.column()
		col.prop( self, 'minimal_switch_gap' )
		if not self.minimal_switch_gap_option:
			col.enabled = False
		elif self.maximal_switch_gap_option and \
					self.minimal_switch_gap > self.maximal_switch_gap:
			row = layout.row()
			row.label(
					icon='ERROR',
					text='Error: Minimal gap must be smaller than maximal gap!'
					)
		
		
		layout.separator()
		row = layout.row()
		row.operator(
			"curve_to_frame.generate_track_switching_curve",
			 icon='FILE_REFRESH',
			 text="refresh switch curve")





