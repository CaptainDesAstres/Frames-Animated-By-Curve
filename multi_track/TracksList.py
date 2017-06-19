import bpy
from functions import *


class Track(bpy.types.PropertyGroup):
	'''object use to be listed as track in tracks list'''
	
	def set_end_frame(self, context):
		'''check that start and end frame are valid when 
				changing end frame settings'''
		size = self.get(True).curve_to_frame.size
		# check end isn't over clip size
		if self.end > size:
			self.end = size
		
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
			size = self.get(True).curve_to_frame.size
			if self.start < size:
				self['end'] = self.start + 1
			else:
				self['start'] = size - 1
				self['end'] = size
	
	
	
	# all properties
	name = bpy.props.StringProperty()
	uid = bpy.props.StringProperty()
	track_id = bpy.props.IntProperty()
	start = bpy.props.IntProperty(update = set_start_frame)
	end = bpy.props.IntProperty(update = set_end_frame)
	
	def get( self, rename = False):
		'''return the movie clip corresponding to this track'''
		# get movieclip by name
		try:
			track = bpy.data.movieclips[ self.name ]
			if track.curve_to_frame.uid == self.uid:
				return track
		except KeyError:
			pass
		
		# get it by uid in case name have been changed
		for track in bpy.data.movieclips:
			if track.curve_to_frame.uid == self.uid:
				
				if rename:
					# update with new name 
					try:
						self.name = track.name
					except AttributeError:
						print('Track renaming error on '+self.name)
				
				return track
		
		# if none corresponding movieclip finded
		return None



class TrackItem(bpy.types.UIList):
	'''Item to display tracks in a list template'''
	
	def draw_item( 
				self, 
				context, 
				layout, 
				data, 
				item, 
				icon, 
				active_data, 
				active_propname, 
				index ):
		'''draw item row'''
		# display name and index in list
		sp = layout.split(0.05)
		col = sp.column()
		col.label( str(item.track_id) )
		sp = sp.split(0.75)
		col = sp.column()
		col.label(item.name, icon='CLIP')
		col = sp.column()
		col.label('['+str(item.start)+'-'+str(item.end)+']')





class TracksActions(bpy.types.Operator):
	'''Tacks list action operator'''
	bl_idname = "curve_to_frame.tracks_list_action"
	bl_label = "Track Action"
	bl_description = "Track Action:\n\
			- Move up selected track.\n\
			- Check all Tracks.\n\
			- Delete selected track.\n\
			- Move down selected track."
	bl_options = {'INTERNAL'}
	
	action = bpy.props.EnumProperty(
		items=(
			('UP', "Up", ""),
			('DOWN', "Down", ""),
			('REMOVE', "Remove", ""),
			('CHECK', "Check", ""),
		)
	)
	
	def invoke(self, context, event):
		scn = context.scene
		i = scn.curve_to_frame.selected_track
		
		try:
			item = scn.curve_to_frame.tracks[i]
		except IndexError:
			self.report({'ERROR'}, 'Error: bad selection')
			return {"CANCELLED"}
		
		if self.action == 'DOWN':
			# move selected track down
			if( i < len(scn.curve_to_frame.tracks)-1 ):
				scn.curve_to_frame.tracks.move( i, i+1 )
				scn.curve_to_frame.selected_track = i+1
			
		elif self.action == 'UP':
			# move selected track up
			if( i > 0 ):
				scn.curve_to_frame.tracks.move( i, i-1 )
				scn.curve_to_frame.selected_track = i-1
			
		elif self.action == 'REMOVE':
			# remove selected track
			scn.curve_to_frame.tracks.remove(i)
			
			length = len(scn.curve_to_frame.tracks)-1
			if i > length:
				scn.curve_to_frame.selected_track = length
			
		elif self.action == 'CHECK':
			# check if all tracks in the list are OK
			index = -1
			for key in scn.curve_to_frame.tracks.keys():
				index += 1
				
				# report and remove inexistant Track
				track = scn.curve_to_frame.tracks[key].get( True)
				if track is None:
					self.report({'ERROR'}, 'Error: \''+key+'\' movieclip didn\'t exist. the corresponding track have been removed.')
					scn.curve_to_frame.tracks.remove(index)
					index -= 1
					continue
				
				# report and remove Track which isn't SEQUENCE
				if track.source != 'SEQUENCE':
					self.report({'ERROR'}, 'Error: \''+key+'\' movieclip is not a sequence. the corresponding track have been removed.')
					scn.curve_to_frame.tracks.remove(index)
					index -= 1
					continue
				
				# initialize corresponding movieclip if necessary
				if track.curve_to_frame.uid == '':
					track.curve_to_frame.initialize()
				
				if get_fcurve_by_data_path(track, 'curve_to_frame.peaks_shape') is None:
					track.curve_to_frame.init_peaks_shape_curve()
				
				# check all image of the sequence exist
				if not track.curve_to_frame.check_image_file():
					self.report({'ERROR'}, 'Error: some images source file of \''+key+'\' movieclip are missing.')
		
		# update track id
		index = -1
		for key in scn.curve_to_frame.tracks.keys():
			index +=1
			scn.curve_to_frame.tracks[index].track_id = index
		
		return {"FINISHED"}





class TracksList():
	'''Tracks list properties and method'''
	
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
		new.start = 1
		new.end = track.curve_to_frame.size
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





