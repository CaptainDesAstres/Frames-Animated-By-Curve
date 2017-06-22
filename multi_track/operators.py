import bpy, os, shutil
from functions import *


class AmplitudeMinMax(bpy.types.Operator):
	'''operator to initialize or refresh curve to frame info of the scene'''
	bl_idname = "curve_to_frame.multi_track_get_amplitude_range"
	bl_label= "get scene amplitude curve mini and maxi value"
	bl_options = {'INTERNAL'}
	
	def execute(self, context):
		'''get scene amplitude curve mini and maxi value'''
		scene = context.scene
		
		fCurve = get_fcurve_by_data_path(scene, 'curve_to_frame.amplitude')
		if(fCurve is None):
			m = M = scene.curve_to_frame.amplitude
		else:
			scene.curve_to_frame.mini, scene.curve_to_frame.maxi = get_curve_limit(fCurve)
		
		# update curves
		status = scene.curve_to_frame.update_curves( context )
		if status is True:
			return {'FINISHED'}
		else:
			self.report( {'ERROR'}, status )
			return {'CANCELLED'}





class RestoreDefaultPeakShape(bpy.types.Operator):
	'''Restore default peak shape settings for multi track'''
	bl_idname = "curve_to_frame.multi_track_default_peak_shape"
	bl_label= "restore default peak shape settings for multi track"
	bl_options = {'INTERNAL'}
	
	def execute(self, context):
		'''restore default peak shape settings for multi track'''
		context.scene.curve_to_frame.init_peaks_shape_curve()
		return {'FINISHED'}





class CurvesRefresh(bpy.types.Operator):
	'''operator to initialize or refresh curve to frame info of the scene'''
	bl_idname = "curve_to_frame.generate_multi_track_curves"
	bl_label= "refresh multi track curves"
	bl_options = {'INTERNAL'}
	
	def execute(self, context):
		'''refresh scene curves'''
		status = context.scene.curve_to_frame.update_curves( context )
		if status is True:
			return {'FINISHED'}
		else:
			self.report( {'ERROR'}, status )
			return {'CANCELLED'}





class SwitchCurveRefresh(bpy.types.Operator):
	'''operator to refresh track switching curve'''
	bl_idname = "curve_to_frame.generate_track_switching_curve"
	bl_label= "refresh track switching curve"
	bl_options = {'INTERNAL'}
	
	def execute(self, context):
		'''refresh track switching curve'''
		context.scene.curve_to_frame.update_switch_curve( context )
		return {'FINISHED'}





class CurveToFrame(bpy.types.Operator):
	'''the operator to render multi track curve to frame animation'''
	bl_idname = "curve_to_frame.render_multi_track"
	bl_label= "Animate Tracks By Curves"
	bl_options = {'INTERNAL'}
	
	def execute(self, context):
		scene = context.scene.curve_to_frame
		
		# check track list isn't empty
		if len(scene.tracks) == 0:
			self.report( {'ERROR'}, 'There is no tracks in the list!' )
			return {'CANCELLED'}
		
		for t in scene.tracks:
			# check every track correspond to a movie clip
			track = t.get(True)
			if track is None:
				self.report( {'ERROR'}, 'There is no loaded movieclip corresponding to «'+t.name+'» track!' )
				return {'CANCELLED'}
			
			# check every image of every track
			if not track.curve_to_frame.check_image_file():
				self.report( {'ERROR'}, 'There is at least one image file missing for «'+track.curve_to_frame.name+'» (in «'+track.curve_to_frame.path+'» directory)!' )
				return {'CANCELLED'}
		
		
		# refresh animation curves
		confirm = scene.update_curves( context )
		if confirm is not True:
			self.report( {'ERROR'}, confirm )
			return {'CANCELLED'}
		
		# refresh track switcthing curve
		scene.update_switch_curve( context )
		
		# check output method
		if(context.scene.ctf_real_copy):
			output = shutil.copyfile
		else:
			output = os.symlink
		
		# get output path
		blender_file_name = os.path.splitext( 
				bpy.path.basename(
						bpy.context.blend_data.filepath
						)
				)[0]
		scene_name = context.scene.name
		dst = bpy.path.abspath( context.scene.render.filepath )
		if(dst[-1] != '/'):
			dst += '/'
		dst += blender_file_name+':'+scene_name+'.curve_to_frame_output'
		
		# make backup if output path already exists
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
			
			# get output frame and track
			track = scene.tracks[ scene.generated_switch ]
			clip = track.get( True )
			fr = clip.curve_to_frame.first
			fr += track.get_frame( scene.combination ) - 1
			
			# copy (or symlink) the corresponding 
			# frame into the output path
			try:
				output( clip.curve_to_frame.path + clip.curve_to_frame.get_frame_name(fr),
						dst + str(context.scene.frame_current).rjust( 6, '0') + clip.curve_to_frame.ext
						)
			except OSError as e:
				self.report({'ERROR'}, 
						'error while copying or linking file: «'\
							+e.strerror+'». Abort action.')
				context.scene.frame_set(current)
				return {'CANCELLED'}
		
		context.scene.frame_set(current)
		
		
		print('Animation have been generated from «'+context.scene.name+'» scene multi track to:\n\t\t'+dst+'')
		return {'FINISHED'}








