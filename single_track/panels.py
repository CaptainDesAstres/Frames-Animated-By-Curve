import bpy
from functions import *


class TrackPanel(bpy.types.Panel):
	'''class of the panel who contains addon control'''
	bl_space_type = "CLIP_EDITOR"
	bl_region_type = "TOOLS"
	bl_label = "Single track"
	bl_category = "Curve Anim"
	
	def draw(self, context):
		'''the function that draw the addon UI'''
		layout = self.layout
		
		# check if there is a movie clip set
		if(context.space_data.clip is not None):
			clip = context.space_data.clip
			
			# draw panel
			clip.curve_to_frame.draw_single_track_panel(context, layout, clip)
			
		else:
			# Display a request for a movie clip
			row = layout.row()
			row.label( 
					text="select/load an images sequence in Movie Editor.",
					icon="ERROR" )
			row = layout.row()
			row.template_ID(context.space_data, 'clip', open='clip.open' )
			





class Panel():
	'''class containing all needed method to draw panel'''
	
	def draw_single_track_panel(self, context, layout, clip):
		'''draw the single track panel layout'''
		# draw movieclip load error if required
		error = self.draw_load_error( layout, clip )
		
		if not error:
			refresh_curve = "curve_to_frame.generate_single_track_curves"
			refresh_mini_maxi =\
					"curve_to_frame.single_track_get_amplitude_range"
			restore_peak_shape =\
					"curve_to_frame.single_track_default_peak_shape"
			
			# draw Movie info & settings
			self.draw_track_info( layout )
			
			# draw amplitude settings
			self.draw_amplitude( layout, 
								refresh_curve, refresh_mini_maxi )
			
			# draw peaks rythm settings
			self.draw_peaks(layout, refresh_curve )
			
			# draw peaks profile settings
			self.draw_peaks_profile( layout, refresh_curve,
						restore_peak_shape )
			
			# draw combination node settings and combination and output value
			self.draw_combination_and_output( layout, refresh_curve )
			
			# draw output and rounding settings
			warning = self.draw_single_track_output( layout, context.scene, clip )
			
			# draw run button or error message
			self.draw_run_button( layout, warning )
	
	
	
	
	
	def draw_load_error(self, layout, clip):
		'''draw movieclip load error if required'''
		if(clip.source != 'SEQUENCE'):
			# Display an error message, requesting for a sequence of images
			row = layout.row()
			row.label( text="Current movie can't be use by addon.",
				 icon="ERROR"  )
			row = layout.row()
			row.label( text="Only images sequence are accept." )
			row = layout.row()
			row.template_ID(bpy.context.space_data, 'clip', open='clip.open' )
			
			return True
			
		elif(not self.init):
			# ask to initialize curve to frame on thes MovieClip
			row = layout.row()
			row.operator(
				"curve_to_frame.init_track",
				text="initialize MovieClip info")
			
			return True
			
		return False
	
	
	
	
	
	def draw_track_info(self, layout):
		'''draw Movie info & settings in the panel'''
		# Display the directory path
		row = layout.row()
		col = row.column()
		col.label( text = "Frame Directory path:" )
		col = row.column()
		col.operator(
			"curve_to_frame.init_track",
			icon = 'FILE_REFRESH',
			text = '')
		row = layout.row()
		row.label( text= self.path )
		
		# Display frame extension
		row = layout.row()
		col = row.column()
		col.label( text="File type: "+self.ext )
		
		# Display first to last accepted frame name range
		col = row.column()
		col.label( text="Valid frames: "\
			+self.get_frame_name(self.first)+' to '\
			+self.get_frame_name(self.last) )
		
		# Display Start/End settings
		layout.separator()
		row = layout.row()
		col = row.column()
		col.prop(self, "start")
		col = row.column()
		col.prop(self, "end")
	
	
	
	
	
	def draw_amplitude( 
						self,
						layout, 
						refresh_curve, 
						refresh_mini_maxi):
		'''draw amplitude settings into the panel'''
		# A float amplitude field
		layout.separator()
		row = layout.row()
		col = row.column()
		col.prop(self, "amplitude")
		
		# A field to remind F-Curve min and max value
		fCurve = get_fcurve_by_data_path(self.id_data, 'curve_to_frame.amplitude')
		if(fCurve is None):
			m = M = self.amplitude
		else:
			m, M = get_curve_limit(fCurve)
		m = round(m*1000)/1000
		M = round(M*1000)/1000
		col = row.column()
		col.label( text = "(Goes from "+str(m)\
					+" to "+str(M)+')' )
		
		# A field to set the min F-Curve Value to 
		# assigne to the first frames
		row = layout.row()
		col = row.column()
		col.prop(self, "mini")
		
		# A field to set the max F-Curve Value to 
		# assigne to the last frames
		col = row.column()
		col.prop(self, "maxi")
		if(self.combination_mode == 'ignore_amplitude'):
			col.enabled = False
		
		# A button to get curve min max value
		col = row.column()
		col.operator(refresh_mini_maxi,
					text = 'auto')
		# display net amplitude value
		col = row.column()
		col.enabled = False
		col.prop(self, "amplitude_net")
		col = row.column()
		col.operator(
			refresh_curve,
			text='',
			icon='FILE_REFRESH')
	
	
	
	
	
	def draw_peaks(self, layout, refresh_curve):
		'''draw peaks rythm settings into the panel'''
		# a button to activate and set peaks per minute
		layout.separator()
		row = layout.row()
		col = row.column()
		col.prop(self, "rate")
		col = row.column()
		col.prop(self, "rate_unit", text='')
		col = row.column()
		col.prop(self, "auto_constant")
		col = row.column()
		col.prop(self, "accuracy")
		
		row = layout.row()
		col = row.column()
		col.prop(self, "synchronized")
		col = row.column()
		if (not self.synchronized):
			col.enabled = False
		col.prop(self, "anticipate")
		col = row.column()
		col.enabled = False
		col.prop(self, "peaks")
		col = row.column()
		col.operator(
			refresh_curve,
			text='',
			icon='FILE_REFRESH')
	
	
	
	




