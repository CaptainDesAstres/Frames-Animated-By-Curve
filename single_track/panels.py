import bpy


class Panel(bpy.types.Panel):
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
			clip.curve_to_frame.panel_single_track(context, layout, clip)
			
		else:
			# Display a request for a movie clip
			row = layout.row()
			row.label( 
					text="select/load an images sequence in Movie Editor.",
					icon="ERROR" )
			row = layout.row()
			row.template_ID(context.space_data, 'clip', open='clip.open' )
			





