import bpy

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












