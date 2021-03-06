from functions import *
import bpy, os, shutil


class AmplitudeMinMax(bpy.types.Operator):
	'''operator to initialize or refresh curve to frame info of a movie clip'''
	bl_idname = "curve_to_frame.single_track_get_amplitude_range"
	bl_label= "get movieclip amplitude curve mini and maxi value"
	bl_options = {'INTERNAL'}
	
	def execute(self, context):
		'''get movieclip amplitude curve mini and maxi value'''
		clip = context.space_data.clip
		
		fCurve = get_fcurve_by_data_path(clip, 'curve_to_frame.amplitude')
		if(fCurve is None):
			m = M = clip.curve_to_frame.amplitude
		else:
			clip.curve_to_frame.mini, clip.curve_to_frame.maxi = get_curve_limit(fCurve)
		
		# update curves
		status = clip.curve_to_frame.update_curves( context )
		if status is True:
			return {'FINISHED'}
		else:
			self.report( {'ERROR'}, status )
			return {'CANCELLED'}






class RestoreDefaultPeakShape(bpy.types.Operator):
	'''Restore default peak shape settings'''
	bl_idname = "curve_to_frame.single_track_default_peak_shape"
	bl_label= "restore default peak shape settings"
	bl_options = {'INTERNAL'}
	
	def execute(self, context):
		'''restore default peak shape settings'''
		context.space_data.clip.curve_to_frame.init_peaks_shape_curve()
		return {'FINISHED'}





class InitTrack(bpy.types.Operator):
	'''operator to initialize or refresh curve to frame info of a movie clip'''
	bl_idname = "curve_to_frame.init_track"
	bl_label= "refresh MovieClip curve to frame Attribute"
	bl_options = {'INTERNAL'}
	
	def execute(self, context):
		'''refresh curve to frame info of a movie clip'''
		bpy.ops.clip.reload()# reload source file
		clip = context.space_data.clip
		if clip is None:
			self.report({'ERROR'}, 'can\'t find the selected movieclip.')
			return {'CANCELLED'}
		else:
			if get_fcurve_by_data_path(clip, 'curve_to_frame.peaks_shape') is None:
					clip.curve_to_frame.init_peaks_shape_curve()
			return clip.curve_to_frame.initialize()





class CurvesRefresh(bpy.types.Operator):
	'''operator to initialize or refresh curve to frame info of a movie clip'''
	bl_idname = "curve_to_frame.generate_single_track_curves"
	bl_label= "refresh movieclip curves"
	bl_options = {'INTERNAL'}
	
	def execute(self, context):
		'''refresh clip curves'''
		status = context.space_data.clip.curve_to_frame.update_curves( context )
		if status is True:
			return {'FINISHED'}
		else:
			self.report( {'ERROR'}, status )
			return {'CANCELLED'}





class CurveToFrame(bpy.types.Operator):
	'''the operator to render single track curve to frame animation'''
	bl_idname = "curve_to_frame.render_single_track"
	bl_label= "Animate Single Track By Curves"
	bl_options = {'INTERNAL'}
	
	def execute(self, context):
		bpy.ops.clip.reload()# reload source file
		# get clip
		clip = context.space_data.clip
		if clip is None:
			self.report({'ERROR'}, 'can\'t find the selected movieclip.')
			return {'CANCELLED'}
		else:
			clip.curve_to_frame.initialize()
		
		# update curves
		status = clip.curve_to_frame.update_curves( context )
		if status is not True:
			self.report( {'ERROR'}, status )
			return {'CANCELLED'}
		
		# check output method
		if(context.scene.ctf_real_copy):
			output = shutil.copyfile
		else:
			output = os.symlink
		
		# get output path
		dst = bpy.path.abspath( context.scene.render.filepath )
		if(dst[-1] != '/'):
			dst += '/'
		dst += clip.name+'.curve_to_frame_output'
		
		# check output path exist, is writable and empty
		if( os.path.exists( dst ) ):
			# check path access
			if(os.access(dst, os.W_OK)):
				# backup old output
				backup_n = context.user_preferences.filepaths.save_version
				backup_output( dst, 0, backup_n )
				
			else:
				# report error then quit 
				self.report(	{'ERROR'},
								'Output path : no write permission' )
				return {'CANCELLED'}
				
		dst += '/'
		
		# create new output directory
		try:
			os.mkdir(dst)
		except OSError as e:
			self.report({'ERROR'}, 
					'Unable to create the output path directory:'+e.strerror)
			return {'CANCELLED'}
		
		# loop from start frame to end frame
		current = context.scene.frame_current
		for frame in range(
						context.scene.frame_start, 
						context.scene.frame_end + 1):
			
			# set current frame and update property value
			context.scene.frame_set(frame)
			
			# get output frame
			fr = clip.curve_to_frame.output
			
			# copy (or symlink) the corresponding 
			# frame into the output path
			try:
				output( clip.curve_to_frame.path + clip.curve_to_frame.get_frame_name(fr),
						dst + clip.curve_to_frame.get_frame_name(context.scene.frame_current)
						)
			except OSError as e:
				self.report({'ERROR'}, 
						'error while copying or linking file: «'\
							+e.strerror+'». Abort action.')
				context.scene.frame_set(current)
				return {'CANCELLED'}
		
		context.scene.frame_set(current)
		
		print('Animation have been generated from '+clip.name+' single track into '+dst+'.')
		return {'FINISHED'}






