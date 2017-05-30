from ..single_track.SingleTrack import SingleTrack
from ..functions import *
import bpy, os, shutil, platform
from math import ceil, floor
from uuid import uuid4








class MultiTrack(SingleTrack, bpy.types.PropertyGroup):
	''' class containing all multi track Property 
			design form curve to frame addon'''
	
