import bpy, platform
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
			clip.curve_to_frame.draw_panel(context, layout, clip)
			
		else:
			# Display a request for a movie clip
			row = layout.row()
			row.label( 
					text="select/load an images sequence in Movie Editor.",
					icon="ERROR" )
			row = layout.row()
			row.template_ID(context.space_data, 'clip', open='clip.open' )
			





class Panel():
	'''Class containing all needed methods to draw panel'''
	
	def draw_panel(self, context, layout, clip):
		'''Draw the single track panel layout'''
		# draw movieclip load error if required
		error = self.draw_load_error( layout, clip )
		
		if not error:
			refresh_curve = "curve_to_frame.generate_single_track_curves"
			refresh_mini_maxi =\
					"curve_to_frame.single_track_get_amplitude_range"
			restore_peak_shape =\
					"curve_to_frame.single_track_default_peak_shape"
			run_operator = "curve_to_frame.render_single_track"
			
			# draw Movie info & settings
			self.draw_track_info( layout )
			
			# draw amplitude settings
			self.draw_amplitude( layout, 
								refresh_curve, refresh_mini_maxi )
			
			# draw peaks rythm settings
			self.draw_peak(layout, refresh_curve )
			
			# draw peaks profile settings
			self.draw_peak_shape( layout, refresh_curve,
						restore_peak_shape )
			
			# draw combination node settings and combination and output value
			self.draw_combination( layout, refresh_curve )
			
			# draw run button or error message
			self.draw_run_button( layout, run_operator, context.scene )
	
	
	
	
	
	def draw_load_error(self, layout, clip):
		'''Draw track load error part of single track panel'''
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
		'''Draw track info and settings part of single and multi track panels'''
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
		layout.separator()
	
	
	
	
	
	def draw_amplitude( 
						self,
						layout, 
						refresh_curve, 
						refresh_mini_maxi):
		'''Draw amplitude settings part of single and multi track panels'''
		# A float amplitude field
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
	
	
	
	
	
	def draw_peak(self, layout, refresh_curve):
		'''Draw peak rate settings part of single and multi track panels'''
		# peaks rate settings
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
		
		# amplitude synchronized settings
		row = layout.row()
		col = row.column()
		col.prop(self, "synchronized")
		col = row.column()
		if (not self.synchronized):
			col.enabled = False
		col.prop(self, "anticipate")
		
		# resuling settings
		col = row.column()
		col.enabled = False
		col.prop(self, "peaks")
		col = row.column()
		col.operator(
			refresh_curve,
			text='',
			icon='FILE_REFRESH')
	
	
	
	
	
	def draw_peak_shape(
				self,
				layout,
				refresh_curve,
				restore_shape
				):
		'''Draw peak shape settings part of single and multi track panels'''
		layout.separator()
		row = layout.row()
		
		# restore default shape button
		col = row.column()
		col.operator(
			restore_shape,
			text='',
			icon='LOAD_FACTORY')
		
		# display peaks shapes settings
		col = row.column()
		col.prop(self, "peaks_shape")
		col = row.column()
		col.prop(self, "peaks_shape_range_start")
		col = row.column()
		col.prop(self, "peaks_shape_range_end")
		
		
		# refresh curve
		col = row.column()
		col.operator(
			refresh_curve,
			text='',
			icon='FILE_REFRESH')
	
	
	
	
	
	def draw_combination( 
						self, 
						layout, 
						refresh_curve, 
						no_output=False ):
		'''Draw combination settings part of single and multi track panels'''
		# combination mode field
		layout.separator()
		row = layout.row()
		col = row.column()
		col.prop(self, 'combination_mode')
		
		# visualize combination of peaks and amplitude curve
		col = row.column()
		col.enabled = False
		col.prop(self, "combination")
		
		
		
		# A field to choose between Round Floor and 
		# Ceil rounding method
		row = layout.row()
		col = row.column()
		col.prop(self, "rounding")
		
		# visualize output frame
		if not no_output:
			col = row.column()
			col.enabled = False
			col.prop(self, "output")
		
		# refresh curve
		col = row.column()
		col.operator(
			refresh_curve,
			text='',
			icon='FILE_REFRESH')
		
		layout.separator()
	
	
	
	
	
	def draw_run_button( self, layout, run_operator, scene ):
		'''Draw single track run button and warning message'''
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
				run_operator,
				text="ignore warning and run at my one risk",
				icon = 'ERROR')
			
			# A checkbox to get real frame file copy
			col = row.column()
			col.prop( scene, "ctf_real_copy", icon='ERROR' )
			warning = True
		else:
			# draw standart run button
			col.operator(
				run_operator,
				text="run")
			
			# A checkbox to get real frame file copy
			col = row.column()
			col.prop( scene, "ctf_real_copy" )
		




