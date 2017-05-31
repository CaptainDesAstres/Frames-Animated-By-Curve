import bpy



class Track(bpy.types.PropertyGroup):
	''' managing curve to frame track Identification'''
	name = bpy.props.StringProperty()
	uid = bpy.props.StringProperty()
	track_id = bpy.props.IntProperty()
	
	def get( self, scene, rename = False):
		'''return the movie clip corresponding to this track'''
		try:
			track = bpy.data.movieclips[ self.name ]
			if track.curve_to_frame.uid == self.uid:
				return track
		except KeyError:
			pass
		
		for track in bpy.data.movieclips:
			if track.curve_to_frame.uid == self.uid:
				
				if rename:
					try:
						self.name = track.name
					except AttributeError:
						print('Track renaming error on '+self.name)
				
				return track
		
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
		col = layout.column()
		col.label(item.name, icon='CLIP')
		col = layout.column()
		col.label( 'id:'+str(item.track_id) )





class TracksActions(bpy.types.Operator):
	'''Tacks list action operator'''
	bl_idname = "curve_to_frame.tracks_list_action"
	bl_label = "Track Action"
	bl_description = "Track Action:\n- Move up selected track.\n- Check all Tracks.\n- Delete selected track.\n- Move down selected track."
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
			
			if i > len(scn.curve_to_frame.tracks)-1:
				scn.curve_to_frame.selected_track = len(scn.curve_to_frame.tracks)-1
			
		elif self.action == 'CHECK':
			# check if all tracks in the list are OK
			index = -1
			for key in scn.curve_to_frame.tracks.keys():
				index += 1
				
				# check the corresponding movieclip exist
				track = scn.curve_to_frame.tracks[index].get(scn, True)
				if track is None:
					self.report({'ERROR'}, 'Error: \''+key+'\' movieclip didn\'t exist. the corresponding track have been removed.')
					scn.curve_to_frame.tracks.remove(index)
					continue
				
				# check the corresponding movieclip is a SEQUENCE
				if track.source != 'SEQUENCE':
					self.report({'ERROR'}, 'Error: \''+key+'\' movieclip is not a sequence. the corresponding track have been removed.')
					scn.curve_to_frame.tracks.remove(index)
					continue
				
				# initialize corresponding movieclip if necessary
				if track.curve_to_frame.uid == '':
					track.curve_to_frame.initialize()
				
				if get_fcurve_by_data_path(track, 'curve_to_frame.peaks_shape') is None:
					track.curve_to_frame.init_peaks_shape_curve()
				
				# check all image of the sequence exist
				if not track.curve_to_frame.check_image_file():
					self.report({'ERROR'}, 'Error: some images source file of \''+key+'\' movieclip are massing.')
		
		# update track id
		index = -1
		for key in scn.curve_to_frame.tracks.keys():
			index +=1
			scn.curve_to_frame.tracks[index].track_id = index
		
		return {"FINISHED"}

