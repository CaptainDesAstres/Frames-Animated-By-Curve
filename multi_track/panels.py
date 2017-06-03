import bpy, platform
from single_track.panels import Panel as SingleTrackPanel

class ListPanel(bpy.types.Panel):
	'''class of the panel who contains addon multi track control'''
	bl_space_type = "CLIP_EDITOR"
	bl_region_type = "TOOLS"
	bl_label = "Multi track: Tracks list"
	bl_category = "Curve Anim"
	
	def draw(self, context):
		'''the function that draw the addon UI'''
		context.scene.curve_to_frame.panel_tracks( self.layout, context )





class AmplitudePanel(bpy.types.Panel):
	'''class of the panel who contains amplitude and peaks settings control for multi track feature'''
	bl_space_type = "CLIP_EDITOR"
	bl_region_type = "TOOLS"
	bl_label = "Multi track: Amplitude & Peaks Settings"
	bl_category = "Curve Anim"
	
	def draw(self, context):
		'''the function that draw the addon UI'''
		layout = self.layout
		context.scene.curve_to_frame.panel_multi_track_amplitude_and_peaks( context, layout)





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
		
		warning = scene.curve_to_frame.draw_output( layout, scene )
		
		# draw run button or error message
		#scene.curve_to_frame.draw_run_button( layout, warning )





class Panel(SingleTrackPanel):
	'''class containing all needed method to draw panel'''
	
	
	
	
	
	
	
	def draw_output( self, layout, scene ):
		'''Draw multi track output panel'''
		warning = False
		# A field to set the output path
		row = layout.row()
		col = row.column()
		col.prop(self, "output_path")
		
		# A checkbox to get real frame file copy
		col = row.column()
		if(not scene.ctf_real_copy \
				and platform.system().lower() not in ['linux', 'unix']):
			col.prop( scene, "ctf_real_copy", icon='ERROR' )
			warning = True
		else:
			col.prop( scene, "ctf_real_copy" )
		
		return warning





