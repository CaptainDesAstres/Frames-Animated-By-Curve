from .Peaks import Peaks
from .CurveToFrameProperty import CurveToFrameProperty
import bpy

class SingleTrack(bpy.types.PropertyGroup, Peaks, CurveToFrameProperty):
	''' class containing all Curve to frame 
			Properties, methods and operators 
			for single track feature'''
	
	
	def update_curves( self, context ):
		'''update curve when settings have been changed'''
		clip = self.id_data
		# initialize animation data if required
		if clip.animation_data is None:
			clip.animation_data_create()
		
		if clip.animation_data.action is None:
			clip.animation_data.action = bpy.data.actions.new( 
										name= clip.name+'Action')
		
		# check and get peaks shapes
		peak_shapes = self.check_and_get_peaks_shapes()
		if type(peak_shapes) is str:
			return peak_shapes
		
		# update amplitude net curve
		amplitude_net_curve = self.update_net_amplitude_curve( clip, context )
		
		
		# update peaks curve
		peaks_curve = self.update_peaks_curve(clip, context,
							amplitude_net_curve, peak_shapes )
		
		#update combination curve
		combination_curve = self.update_combination_curve(
												clip, 
												context, 
												amplitude_net_curve,
												peaks_curve
												)
		
		# update output curve
		self.update_output_curve(clip, context, combination_curve)
		
		return True
