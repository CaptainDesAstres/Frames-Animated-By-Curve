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


# Add to scene type a property to define if script does real file copy
if platform.system().lower() in ['linux', 'unix']:
	bpy.types.Scene.CtFRealCopy = bpy.props.BoolProperty(
		name="Make real copy file", 
		description="Do Frames Animated By Curve add-on make \
				real file copy rather than symbolic link.",
		options = {'LIBRARY_EDITABLE'},
		default = False)
else:
	bpy.types.Scene.CtFRealCopy = bpy.props.BoolProperty(
		name="Make real copy file", 
		description="You must keep this enable as your system \
				don't implement symbolic link. disable at your one risk!",
		options = {'LIBRARY_EDITABLE'},
		default = True)




def register():
	'''addon register'''
	bpy.utils.register_class(CtFRestoreDefaultPeakShape)
	bpy.utils.register_class(CtFRestoreMultiTrackDefaultPeakShape)
	bpy.utils.register_class(TracksActions)
	bpy.utils.register_class(CtFRefresh)
	bpy.utils.register_class(Track)
	bpy.utils.register_class(TrackItem)
	bpy.utils.register_class(CtFRefreshClipMiniMaxi)
	bpy.utils.register_class(CtFRefreshSceneMiniMaxi)
	bpy.utils.register_class(CtFSingleTrackCurvesRefresh)
	bpy.utils.register_class(CtFMultiTrackCurvesRefresh)
	bpy.utils.register_class(CtF)
	
	bpy.types.MovieClip.CtF = bpy.props.PointerProperty(type=CtF)
	bpy.types.Scene.CtF = bpy.props.PointerProperty(type=CtF)
	
	bpy.utils.register_class(SingleTrackCurveToFrame)
	bpy.utils.register_class(SingleTrackPanel)
	bpy.utils.register_class(MultiTrackTracksPanel)
	bpy.utils.register_class(MultiTrackAmplitudePanel)
	bpy.utils.register_class(MultiTrackOutputPanel)
	print("Frames Animated By Curve is enabled")




def unregister():
	'''addon unregister'''
	bpy.utils.unregister_class(CtFRestoreDefaultPeakShape)
	bpy.utils.unregister_class(CtFRestoreMultiTrackDefaultPeakShape)
	bpy.utils.unregister_class(TracksActions)
	bpy.utils.unregister_class(CtFRefresh)
	bpy.utils.unregister_class(Track)
	bpy.utils.unregister_class(TrackItem)
	bpy.utils.unregister_class(CtFRefreshClipMiniMaxi)
	bpy.utils.unregister_class(CtFRefreshSceneMiniMaxi)
	bpy.utils.unregister_class(CtFSingleTrackCurvesRefresh)
	bpy.utils.unregister_class(CtFMultiTrackCurvesRefresh)
	bpy.utils.unregister_class(CtF)
	bpy.utils.unregister_class(SingleTrackPanel)
	bpy.utils.unregister_class(MultiTrackAmplitudePanel)
	bpy.utils.unregister_class(SingleTrackCurveToFrame)
	bpy.utils.unregister_class(MultiTrackTracksPanel)
	bpy.utils.unregister_class(MultiTrackOutputPanel)
	print("Frames Animated By Curve is disabled")

