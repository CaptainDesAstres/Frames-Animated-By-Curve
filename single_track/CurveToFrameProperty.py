from functions import *
import bpy, os
from math import ceil, floor




class CurveToFrameProperty():
	'''class containing all the property usefull for track settings'''
	
	def check_driver( self ):
		'''check the object have no driver on property used by the addon'''
		if(		self.id_data.animation_data is None
				or self.id_data.animation_data.drivers is None):
			return False
		
		for driver in self.id_data.animation_data.drivers:
			if( driver.data_path.startswith('curve_to_frame.') ):
				return True
		
		return False
	
	
	
	#################################################
	##     output settings                         ##
	#################################################
	
	
	
	
	# output path
	output_path = bpy.props.StringProperty(
		name = "output",
		description = "Output directory path.",
		default = '//',
		subtype = 'DIR_PATH')
	
	
