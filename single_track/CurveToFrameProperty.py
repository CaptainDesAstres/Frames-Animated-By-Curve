from functions import *
import bpy, os, shutil, platform
from math import ceil, floor
from uuid import uuid4




class CurveToFrameProperty():
	'''class containing all the property usefull for track settings'''
	
	def update_curves( self, context ):
		'''method that must be over ride: update curve when settings have been changed'''
	
	
	
	
	
	def check_driver( self ):
		'''check the object have no driver on property used by the addon'''
		if(		self.id_data.animation_data is None
				or self.id_data.animation_data.drivers is None):
			return False
		
		for driver in self.id_data.animation_data.drivers:
			if( driver.data_path.startswith('curve_to_frame.') ):
				return True
		
		return False
	
	
	
	
	
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
	
	
	
	
	
	def set_mini(self, context):
		'''check that maxi value are greater than maxi value 
				when editing mini value'''
		if self.mini > self.maxi:
			self['maxi'] = self.mini
	
	
	
	
	
	def set_maxi(self, context):
		'''check that maxi value are greater than maxi value
				when editing maxi value'''
		if self.mini > self.maxi:
			self['mini'] = self.maxi
	
	
	
	
	
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
	
	
	
	
	
	def init_peaks_shape_curve( self ):
		'''restore object default peaks shape curve'''
		ob = self.id_data
		
		# erase previous curve
		curve = get_fcurve_by_data_path( ob, 'curve_to_frame.peaks_shape' )
		if curve is not None:
			ob.animation_data.action.fcurves.remove(curve)
		
		# initialize peaks shape curve and settings
		if ob.animation_data is None:
			ob.animation_data_create()
		
		if ob.animation_data.action is None:
			ob.animation_data.action = bpy.data.actions.new( 
						name= ob.name+'Action')
		
		ob.animation_data.action.fcurves.new( 'curve_to_frame.peaks_shape' )
		curve = get_fcurve_by_data_path( ob, 'curve_to_frame.peaks_shape' )
		
		# set default profile
		curve.keyframe_points.insert( 0 , 0 )
		curve.keyframe_points[-1].interpolation = 'LINEAR'
		curve.keyframe_points.insert( 1 , 1 )
		curve.keyframe_points[-1].interpolation = 'LINEAR'
		curve.keyframe_points.insert( 2 , 0 )
		curve.keyframe_points[-1].interpolation = 'LINEAR'
		
		# erase range start/end curve
		curve = get_fcurve_by_data_path( ob, 'curve_to_frame.peaks_shape_range_start' )
		if curve is not None:
			ob.animation_data.action.fcurves.remove(curve)
		self.peaks_shape_range_start = 0
		
		curve = get_fcurve_by_data_path( ob, 'curve_to_frame.peaks_shape_range_end' )
		if curve is not None:
			ob.animation_data.action.fcurves.remove(curve)
		self.peaks_shape_range_end = 2
	
	
	
	
	
	def check_and_get_peaks_shapes( self ):
		'''get all peaks shape and check them'''
		# get shape curve
		shape_curve = get_fcurve_by_data_path( self.id_data, 
				'curve_to_frame.peaks_shape' )
		if shape_curve is None:
			self.init_peaks_shape_curve()
			shape_curve = get_fcurve_by_data_path( self.id_data, 'curve_to_frame.peaks_shape' )
		
		# get shape range start settings/curve
		start = self.peaks_shape_range_start
		start_curve = get_fcurve_by_data_path( self.id_data, 
				'curve_to_frame.peaks_shape_range_start' )
		
		# get shape range end settings/curve
		end = self.peaks_shape_range_end
		end_curve = get_fcurve_by_data_path( self.id_data, 
				'curve_to_frame.peaks_shape_range_end' )
		
		# get all keyframe time for start curve
		keys = [0]
		if start_curve is not None:
			for k in start_curve.keyframe_points:
				k.interpolation = 'CONSTANT'
				keys.append(k.co[0])
		# get all keyframe time for end curve
		if end_curve is not None:
			for k in end_curve.keyframe_points:
				k.interpolation = 'CONSTANT'
				keys.append(k.co[0])
		
		# avoid useless double and sort
		keys.sort()
		for k in list(keys):
			if keys.count(k) > 1:
				keys.remove(k)
		
		shapes = {}
		for fr in keys:
			# get end and start value at this frame
			if start_curve is not None:
				start = start_curve.evaluate(fr)
			if end_curve is not None:
				end = end_curve.evaluate(fr)
			
			# avoid end greater than start situation
			if end <= start:
				return 'Error at frame '+str(fr)+': \nPeaks shape range is set to start at frame '+str(start)+' and end at frame '+str(end)+': \nend frame MUST BE GREATER than start frame!'
			
			# do needed operation if it's a new range
			r = (start, end)
			if r not in shapes.keys():
				# add to range list
				keyframes = []
				length = end - start
				
				# get keyframe between this range
				for k in shape_curve.keyframe_points:
					fr = k.co[0]
					if fr >= start and fr <= end:
						keyframes.append(k)
				
				# check there is a keyframe corresponding to start/end frame
				if keyframes[0].co[0] != start:
					return 'Error at frame '+str(fr)+': \nPeaks Shape range is set to start at frame '+str(start)+' \nbut peaks shape curve have no keyframe at this position.'
				start = keyframes[0]
				
				if keyframes[-1].co[0] != end:
					return 'Error at frame '+str(fr)+': \nPeaks Shape range is set to end at frame '+str(end)+' \nbut peaks shape curve have no keyframe at this position.'
				end = keyframes[-1]
				
				# check if first and last keyframe have the same value
				if end.co[1] != start.co[1]:
					return 'Error at frame '+str(int(fr))+':\nPeaks Shape range is set to start at frame '+str(int(start.co[0]))+' and end at frame '+str(int(end.co[0]))+' \nbut corresponding peaks shape curve keyframe at those positions didn\'t have the same value \n(respectivly '+str(start.co[1])+' and '+str(end.co[1])+').'
				
				# copy keyframe and normalize settings
				KFInfoList = []
				prev = start.co[0]
				for k in keyframes:
					KF = {}
					# get frame
					KF['frame'] = (k.co[0]-prev) / length
					prev = k.co[0]
					
					# get value
					KF['value'] = k.co[1]
					
					# get interpolation
					KF['interpolation'] = k.interpolation
					
					# get easing
					KF['easing'] = k.easing
					
					# get left X and Y
					y = k.handle_left[1] - k.co[1]
					x = ( k.handle_left[0] - k.co[0] ) / length
					KF['left'] = ( x, y )
					
					# get right X and Y
					y = k.handle_right[1] - k.co[1]
					x = ( k.handle_right[0] - k.co[0] ) / length
					KF['right'] = ( x, y )
					
					KFInfoList.append(KF)
				
				# copy first keyframe into last keyframe
				last = KFInfoList[0].copy()
				last['frame'] = KFInfoList[-1]['frame']
				last['left'] = KFInfoList[-1]['left']
				KFInfoList[-1] = last
				
				shapes[r] = KFInfoList
		
		return shapes
	
	
	
	
	
	def get_frame_name(self, n):
		'''return the file name of a frame'''
		return	(	self.prefix +
					str(int(n)).rjust(self.number_size, '0')+
					self.suffix + self.ext	)
	
	
	
	
	
	def check_image_file( self ):
		'''check in all the movieclip sequence image exists'''
		for fr in range( self.first,
					self.last+1 ):
			if not os.path.exists( self.path + self.get_frame_name( fr ) ):
				return False
		return True
	
	
	
	
	
	def draw_clip_load_error(self, layout, clip):
		'''draw movieclip load error if required'''
		if(clip.source != 'SEQUENCE'):
			# Display an error message, requesting for a sequence of images
			row = layout.row()
			row.label( text="Current movie can't be use by addon.",
				 icon="ERROR"  )
			row = layout.row()
			row.label( text="Only images sequence are accept." )
			row = layout.row()
			row.template_ID(bpy.context.space_data, 'clip', open='clip.open' )
			
			return True
			
		elif(not self.init):
			# ask to initialize curve to frame on thes MovieClip
			row = layout.row()
			row.operator(
				"curve_to_frame.init_track",
				text="initialize MovieClip info")
			
			return True
			
		return False
	
	
	
	
	
	def draw_movieclip_settings(self, layout):
		'''draw Movie info & settings in the panel'''
		# Display the directory path
		row = layout.row()
		col = row.column()
		col.label( text = "Frame Directory path:" )
		col = row.column()
		col.operator(
			"curve_to_frame.init_track",
			icon = 'FILE_REFRESH',
			text = '')
		row = layout.row()
		row.label( text= self.path )
		
		# Display frame extension
		row = layout.row()
		col = row.column()
		col.label( text="File type: "+self.ext )
		
		# Display first to last accepted frame name range
		col = row.column()
		col.label( text="Valid frames: "\
			+self.get_frame_name(self.first)+' to '\
			+self.get_frame_name(self.last) )
		
		# Display Start/End settings
		layout.separator()
		row = layout.row()
		col = row.column()
		col.prop(self, "start")
		col = row.column()
		col.prop(self, "end")
	
	
	
	
	
	def draw_amplitude( 
						self,
						layout, 
						refresh_curve, 
						refresh_mini_maxi):
		'''draw amplitude settings into the panel'''
		# A float amplitude field
		layout.separator()
		row = layout.row()
		col = row.column()
		col.prop(self, "amplitude")
		
		# A field to remind F-Curve min and max value
		fCurve = get_fcurve_by_data_path(self.id_data, 'curve_to_frame.amplitude')
		if(fCurve is None):
			m = M = self.amplitude
		else:
			m, M = get_curve_limit(fCurve)
		m = round(m*1000)/1000
		M = round(M*1000)/1000
		col = row.column()
		col.label( text = "(Goes from "+str(m)\
					+" to "+str(M)+')' )
		
		# A field to set the min F-Curve Value to 
		# assigne to the first frames
		row = layout.row()
		col = row.column()
		col.prop(self, "mini")
		
		# A field to set the max F-Curve Value to 
		# assigne to the last frames
		col = row.column()
		col.prop(self, "maxi")
		if(self.combination_mode == 'ignore_amplitude'):
			col.enabled = False
		
		# A button to get curve min max value
		col = row.column()
		col.operator(refresh_mini_maxi,
					text = 'auto')
		# display net amplitude value
		col = row.column()
		col.enabled = False
		col.prop(self, "amplitude_net")
		col = row.column()
		col.operator(
			refresh_curve,
			text='',
			icon='FILE_REFRESH')
	
	
	
	
	
	def draw_peaks(self, layout, refresh_curve):
		'''draw peaks rythm settings into the panel'''
		# a button to activate and set peaks per minute
		layout.separator()
		row = layout.row()
		col = row.column()
		col.prop(self, "rate")
		col = row.column()
		col.prop(self, "rate_unit", text='')
		col = row.column()
		col.prop(self, "auto_constant")
		col = row.column()
		col.prop(self, "accuracy")
		
		row = layout.row()
		col = row.column()
		col.prop(self, "synchronized")
		col = row.column()
		if (not self.synchronized):
			col.enabled = False
		col.prop(self, "anticipate")
		col = row.column()
		col.enabled = False
		col.prop(self, "peaks")
		col = row.column()
		col.operator(
			refresh_curve,
			text='',
			icon='FILE_REFRESH')
	
	
	
	
	
	def draw_peaks_profile( self, layout, refresh_curve, restore_shape ):
		'''draw peaks profile settings'''
		layout.separator()
		row = layout.row()
		
		# restore default shape button
		col = row.column()
		col.operator(
			restore_shape,
			text='',
			icon='LOAD_FACTORY')
		
		# display peaks shapes settings
		col = row.column()
		col.prop(self, "peaks_shape")
		col = row.column()
		col.prop(self, "peaks_shape_range_start")
		col = row.column()
		col.prop(self, "peaks_shape_range_end")
		
		
		# refresh curve
		col = row.column()
		col.operator(
			refresh_curve,
			text='',
			icon='FILE_REFRESH')
	
	
	
	
	
	def draw_combination_and_output( 
						self, 
						layout, 
						refresh_curve, 
						no_output=False ):
		'''draw combination and output settings and value into the panel'''
		# combination mode field
		layout.separator()
		row = layout.row()
		row.prop(self, 'combination_mode')
		
		# visualize combination of peaks and amplitude curve
		row = layout.row()
		col = row.column()
		col.enabled = False
		col.prop(self, "combination")
		
		# visualize output frame
		if no_output:
			col = row.column()
			col.prop(self, "rounding")
		else:
			col = row.column()
			col.enabled = False
			col.prop(self, "output")
		
		# refresh curve
		col = row.column()
		col.operator(
			refresh_curve,
			text='',
			icon='FILE_REFRESH')
	
	
	
	
	
	def draw_single_track_output( self, layout, scene, clip ):
		'''draw rounding & output settings into the panel'''
		warning = False
		# A field to choose between Round Floor and 
		# Ceil rounding method
		layout.separator()
		row = layout.row()
		col = row.column()
		col.prop(self, "rounding")
		
		# A checkbox to get real frame file copy
		col = row.column()
		
		if(not scene.ctf_real_copy \
				and platform.system().lower() not in ['linux', 'unix']):
			col.prop( scene, "ctf_real_copy", icon='ERROR' )
			warning = True
			
		else:
			col.prop( scene, "ctf_real_copy" )
		
		# A field to set the output path
		row = layout.row()
		col = row.column()
		col.prop(self, "output_path")
		path = bpy.path.abspath(self.output_path )
		
		
		return warning
	
	
	
	
	
	def draw_multi_track_output( self, layout, scene ):
		'''draw rounding & output settings into the panel'''
		warning = False
		# A field to set the output path
		row = layout.row()
		col = row.column()
		col.prop(self, "output_path")
		
		# A checkbox to get real frame file copy
		col = row.column()
		if(not scene.ctf_real_copy \
				and platform.system().lower() not in ['linux', 'unix']):
			col.prop( scene, "ctf_real_copy", icon='ERROR' )
			warning = True
		else:
			col.prop( scene, "ctf_real_copy" )
		
		return warning
	
	
	
	
	
	def draw_run_button( self, layout, warning ):
		'''check situation and draw run button into panel'''
		if( self.check_driver() ):
			# check no driver is use on curve to frame property
			row = layout.row()
			row.label(text='This function can\'t be used with driver!', 
						icon='ERROR')
		elif(warning):
			# check there is no warning
			row = layout.row()
			row.operator(
				"curve_to_frame.render_single_track",
				text="ignore warning and run at my one risk",
				icon = 'ERROR')
		else:
			# draw standart run button
			row = layout.row()
			row.operator(
				"curve_to_frame.render_single_track",
				text="run")
	
	
	
	
	
	def panel_single_track(self, context, layout, clip):
		'''draw the curve to frame panel'''
		# draw movieclip load error if required
		error = self.draw_clip_load_error( layout, clip )
		refresh_curve = "curve_to_frame.generate_single_track_curves"
		refresh_mini_maxi = "curve_to_frame.single_track_get_amplitude_range"
		restore_peak_shape = "curve_to_frame.single_track_default_peak_shape"
		
		if not error:
			# draw Movie info & settings
			self.draw_movieclip_settings( layout )
			
			# draw amplitude settings
			self.draw_amplitude( layout, 
								refresh_curve, refresh_mini_maxi )
			
			# draw peaks rythm settings
			self.draw_peaks(layout, refresh_curve )
			
			# draw peaks profile settings
			self.draw_peaks_profile( layout, refresh_curve,
						restore_peak_shape )
			
			# draw combination node settings and combination and output value
			self.draw_combination_and_output( layout, refresh_curve )
			
			# draw output and rounding settings
			warning = self.draw_single_track_output( layout, context.scene, clip )
			
			# draw run button or error message
			self.draw_run_button( layout, warning )
	
	
	
	
	
	def update_net_amplitude_curve( self, clip, context ):
		'''update clip amplitude net curve'''
		# determine frame working space and frame step
		frame = start = floor(context.scene.frame_start - 5)
		end = ceil(context.scene.frame_end + 5)
		
		# get and erase amplitude_net fcurve
		amplitude_net_curve = get_fcurve_by_data_path(clip, 
										'curve_to_frame.amplitude_net')
		if amplitude_net_curve is not None:
			hide = amplitude_net_curve.hide
			clip.animation_data.action.fcurves.remove(amplitude_net_curve)
		else:
			hide = True
		clip.animation_data.action.fcurves.new('curve_to_frame.amplitude_net')
		amplitude_net_curve = get_fcurve_by_data_path(clip,
										'curve_to_frame.amplitude_net')
		
		# get amplitude fcurve
		raw_curve = get_fcurve_by_data_path(clip, 'curve_to_frame.amplitude')
		raw_value = clip.curve_to_frame.amplitude
		
		# get mini and maxi fcurve
		mini_curve = get_fcurve_by_data_path(clip, 'curve_to_frame.mini')
		mini_value = clip.curve_to_frame.mini
		maxi_curve = get_fcurve_by_data_path(clip, 'curve_to_frame.maxi')
		maxi_value = clip.curve_to_frame.maxi
		
		# generate amplitude_net curve
		while( frame <= end ):
			# get mini value at this frame
			if mini_curve is not None:
				mini_value = mini_curve.evaluate(frame)
			
			# get maxi value at thes frame
			if maxi_curve is not None:
				maxi_value = max ( maxi_curve.evaluate(frame), mini_value )
			
			# get amplitude raw value
			if raw_curve is not None:
				raw_value = raw_curve.evaluate(frame)
			
			#compute net value
			if raw_value >= maxi_value:
				net_amplitude_value = 1
			elif raw_value <= mini_value:
				net_amplitude_value = 0
			else:
				net_amplitude_value = ( raw_value - mini_value )\
										/( maxi_value - mini_value )
			
			# create keyframe
			amplitude_net_curve.keyframe_points.insert(frame,
								net_amplitude_value)
			
			frame += 1
		
		#erase keyframe on flat section
		avoid_useless_keyframe( amplitude_net_curve )
		
		# prevent curve edition
		amplitude_net_curve.lock = True
		amplitude_net_curve.hide = hide
		
		return amplitude_net_curve
	
	
	
	
	
	def update_peaks_curve(self, 
					clip, 
					context, 
					amplitude_net_curve, 
					shapes ):
		'''update clip peaks curve'''
		# remove old peaks
		peaks_curve = get_fcurve_by_data_path(clip, 'curve_to_frame.peaks')
		if peaks_curve is not None:
			hide = peaks_curve.hide
			clip.animation_data.action.fcurves.remove(peaks_curve)
		else:
			hide = True
		
		# create new peaks
		clip.animation_data.action.fcurves.new('curve_to_frame.peaks')
		peaks_curve = get_fcurve_by_data_path(clip, 'curve_to_frame.peaks')
		
		# get rate curve and default value
		rate_curve = get_fcurve_by_data_path(clip, 'curve_to_frame.rate')
		rate_value = clip.curve_to_frame.rate
		
		# convert rate_curve to constant interpolation
		if clip.curve_to_frame.auto_constant and rate_curve is not None:
			for k in rate_curve.keyframe_points:
				k.interpolation = 'CONSTANT'
		
		# get scene start/end frame
		start = context.scene.frame_start
		end = context.scene.frame_end
		
		
		if rate_curve is None and rate_value <= 0:
			if rate_value == 0:
				# 0 valued flat peaks curve
				peaks_curve.keyframe_points.insert(0, 0)
			else:
				# 1 valued flat peaks curve
				peaks_curve.keyframe_points.insert(0, 1)
		else:
			# rate_curve is animated
			if clip.curve_to_frame.synchronized:
				curve_to_frame.generate_sync_peaks_curve( context, clip,
						peaks_curve, shapes, rate_curve, amplitude_net_curve,
						start, end
						)
			else:
				curve_to_frame.generate_peaks_curve_segment( context, clip,
						peaks_curve, shapes, rate_curve, start, end
						)
		
		# prevent curve edition
		peaks_curve.lock = True
		peaks_curve.hide = hide
		
		return peaks_curve
	
	
	
	
	
	def generate_sync_peaks_curve(
				context,
				clip,
				peaks_curve,
				shapes,
				rate_curve,
				amplitude_net_curve,
				start,
				end
				):
		'''generate the peaks curve when synchronized with amplitude'''
		# get first segment starting frame
		seg_start = start
		amplitude = amplitude_net_curve.evaluate(seg_start)
		if amplitude == 0:
			anticipate = True
		else:
			anticipate = False
		
		
		while( seg_start < end ):
			amplitude = amplitude_net_curve.evaluate(seg_start)
			if amplitude == 0:
				k = peaks_curve.keyframe_points.insert( seg_start, 0 )
				k.interpolation = 'CONSTANT'
				while amplitude == 0 and seg_start <= end:
					seg_start += clip.curve_to_frame.accuracy
					amplitude = amplitude_net_curve.evaluate(seg_start)
			
			seg_end = seg_start
			while amplitude != 0 and seg_end <= end:
				seg_end += clip.curve_to_frame.accuracy
				amplitude = amplitude_net_curve.evaluate(seg_end)
			
			seg_start = curve_to_frame.generate_peaks_curve_segment( 
							context, clip, peaks_curve, shapes, rate_curve,
							seg_start, seg_end, anticipate )
			anticipate = True
	
	
	
	
	
	def generate_peaks_curve_segment(
						context,
						clip,
						peaks_curve,
						shapes,
						rate_curve,
						start,
						end,
						anticipate = False
						):
		'''generate a segment of peaks curve'''
		# get frame rate and start/end frame
		fps = context.scene.render.fps
		
		# get peaks shape range start/end curve
		shape_start_curve =  get_fcurve_by_data_path( clip, 
				'curve_to_frame.peaks_shape_range_start' )
		shape_end_curve = get_fcurve_by_data_path( clip, 
				'curve_to_frame.peaks_shape_range_end' )
		
		# get default rate
		rate = clip.curve_to_frame.rate
		if rate_curve is not None:
			rate = rate_curve.evaluate( start )
		
		# get real starting frame
		frame = start
		if rate <= 0:
			anticipate = False
			frame, current_shape, shape_KF, rate =\
						curve_to_frame.generate_no_peaks_segment( clip, rate_curve,
								peaks_curve, shape_start_curve, shape_end_curve,
								shapes, frame, end )
			if frame >= end:
				return frame
		
		# convert rate if in ppm
		if clip.curve_to_frame.rate_unit == 'ppm':
			rate = fps * 60 / rate
		
		# get peaks shape start range
		if shape_start_curve is None:
			shape_start = clip.curve_to_frame.peaks_shape_range_start
		else:
			shape_start = shape_start_curve.evaluate( start )
		
		# get peaks shape end range
		if shape_end_curve is None:
			shape_end = clip.curve_to_frame.peaks_shape_range_end
		else:
			shape_end = shape_end_curve.evaluate( start )
		
		# initial range and key frame
		current_shape = ( shape_start, shape_end )
		shape_key = 0
		
		# generate anticipated keyframe
		if anticipate:
			frame, shape_key = curve_to_frame.generate_anticipated_peaks(
							clip, shapes[current_shape],
							frame, rate, peaks_curve
							)
		
		# get shape keyframe
		shape_KF = shapes[current_shape][shape_key]
		
		# generate the segment
		while( True ):
			# insert keyframe
			keyframe = peaks_curve.keyframe_points.insert( frame,
					shape_KF['value'] )
			
			# set left handle of keyframe
			keyframe.handle_left_type = 'FREE'
			keyframe.handle_left[0] = keyframe.co[0] \
																+ shape_KF['left'][0] * rate
			keyframe.handle_left[1] = keyframe.co[1] \
																+ shape_KF['left'][1]
			
			if frame >= end :
				return frame + 0.01
			
			# get rate value
			if rate_curve is not None:
				rate = rate_curve.evaluate( frame )
				if rate > 0 and clip.curve_to_frame.rate_unit == 'ppm':
					rate = fps * 60 / rate
			
			# peaks end instructions
			shape_key += 1
			if shape_key == len(shapes[current_shape]):
				shape_key = 1
				# get new range
				if shape_start_curve is not None:
					shape_start = shape_start_curve.evaluate( frame )
				if shape_end_curve is not None:
					shape_end = shape_end_curve.evaluate( frame )
				current_shape = ( shape_start, shape_end )
				shape_KF = shapes[current_shape][0]
				
				# add a keyframe if new peaks keyframe value different 
				#    from the last of the previous peaks
				if( shape_KF['value'] != keyframe.co[1] ):
					frame += 0.01
					keyframe.interpolation = 'LINEAR'
					
					keyframe = peaks_curve.keyframe_points.insert(
							frame, shape_KF['value'] )
			
			# set right handle of keyframe
			keyframe.handle_right_type = 'FREE'
			keyframe.handle_right[0] = keyframe.co[0] \
																+ shape_KF['right'][0] * rate
			keyframe.handle_right[1] = keyframe.co[1] \
																+ shape_KF['right'][1]
			
			# set right interpolation and easing
			keyframe.interpolation = shape_KF['interpolation']
			keyframe.easing = shape_KF['easing']
			
			if rate <= 0:
				frame, current_shape, shape_KF, rate =\
							curve_to_frame.generate_no_peaks_segment( clip, rate_curve,
									peaks_curve, shape_start_curve, shape_end_curve,
									shapes, frame, end )
				if frame >= end:
					return frame
			else:
				# get next shape keyframe
				shape_KF = shapes[current_shape][shape_key]
				frame += shape_KF['frame'] * rate
		return frame
	
	
	
	
	
	def generate_anticipated_peaks(
				clip,
				shape,
				start,
				rate,
				peaks_curve
				):
		'''generate anticipated peaks keyframe'''
		# get anticipate settings
		anticipate_curve = get_fcurve_by_data_path( clip, 
				'curve_to_frame.anticipate' )
		if anticipate_curve is None:
			anticipate = clip.curve_to_frame.anticipate
		else:
			anticipate = anticipate_curve.evaluate(start)
		
		# init frame and shape key
		shape_key = 0
		frame = start
		frame -= anticipate * rate
		
		# don't start peaks before last peaks_curve keyframe
		frame = max(frame, peaks_curve.keyframe_points[-1].co[0] + 0.01 )
		
		KF = shape[shape_key]
		l = len(shape)-1
		while(shape_key < l):
			# insert anticipated keyframe
			keyframe = peaks_curve.keyframe_points.insert( frame, KF['value'])
			
			# set handle and interpolation settings
			keyframe.handle_left_type = 'FREE'
			keyframe.handle_left[0] = keyframe.co[0] \
																+ KF['left'][0] * rate
			keyframe.handle_left[1] = keyframe.co[1] \
																+ KF['left'][1]
			
			keyframe.handle_right_type = 'FREE'
			keyframe.handle_right[0] = keyframe.co[0] \
																+ KF['right'][0] * rate
			keyframe.handle_right[1] = keyframe.co[1] \
																+ KF['right'][1]
			
			keyframe.interpolation = KF['interpolation']
			keyframe.easing = KF['easing']
			
			# next keyframe
			shape_key += 1
			KF = shape[shape_key]
			frame += KF['frame'] * rate
		
		return frame, shape_key
	
	
	
	
	
	def generate_no_peaks_segment( clip,
					rate_curve,
					peaks_curve,
					shape_start_curve,
					shape_end_curve,
					shapes,
					frame,
					end ):
		'''generate flat peaks curve segment when rate <= 0'''
		rate = rate_curve.evaluate( frame )
		while rate <= 0:
			frame += clip.curve_to_frame.accuracy
			
			if rate == 0:
				keyframe = peaks_curve.keyframe_points.insert( frame, 0 )
				test = True
			else:
				keyframe = peaks_curve.keyframe_points.insert( frame, 1 )
				test = False
			
			keyframe.interpolation = 'CONSTANT'
			
			rate = rate_curve.evaluate( frame )
			while( rate <= 0 and ((rate == 0) == test) and frame <= end ):
				frame += clip.curve_to_frame.accuracy
				rate = rate_curve.evaluate( frame )
			
			if rate > 0 and clip.curve_to_frame.rate_unit == 'ppm':
				rate = fps * 60 / rate
			
			# start a new peaks
			shape_key = 0
			
			# get new range
			if shape_start_curve is not None:
				shape_start = shape_start_curve.evaluate( frame )
			if shape_end_curve is not None:
				shape_end = shape_end_curve.evaluate( frame )
			current_shape = ( shape_start, shape_end )
			
			shape_KF = shapes[current_shape][shape_key]
			
			return frame, current_shape, shape_KF, rate
	
	
	
	
	
	def update_combination_curve(
						self,
						clip, 
						context, 
						amplitude_net_curve,
						peaks_curve):
		'''update clip combination curve'''
		# get combination mode curve
		combination_enum = clip.curve_to_frame.bl_rna.\
													properties['combination_mode'].enum_items
		combination_mode = combination_enum.find( clip.curve_to_frame.combination_mode )
		combination_mode_curve = get_fcurve_by_data_path(clip, 
								'curve_to_frame.combination_mode')
		
		# get and initialize combination curve
		combination_curve = get_fcurve_by_data_path(clip, 
								'curve_to_frame.combination')
		if combination_curve is not None:
			hide = combination_curve.hide
			clip.animation_data.action.fcurves.remove(combination_curve)
		else:
			hide = True
		clip.animation_data.action.fcurves.new(
									'curve_to_frame.combination')
		combination_curve = get_fcurve_by_data_path(clip, 
									'curve_to_frame.combination')
		
		# get rate curve
		rate_curve = get_fcurve_by_data_path(clip, 'curve_to_frame.rate')
		
		# loop only on peak curve keyframe
		for keyframe in peaks_curve.keyframe_points:
			# get peaks keyframe value and frame
			frame = keyframe.co[0]
			value = max( min(1, keyframe.co[1]), 0 )
			
			# get combination_mode at this frame
			if combination_mode_curve is not None:
				combination_mode = combination_mode_curve.evaluate(frame)
			
			# generate keyframe
			if combination_mode != 3 : # «combination mode == multiply or clamp
				value = value * amplitude_net_curve.evaluate(frame)
			
			if combination_mode != 4 :
				combination_curve.keyframe_points.insert(frame, value)
				combination_curve.keyframe_points[-1].interpolation = 'LINEAR'
		
		
		# loop for all frame
		end = max(	peaks_curve.keyframe_points[-1].co[0], 
					context.scene.frame_end )
		frame = start = context.scene.frame_start
		while frame <= end:
			# get combination_mode at this frame
			if combination_mode_curve is not None:
				combination_mode = combination_mode_curve.evaluate(frame)
			
			if combination_mode == 0 : # combination mode is «multiply»
				value = max( min( 1, peaks_curve.evaluate(frame) ), 0 )\
						* amplitude_net_curve.evaluate(frame)
				combination_curve.keyframe_points.insert(frame, value)
			elif combination_mode == 2: # combination mode is «clamp_curve»
				combination_curve.keyframe_points.insert(
						frame,
						max(
							min (
									amplitude_net_curve.evaluate(frame),
									peaks_curve.evaluate(frame),
									1
									),
							0
						)
					)
			elif combination_mode == 4: 
				# combination mode is «ignore peaks»
				combination_curve.keyframe_points.insert(
							frame,
							amplitude_net_curve.evaluate(frame)
							)
			
			combination_curve.keyframe_points[-1].interpolation = 'LINEAR'
			
			# next frame
			frame += 1
		
		#erase keyframe on flat section
		avoid_useless_keyframe( combination_curve )
		
		# prevent curve edition
		combination_curve.lock = True
		combination_curve.hide = hide
		
		return combination_curve
	
	
	
	
	
	def update_output_curve(self, clip, context, combination_curve):
		'''update output curve'''
		# get and initialize output curve
		output_curve = get_fcurve_by_data_path(clip, 'curve_to_frame.output')
		if output_curve is not None:
			hide = output_curve.hide
			clip.animation_data.action.fcurves.remove(output_curve)
		else:
			hide = True
		clip.animation_data.action.fcurves.new('curve_to_frame.output')
		output_curve = get_fcurve_by_data_path(clip, 'curve_to_frame.output')
		
		# get start and end curve
		start_curve = get_fcurve_by_data_path(clip, 'curve_to_frame.start')
		end_curve = get_fcurve_by_data_path(clip, 'curve_to_frame.end')
		
		# generate first keyframe
		start = context.scene.frame_start
		output_curve.keyframe_points.insert( start - 1, 0 )
		output_curve.keyframe_points[-1].interpolation = 'LINEAR'
		
		# get rounding method
		if(clip.curve_to_frame.rounding == 'round'):
			rounding = round
		elif(clip.curve_to_frame.rounding == 'floor'):
			rounding = floor
		else:
			rounding = ceil
		
		# generate a keyframe at each frame
		frame = start
		end = context.scene.frame_end
		while frame <= end:
			# get start value at this frame
			if start_curve is not None:
				start_value = start_curve.evaluate(frame)
			else:
				start_value = clip.curve_to_frame.start
			
			# check start_value
			if start_value < 1 :
				start_value = 1
			elif start_value > clip.curve_to_frame.size:
				start_value = clip.curve_to_frame.size
			
			# get end value at this frame
			if end_curve is not None:
				end_value = end_curve.evaluate(frame)
			else:
				end_value = clip.curve_to_frame.end
			
			# check end_value
			if end_value < start_value :
				end_value = start_value
			elif end_value > clip.curve_to_frame.size:
				end_value = clip.curve_to_frame.size
			
			# generate keyframe
			output_frame = rounding(
					clip.curve_to_frame.first + start_value - 1 
					+ combination_curve.evaluate(frame)
					* (end_value - start_value)
					)
			output_curve.keyframe_points.insert( frame, output_frame )
			
			# next frame
			frame += 1
		
		# generate last keyframe
		output_curve.keyframe_points.insert( frame , 0 )
		output_curve.keyframe_points[-1].interpolation = 'LINEAR'
		
		#erase keyframe on flat section
		avoid_useless_keyframe( output_curve )
		
		# prevent curve edition
		output_curve.lock = True
		output_curve.hide = hide
	
	
	
	
	
	def panel_multi_track_amplitude_and_peaks(self, context, layout):
		'''draw the curve to frame panel'''
		
		refresh_curve = "curve_to_frame.generate_multi_track_curves"
		refresh_mini_maxi = "curve_to_frame.multi_track_get_amplitude_range"
		restore_peak_shape = "curve_to_frame.multi_track_default_peak_shape"
		
		# draw amplitude settings
		self.draw_amplitude( layout,
							refresh_curve, refresh_mini_maxi )
		
		# draw peaks rythm settings
		self.draw_peaks(layout, refresh_curve )
		
		# draw peaks profile settings
		self.draw_peaks_profile( layout, refresh_curve,
					restore_peak_shape )
		
		# draw combination node settings and combination and output value
		self.draw_combination_and_output( layout, refresh_curve, True )
	
	
	
	
	
	def panel_tracks( self, layout, context ):
		'''draw the tracks panel content'''
		# track adding field
		row = layout.row()
		col = row.column()
		col.prop_search(self, "track_add", bpy.data, "movieclips")
		col = row.column()
		col.operator(
				"clip.open", text='', icon='FILESEL')
		
		# error message if unvalid track
		if self.track_add != '':
			row = layout.row()
			if self.track_add not in bpy.data.movieclips.keys():
				row.label( '  Error: movieclip not found', icon = 'ERROR' )
			else:
				row.label( '  Unvalid choice : only image sequence can be used.',
								icon = 'ERROR' )
		
		# display Tracks list
		row = layout.row()
		col = row.column()
		col.template_list(
				"TrackItem",
				"",
				self,
				"tracks",
				self,
				"selected_track",
				rows=5)
		
		# track list action button
		col = row.column( align=True )
		col.operator("curve_to_frame.tracks_list_action", icon='TRIA_UP', text="").action = 'UP'
		col.operator("curve_to_frame.tracks_list_action", icon='FILE_TICK', text="").action = 'CHECK'
		col.operator("curve_to_frame.tracks_list_action", icon='X', text="").action = 'REMOVE'
		col.operator("curve_to_frame.tracks_list_action", icon='TRIA_DOWN', text="").action = 'DOWN'
		
		# display selected track settings
		if (self.selected_track >= 0 
				and self.selected_track < len(self.tracks) ):
			track = self.tracks[self.selected_track].get(context.scene).curve_to_frame
			
			# Display selected track directory path
			layout.separator()
			row = layout.row()
			row.label( text = "Frame Directory path:" )
			row = layout.row()
			row.label( text= track.path )
			
			# Display selected track source file extension
			row = layout.row()
			col = row.column()
			col.label( text="File type: "+track.ext )
			
			# Display first to last accepted frame name range
			col = row.column()
			col.label( text="Valid frames: "\
				+track.get_frame_name(track.first)+' to '\
				+track.get_frame_name(track.last) )
			
			# Display Start/End settings
			layout.separator()
			row = layout.row()
			col = row.column()
			col.prop(track, "start")
			col = row.column()
			col.prop(track, "end")
	
	
	
	
	
	
	
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
	
	#################################################
	##     amplitude settings                      ##
	#################################################
	# amplitude property
	amplitude = bpy.props.FloatProperty(
		name = 'amplitude (raw)',
		description = 'Determined the frame of the Movie \
								clip to use at each frame',
		default = 0.0
		)
	
	# amplitude after applying min and max value
	amplitude_net = bpy.props.FloatProperty(
		name = 'amplitude (net)',
		description = 'show the apply of mini and maxi to \
							amplitude raw. Can\'t be edit.',
		)
	
	# method used to combine amplitude and peaks curve
	combination_mode = bpy.props.EnumProperty(
		name = 'combination mode',
		description = 'the way to combine amplitude and peaks curve',
		default = 'ignore_peaks',
		items = [
#			(identifier,			name,
#				description, number)
			
			('multiply',		'Peaks Curve Multiplied by amplitude',
				'peaks is multiplied by \
				amplitude percentage of maxi',				0),
			
			('clamp_key',		'Peaks Keyframe Clamped to amplitude',
				'peaks keyframe is clamped by amplitude',		1),
			
			('clamp_curve',		'Peaks Curve Clamped to amplitude',
				'all peaks value is clamped by amplitude',		2),
			
			('ignore_amplitude',			'Only use peaks curve',
				'Only use peaks curve',			3),
			
			('ignore_peaks',			'Only use amplitude curve',
				'Only use amplitude curve',			4)
			
			],
		update = update_curves
		)
	
	# min value associated to the first frames
	mini = bpy.props.FloatProperty(
		name = 'Mini',
		description = 'the minimal value of the \
						amplitude curve, all smaller\
						 value will display the first frame',
		default = 0.0,
		update = set_mini
		)
	
	# max value associated to the last frames
	maxi = bpy.props.FloatProperty(
		name = 'Maxi',
		description = 'the maximal value of the amplitude\
						 curve. All bigger value will display \
						the last frame. This property is useless \
						when amplitude is ignored.',
		default = 1.0,
		update = set_maxi
		)
	
	
	
	
	
	#################################################
	##     output settings                         ##
	#################################################
	# combination of net amplitude and peaks curves
	combination = bpy.props.FloatProperty(
		name = "combination",
		description = "Only to visualize the combination of \
					peaks and amplitude curve curve. Can't \
					be edit manually: use rate and amplitude settings.",
		default = 0,
		min = 0,
		max = 1)
	
	# output frame curve
	output = bpy.props.IntProperty(
		name = "output frame",
		description = "Only to visualize the output frames. \
						Can't be edit manually.")
	
	# Rounding method
	rounding = bpy.props.EnumProperty(
		name = 'Rounding method',
		description = 'the rounding method use by the \
						script to round the float computed \
						value into a integer value corresponding \
						to a frame',
		options = {'LIBRARY_EDITABLE'},
		default = 'round',
		items = [
			#(identifier,	name, 		description )
			('round',		'round',	'the closest integer.'),
			('ceil',		'ceil',		'the closest greater integer'),
			('floor',		'floor',		'the closest smaller integer')
			]
		)
	
	# output path
	output_path = bpy.props.StringProperty(
		name = "output",
		description = "Output directory path.",
		default = '//',
		subtype = 'DIR_PATH')
	
	
