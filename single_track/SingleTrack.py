from .Peaks import Peaks
from .CurveToFrameProperty import CurveToFrameProperty
import bpy

class SingleTrack(bpy.types.PropertyGroup, Peaks, CurveToFrameProperty):
	''' class containing all Curve to frame 
			Properties, methods and operators 
			for single track feature'''
	
	
	def update_curves( self, context ):
		'''update curve when settings have been changed'''
		# initialize animation data if required
		if self.id_data.animation_data is None:
			self.id_data.animation_data_create()
		
		if self.id_data.animation_data.action is None:
			self.id_data.animation_data.action = bpy.data.actions.new( 
										name= self.id_data.name+'Action')
		
		# check and get peaks shapes
		peak_shapes = self.check_and_get_peaks_shapes()
		if type(peak_shapes) is str:
			return peak_shapes
		
		# update amplitude net curve
		amplitude_net_curve = self.update_net_amplitude_curve( self.id_data, context )
		
		
		# update peaks curve
		peaks_curve = self.update_peaks_curve(self.id_data, context,
							amplitude_net_curve, peak_shapes )
		
		#update combination curve
		combination_curve = self.update_combination_curve(
												self.id_data, 
												context, 
												amplitude_net_curve,
												peaks_curve
												)
		
		if(type(self.id_data) is bpy.types.MovieClip ):
			# update output curve
			self.update_output_curve(self.id_data, context, combination_curve)
		
		return True
