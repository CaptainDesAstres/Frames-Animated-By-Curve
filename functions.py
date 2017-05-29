import os, shutil, bpy

def backup_output( path, level, maximum ):
	'''backup output directory'''
	# get backup path
	if level != 0:
		backup = path+'.backup'+str(level)
	else:
		backup = path
	
	# check older backup
	if os.path.exists( backup ):
		backup_output( path, level+1, maximum )
	else:
		return
	
	# erase too old backup
	if level >= maximum:
		shutil.rmtree(backup)
	else:
		# increment the backup
		shutil.move(
								backup,
								path+'.backup'+str(level+1)
								)






def get_fcurve_by_data_path(ob, path):
	'''Return object fcurve corresponding to datapath or None'''
	
	if(ob.animation_data is None or ob.animation_data.action is None):
		return None
	
	for curve in ob.animation_data.action.fcurves:
		if curve.data_path == path:
			return curve
	return None





def get_curve_limit( curve ):
	'''return curve min and max values'''
	m = M = curve.evaluate(1)
	s, e = curve.range()
	
	if s < bpy.context.scene.frame_start:
		s = bpy.context.scene.frame_start
	
	if e > bpy.context.scene.frame_end:
		e = bpy.context.scene.frame_end
	
	for i in range(int(s)-1, int(e)+1):
		val = curve.evaluate(i)
		if val < m:
			m = val
		if val > M:
			M = val
	return (m,M)







def avoid_useless_keyframe( curve ):
	'''erase useless keyframe of a curve'''
	k = 1
	while(k < len(curve.keyframe_points)-1 ):
		prev = curve.keyframe_points[ k-1 ]
		cur = curve.keyframe_points[ k ]
		next = curve.keyframe_points[ k+1 ]
		if( prev.co[1] == cur.co[1] and cur.co[1] == next.co[1] ):
			curve.keyframe_points.remove( cur )
		else:
			k += 1

