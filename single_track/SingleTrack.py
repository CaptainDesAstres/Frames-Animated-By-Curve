from .Peaks import Peaks
from .CurveToFrameProperty import CurveToFrameProperty
import bpy

class SingleTrack(bpy.types.PropertyGroup, Peaks, CurveToFrameProperty):
	''' class containing all Curve to frame 
			Properties, methods and operators 
			for single track feature'''
