from .TracksList import *
from .Peaks import Peaks
from single_track.CurveToFrameProperty import CurveToFrameProperty
from functions import *
import bpy, os, shutil, platform
from math import ceil, floor
from uuid import uuid4








class MultiTrack(bpy.types.PropertyGroup, TracksList, Peaks, CurveToFrameProperty):
	''' class containing all Curve to frame 
			Properties, methods and operators 
			for multi track feature'''
	
	
	def update_curves( self, context ):
		'''update curve when settings have been changed'''
		scene = self.id_data
		# initialize animation data if required
		if scene.animation_data is None:
			scene.animation_data_create()
		
		if scene.animation_data.action is None:
			scene.animation_data.action = bpy.data.actions.new( 
										name= scene.name+'Action')
		
		# check and get peaks shapes
		peak_shapes = self.check_and_get_peaks_shapes()
		if type(peak_shapes) is str:
			return peak_shapes
		
		# update amplitude net curve
		amplitude_net_curve = self.update_net_amplitude_curve( scene, context )
		
		
		# update peaks curve
		peaks_curve = self.update_peaks_curve(scene, context,
							amplitude_net_curve, peak_shapes )
		
		#update combination curve
		combination_curve = self.update_combination_curve(
												scene, 
												context, 
												amplitude_net_curve,
												peaks_curve
												)
		
		return True
	
	
