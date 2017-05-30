from ..single_track.CurveToFrameProperty import CurveToFrameProperty
from ..functions import *
import bpy, os, shutil, platform
from math import ceil, floor
from uuid import uuid4








class MultiTrack(bpy.types.PropertyGroup, CurveToFrameProperty):
	''' class containing all Curve to frame 
			Properties, methods and operators 
			for multi track feature'''
