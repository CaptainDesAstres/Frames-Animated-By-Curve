bl_info = {
    "name": "Frames Animated By Curve",
    "author": "Captain DesAstres",
    "version": (0, 1),
    "blender": (2, 78, 0),
    "location": "Movie Clip Editor -> Tools",
    "description": "A Blender plugin who take a short animation of a simple move to make a bigger one, using a F-Curve.",
    "wiki_url": "https://github.com/CaptainDesAstres/Frames-Animated-By-Curve",
    "category": "Animation"}

from .functions import *
from .main import *
import bpy, platform






def register():
	'''addon register'''
	bpy.utils.register_class(CurveToFrame.RestoreDefaultPeakShape)
	bpy.utils.register_class(CurveToFrame.RestoreMultiTrackDefaultPeakShape)
	bpy.utils.register_class(CurveToFrame.TracksActions)
	bpy.utils.register_class(CurveToFrame.InitMovieClip)
	bpy.utils.register_class(CurveToFrame.Track)
	bpy.utils.register_class(CurveToFrame.TrackItem)
	bpy.utils.register_class(CurveToFrame.RefreshClipMiniMaxi)
	bpy.utils.register_class(CurveToFrame.RefreshSceneMiniMaxi)
	bpy.utils.register_class(CurveToFrame.SingleTrackCurvesRefresh)
	bpy.utils.register_class(CurveToFrame.MultiTrackCurvesRefresh)
	bpy.utils.register_class(CurveToFrame)
	bpy.utils.register_class(CurveToFrame.SingleTrackCurveToFrame)
	bpy.utils.register_class(CurveToFrame.SingleTrackPanel)
	bpy.utils.register_class(CurveToFrame.MultiTrackTracksPanel)
	bpy.utils.register_class(CurveToFrame.MultiTrackAmplitudePanel)
	bpy.utils.register_class(CurveToFrame.MultiTrackOutputPanel)
	
	bpy.types.MovieClip.curve_to_frame = bpy.props.PointerProperty(type=CurveToFrame)
	bpy.types.Scene.curve_to_frame = bpy.props.PointerProperty(type=CurveToFrame)
	
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
	bpy.utils.unregister_class(CurveToFrame.RestoreDefaultPeakShape)
	bpy.utils.unregister_class(CurveToFrame.RestoreMultiTrackDefaultPeakShape)
	bpy.utils.unregister_class(CurveToFrame.TracksActions)
	bpy.utils.unregister_class(CurveToFrame.InitMovieClip)
	bpy.utils.unregister_class(CurveToFrame.Track)
	bpy.utils.unregister_class(CurveToFrame.TrackItem)
	bpy.utils.unregister_class(CurveToFrame.RefreshClipMiniMaxi)
	bpy.utils.unregister_class(CurveToFrame.RefreshSceneMiniMaxi)
	bpy.utils.unregister_class(CurveToFrame.SingleTrackCurvesRefresh)
	bpy.utils.unregister_class(CurveToFrame.MultiTrackCurvesRefresh)
	bpy.utils.unregister_class(CurveToFrame)
	bpy.utils.unregister_class(CurveToFrame.SingleTrackPanel)
	bpy.utils.unregister_class(CurveToFrame.MultiTrackAmplitudePanel)
	bpy.utils.unregister_class(CurveToFrame.SingleTrackCurveToFrame)
	bpy.utils.unregister_class(CurveToFrame.MultiTrackTracksPanel)
	bpy.utils.unregister_class(CurveToFrame.MultiTrackOutputPanel)
	print("Frames Animated By Curve is disabled")

