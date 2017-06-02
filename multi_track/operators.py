import bpy


class CurvesRefresh(bpy.types.Operator):
	'''operator to initialize or refresh curve to frame info of the scene'''
	bl_idname = "curve_to_frame.generate_multi_track_curves"
	bl_label= "refresh multi track curves"
	bl_options = {'INTERNAL'}
	
	def execute(self, context):
		'''refresh scene curves'''
		status = context.scene.curve_to_frame.update_curves( context )
		if status is True:
			return {'FINISHED'}
		else:
			self.report( {'ERROR'}, status )
			return {'CANCELLED'}





