from ..single_track import single_track
from ..functions import *
import bpy, os, shutil, platform
from math import ceil, floor
from uuid import uuid4








class CurveToFrame(single_track.CurveToFrame, bpy.types.PropertyGroup):
	''' class containing all multi track Property 
			design form curve to frame addon'''
	
