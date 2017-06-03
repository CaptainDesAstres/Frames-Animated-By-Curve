import bpy,os
from uuid import uuid4


class Track():
	'''A class containing all properties and methods
		relative to the track info and settings for 
		Curve To Frame addon'''
	
	def set_end_frame(self, context):
		'''check that start and end frame are valid when 
				changing end frame settings'''
		# check end isn't over clip size
		if self.end > self.size:
			self.end = self.size
		
		# check start isn't over end
		if self.start >= self.end:
			if self.end > 1:
				self['start'] = self.end - 1
			else:
				self['start'] = 1
				self['end'] = 2
	
	
	
	
	
	def set_start_frame(self, context):
		'''check that start and end frame are valid 
				when changing start frame settings'''
		# check start isn't under 0
		if self.start < 1:
			self.start = 1
		
		# check start isn't over end
		if self.start >= self.end:
			if self.start < self.size:
				self['end'] = self.start + 1
			else:
				self['start'] = self.size - 1
				self['end'] = self.size
	
	
	
	
	# flag to know if curve to frame have been initialize on this MovieClip
	init = bpy.props.BoolProperty(default = False)
	uid = bpy.props.StringProperty( default = '' )
	
	#################################################
	##     clip settings                           ##
	#################################################
	
	path = bpy.props.StringProperty() # The sources directory path
	prefix = bpy.props.StringProperty() # the source name prefix
	suffix = bpy.props.StringProperty() # the source name suffix
	number_size = bpy.props.IntProperty() # the source name frame number size in char
	first = bpy.props.IntProperty() # the first frame number (in source file name)
	last = bpy.props.IntProperty() # the last frame number (in source file name)
	
	# first frame of the clip to use
	start = bpy.props.IntProperty(
		name = "First frame",
		description = "first frame that Frames Animated \
					By Curve add-on must take in count",
		default = 1,
		min = 1,
		update = set_start_frame)
	
	# last frame of the clip to use
	end = bpy.props.IntProperty(
		name = "Last frame",
		description = "last frame that Frames Animated \
					By Curve add-on must take in count",
		update = set_end_frame)
	
	
	size = bpy.props.IntProperty() # number of frame of the sequence
	ext = bpy.props.StringProperty() # extension of source file
	
	
	
	
	
	def initialize( self ):
		'''init or reload movieclip info'''
		clip = self.id_data
		
		# get source path and extension
		self.path, name = os.path.split(bpy.path.abspath(clip.filepath))
		self.path += '/'
		name, self.ext = os.path.splitext( name )
		
		# get file naming prefix, suffix and length
		l = len(name)
		n = l-1
		while ( not name[n].isdigit() and n > 0 ):
			n -= 1
		self.suffix = name[n+1:l]
		self.prefix = name[0:n].rstrip('0123456789')
		self.number_size = l - len(self.suffix)-len(self.prefix)
		
		# Get clip length and first and last frame number
		self.first = int(name[len(self.suffix):n+1])
		self.size = clip.frame_duration
		self.last = self.first + self.size -1
		
		# adapt curve_to_frame.end property if needed
		if(not self.init or self.end > self.size):
			self.end = self.size
			self.init = True
		
		# allocate an uid to the clip
		if(self.uid == '' ):
			self.uid = str(uuid4())
		
		return {'FINISHED'}
	
	
	
	
	
	def get_frame_name(self, n):
		'''return the file name of a frame'''
		return	( self.prefix +
					str(int(n)).rjust(self.number_size, '0')+
					self.suffix + self.ext )
	
	
	
	
	
	def check_image_file( self ):
		'''check in all the movieclip sequence image exists'''
		for fr in range( self.first,
					self.last+1 ):
			if not os.path.exists( self.path + self.get_frame_name( fr ) ):
				return False
		return True
	
	
	
	
	
	
	
