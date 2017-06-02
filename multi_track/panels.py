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
