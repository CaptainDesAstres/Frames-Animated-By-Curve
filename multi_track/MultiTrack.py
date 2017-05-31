from .TracksList import *
from .Peaks import Peaks
from ..single_track.CurveToFrameProperty import CurveToFrameProperty
from ..functions import *
import bpy, os, shutil, platform
from math import ceil, floor
from uuid import uuid4








class MultiTrack(bpy.types.PropertyGroup, Peaks, CurveToFrameProperty):
	''' class containing all Curve to frame 
			Properties, methods and operators 
			for multi track feature'''
	
	
	def add_track( self, context ):
		'''add the selected tracks in tracks list'''
		# get new track name and avoid recursive call
		track = self.track_add
		if track == '':
			return
		
		# get the corresponding movieclip
		try:
			track = bpy.data.movieclips[ track ]
		except KeyError:
			return
		
		# check the source is compatible
		if track.source != 'SEQUENCE':
			return
		
		# load tracks if necessary
		if track.curve_to_frame.uid == '':
			track.curve_to_frame.initialize()
		if get_fcurve_by_data_path(track, 'curve_to_frame.peaks_shape') is None:
			track.curve_to_frame.init_peaks_shape_curve()
		
		# add to the list
		new = self.tracks.add()
		new.name = track.name
		new.uid = track.curve_to_frame.uid
		new.track_id = len(self.tracks)-1
		self.selected_track = new.track_id
		
		# clear the add field
		self.track_add=''
	
	
	
	
	#########################
	## list and properties ##
	#########################
	
	track_add = bpy.props.StringProperty(
				name = "Add",
				description = "Add tracks to the list",
				default = '',
				update = add_track )
	
	tracks = bpy.props.CollectionProperty(
				type=Track,
				options = {'LIBRARY_EDITABLE'} )
	
	selected_track = bpy.props.IntProperty( default = -1 )
	
	
	
	
	
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
	
	
