bl_info = {
    "name": "Frames Animated By Curve",
    "author": "Captain DesAstres",
    "version": (0, 1),
    "blender": (2, 78, 0),
    "location": "Movie Clip Editor -> Tools",
    "description": "A Blender plugin who take a short animation of a simple move to make a bigger one, using a F-Curve.",
    "wiki_url": "https://github.com/CaptainDesAstres/Frames-Animated-By-Curve",
    "category": "Animation"}

import os, sys
sys.path.append( os.path.abspath('.') )
from functions import *
from single_track.SingleTrack import SingleTrack
from multi_track.MultiTrack import MultiTrack
from multi_track.TracksList import *
import single_track.operators
import multi_track.operators
import bpy, platform






def register():
	'''addon register'''
	# single track feature settings
	bpy.utils.register_class(SingleTrack)
	
	# single track feature Panel
	bpy.utils.register_class(SingleTrack.SingleTrackPanel)
	
	# single track feature Operator
	bpy.utils.register_class(single_track.operators.InitTrack)
	bpy.utils.register_class(SingleTrack.RestoreDefaultPeakShape)
	bpy.utils.register_class(SingleTrack.RefreshClipMiniMaxi)
	bpy.utils.register_class(single_track.operators.CurvesRefresh)
	bpy.utils.register_class(single_track.operators.CurveToFrame)
	
	# track object and operator
	bpy.utils.register_class(Track)
	bpy.utils.register_class(TrackItem)
	bpy.utils.register_class(TracksActions)
	
	# multi track feature settings
	bpy.utils.register_class(MultiTrack)
	
	# multi track feature Panel
	bpy.utils.register_class(SingleTrack.MultiTrackTracksPanel)
	bpy.utils.register_class(SingleTrack.MultiTrackAmplitudePanel)
	bpy.utils.register_class(SingleTrack.MultiTrackOutputPanel)
	
	# multi track feature Operator
	bpy.utils.register_class(SingleTrack.RestoreMultiTrackDefaultPeakShape)
	bpy.utils.register_class(SingleTrack.RefreshSceneMiniMaxi)
	bpy.utils.register_class(multi_track.operators.CurvesRefresh)
	
	bpy.types.MovieClip.curve_to_frame = bpy.props.PointerProperty(type=SingleTrack)
	bpy.types.Scene.curve_to_frame = bpy.props.PointerProperty(type=MultiTrack)
	
	# Add to scene type a property to define if script does real file copy
	if platform.system().lower() in ['linux', 'unix']:
		bpy.types.Scene.ctf_real_copy = bpy.props.BoolProperty(
			name="Make real copy file", 
			description="Do Frames Animated By Curve add-on make \
					real file copy rather than symbolic link.",
			options = {'LIBRARY_EDITABLE'},
			default = False)
	else:
		bpy.types.Scene.ctf_real_copy = bpy.props.BoolProperty(
			name="Make real copy file", 
			description="You must keep this enable as your system \
					don't implement symbolic link. disable at your one risk!",
			options = {'LIBRARY_EDITABLE'},
			default = True)
	
	print("Frames Animated By Curve is enabled")




def unregister():
	'''addon unregister'''
	# single track feature settings
	bpy.utils.unregister_class(SingleTrack)
	
	# single track feature Panel
	bpy.utils.unregister_class(SingleTrack.SingleTrackPanel)
	
	# single track feature Operator
	bpy.utils.unregister_class(single_track.operators.InitTrack)
	bpy.utils.unregister_class(SingleTrack.RestoreDefaultPeakShape)
	bpy.utils.unregister_class(SingleTrack.RefreshClipMiniMaxi)
	bpy.utils.unregister_class(single_track.operators.CurvesRefresh)
	bpy.utils.unregister_class(single_track.operators.CurveToFrame)
	
	# track object and operator
	bpy.utils.unregister_class(Track)
	bpy.utils.unregister_class(TrackItem)
	bpy.utils.unregister_class(TracksActions)
	
	# multi track feature settings
	bpy.utils.unregister_class(MultiTrack)
	
	# multi track feature Panel
	bpy.utils.unregister_class(SingleTrack.MultiTrackTracksPanel)
	bpy.utils.unregister_class(SingleTrack.MultiTrackAmplitudePanel)
	bpy.utils.unregister_class(SingleTrack.MultiTrackOutputPanel)
	
	# multi track feature Operator
	bpy.utils.unregister_class(SingleTrack.RestoreMultiTrackDefaultPeakShape)
	bpy.utils.unregister_class(SingleTrack.RefreshSceneMiniMaxi)
	bpy.utils.unregister_class(multi_track.operators.CurvesRefresh)
	print("Frames Animated By Curve is disabled")

