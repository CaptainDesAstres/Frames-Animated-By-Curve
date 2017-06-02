import bpy
from functions import *


class AmplitudeMinMax(bpy.types.Operator):
	'''operator to initialize or refresh curve to frame info of the scene'''
	bl_idname = "curve_to_frame.multi_track_get_amplitude_range"
	bl_label= "get scene amplitude curve mini and maxi value"
	bl_options = {'INTERNAL'}
	
	def execute(self, context):
		'''get scene amplitude curve mini and maxi value'''
		scene = context.scene
		
		fCurve = get_fcurve_by_data_path(scene, 'curve_to_frame.amplitude')
		if(fCurve is None):
			m = M = scene.curve_to_frame.amplitude
		else:
			scene.curve_to_frame.mini, scene.curve_to_frame.maxi = get_curve_limit(fCurve)
		
		# update curves
		status = scene.curve_to_frame.update_curves( context )
		if status is True:
			return {'FINISHED'}
		else:
			self.report( {'ERROR'}, status )
			return {'CANCELLED'}





class RestoreDefaultPeakShape(bpy.types.Operator):
	'''Restore default peak shape settings for multi track'''
	bl_idname = "curve_to_frame.multi_track_default_peak_shape"
	bl_label= "restore default peak shape settings for multi track"
	bl_options = {'INTERNAL'}
	
	def execute(self, context):
		'''restore default peak shape settings for multi track'''
		context.scene.curve_to_frame.init_peaks_shape_curve()
		return {'FINISHED'}





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





