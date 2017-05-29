# Frames-Animated-By-Curve
A Blender plugin who take a short animation of a simple move to make a bigger one, using a F-Curve.



# Addon installation:

1. On **https://github.com/CaptainDesAstres/Frames-Animated-By-Curve** click «clone or download» then «download zip».
2. Run blender, File > User Preferences **(Ctrl + Alt + U)** > Addons.
3. Click «Install From File…» (in bottom of the «Addons» window) and give the path where you have download the addon and confirm.
4. Back to the addons list, check the checkbox of the addon (if necessary, type «Frames Animated By Curve» in the search box to find it)
5. Save user settings


# Introduction:

Frames-Animated-By-Curve is usefull to make long animation from short simple animation. For example, you can render a short animation of a character opening the mouth in 100 frames then use «Frames-Animated-By-Curve» to get an longer animation with a speaking character, with the mouth synchronized to a curve corresponding to his speech. This correpond to the example used in the following tutorial.

All addon feature can be found in Movie Clip Editor, in the Tools (press T key).


# «Single track»: frames, amplitude and output settings:

In the first place, render a «source animation». For the example, we will use an animation of a character with closed mouth at frame 1 and wide open mouth at frame 100 (with a linear interpolation). You should always render the animation as a sequence of image files (jpg, png, exr, etc… ) and never use video file. Our goal is to render a «output animation» of the same character moving is mouth accordingly to a speech sound file.


## Load the animation:

1. In Movie Clip Editor, open/load the rendered sequence.
2. If necessary, open the «Tools» panel on the left of Movie Clip Editor(press T).
3. Display the addon feature by going into the «Curve Anim» tab: to begin, we'll see the settings in «Single track» part of the panel.
4. Firstly, you should have a «Initialize Movie Clip Info button»: press it to get full panel settings. (If there is no button, you're probably trying to use an incompatible Movie Clip format: __Frames-Animated-By-Curve only support sequence of picture, no video format__.

if you load numerous Movie Clip, most part of the following settings will be individual to each Movie Clip.


## Frame to used:

In the exemple, we have rendered 100 frames source animation, but maybe you don't want to use the first 5 frames because you find the mouth too closed: then set «First frame» to 6.
In the same way, maybe you find the mouth too widly open in the 25 last frames: set «Last frame» to 75.

As usual in Blender, you can animate those setting with curve. Just keep in mind that:
* «First frame» must always be greater or equal to 1.
* «End frame» must always be less or equal to Movie Clip total length in frames.
* «End frame» must always be greater or equal to «First frame».
The script will correct settings that don't follow those rules.


## Amplitude settings:

### «Amplitude **(raw)**»:

In the simplest way to use this addon, «Amplitude **(raw)**» is a numerical value which is used to deduct the frame of source animation to use as frame at each frame of the output animation. In our example, this mean that greater the amplitude is, greater the mouth will be open, and vice versa. This settings must generally be animated.

You can animate it manually but, in our example, we probably want to animate this settings with a sound file:
1. Press «I» while over «Amplitude **(raw)**» settings
2. Go to the graph editor and select «Amplitude **(raw)**» fcurve
3. Go into «Key» menu > «Bake Sound to F-Curve»
4. Select your sound file and proceed to the settings in the left panel (see Blender documentation for more info) and confirm.


### Amplitude «Mini» and «Maxi» value:

In the right of «Amplitude **(raw)**» settings is displayed its lowest and greatest values, and under «Amplitude **(raw)**» is 2 settings : «Mini» and «Maxi»: each of those define limit value for «Amplitude **(raw)**»:
* If amplitude is greater than «Maxi», the last frame of source animation will be used for output animation frame.
* If amplitude is lower than «Mini», the first frame of source animation will be used for output animation frame.
* And if amplitude is between the 2 values, then the frame of source animation to use as output animation frame will be deduct proportionnaly to amplitude value.
* If «Mini»/«Maxi» have the same value, the first frame will be used when amplitude is lower, and the last when it's over.
A button directly on the right of «Mini»/«Maxi» allow you to automatically set «Mini»/«Maxi» to the lowest and greatest values of «Amplitude **(raw)**» curve. 

As usual in Blender, you can animate those setting with curve. Just keep in mind that «Maxi» must always be greater than «Mini». If this rule is not respected, the script will act like if «Mini»/«Maxi» are equal to «Mini» value.


### Amplitude net :

At the right of «Mini»/«Maxi» settings is another amplitude field: «amplitude **(net)**». This field isn't editable: it's only here to visualize the effect that «Mini»/«Maxi» settings have on «Amplitude **(raw)**». On its right is a button who allow you to refresh its curve when other settings have change. It result in a curve with varying value between 0 and 1, corresponding respectively to first and last frame of the source animation. 

By default, this curve is hidden in the graph editor but can be visuallize by pressing the eye button. Edition is locked and it's useless to try to edit it manually as all edition will be erased when the curve will be refreshed. So, you should only edit «Amplitude **(raw)**» to see effect on «amplitude **(net)**» after refreshing it.


## Output

### path

In the bottom of the «Single track» part of the panel, you'll find a output field to choose the path where output animation will be saved. By default, it's the same directory than the blender file. Remember that no matter this settings, the script will always create a sub directory for the output animation, named with the Movie Clip name concatenate with '.curve_to_frame_output'. You can find and change the Movie Clip name in the bottom of the Movie Clip Editor. If you name it "chatty.png", then the output directory will be named "chatty.png.curve_to_frame_output"

You should know that the addon script take count of user preferences «Save Versions» settings to keep backup of old output. So, if you run script multiple time, old output will be moved to «chatty.png.curve_to_frame_output.backup1», then «chatty.png.curve_to_frame_output.backup2» and so on…


### animation frame length

The frame range used to define the length of the output animation is the same as for the scene: «Properties» > «Render» > «Dimensions» > «Start Frame»/«End Frame».


### copy file or make a symlink

Over the «output» field, the «Make real copy file» checkbox let you choose if you want the output to be source file copy or if you simply want symbolic link. **On Python, symbolic link are only supported on unix/linux OS. Therefore, this checkbox should always stay checked on Windows.**


### run the script

(A little bit above output settings is «combination mode»: be sure it's set to «Only use amplitude curve» (Other combination mode will be explained later).)

We finaly can run the script to get the output animation: under the Output field, click the «run» button. If all goes well, the output directory will be created (as explained) in the chosen output path and the output animation will be created inside. The output animation must be manually load as a Movie Clip to see result.


### Rounding method

The addon script use «amplitude **(net)**» value (which is a float between 0 and 1) to get source animation frame number to use. for this, it multiply it value by the number of frames of the source animation. There for, he get a float who must be convert into integer: the «rounding method», over the «run» button let you chose the method:
* floor: the largest integer value less than or equal to result value.
* ceil: the smallest integer value greater than or equal to result value.
* round: the result closest integer value.


# «Single track»: peaks and combination settings:

Now that you have seen the result, you probably find that the mouth didn't move enough while the character is speaking: if you've used a sound file as explained above, it's because the sound volume didn't go up and down at each syllable. There is no magic way to do it accordingly to real speech rate but Frames-Animated-By-Curve have a «peak» features that can generate a more realistic result.

Peak generate a «peaks» curve which periodically goes from 0 to 1 to 0 and so on… As for «amplitude **(net)**» curve, the 0 and 1 value correspond respectively to first and last frame of source animation. So, in our example, it will look like Chatty open and close his mouth regularly. And, as for «amplitude **(net)**» curve, «peaks» curve is generated by the script with user settings: it must not be directly edit and it's, by default, hidden in Graph Editor.

To see only peaks curve effect on animation, we firstly set «combination mode» (a little over output settings) to «Only use peaks curve» (Other combination mode will be explained later).


## Peak basics settings

Peak basic settings are under amplitude settings. It's on 2 lines of 4/3 fields each and one refreshing button:
«Rate», «Rate unit»(Frames by default), «constant», «accuracy»,
«Sync to amplitude», «anticipate», «peaks» and the refresh button.


## «peaks» field and refresh button

The last settings, «peaks», is not editable: as explained sooner, it correspond to the generated peaks curve which allow to vizualize settings effect. Right beside it is a refresh button: remember to click it each time you change settings to apply them and vizualize the effect.


## «rate»

The «rate» setting is here to define the rate of peaks. At its right you can choose its unit:
* «Frames» if you simply want to define peaks length in frames.
* «Peaks Per Minute»(ppm) if you prefer to define the number of peaks per minute(ppm).

«Peaks Per Minute» unit is recommanded in case you change your project frame rate in process. For further explanations, we assume that your animation frame rate setting is set to 30 fps («Properties» > «Render» > «Dimensions» > «Frame Rate» > «30 fps»).

As its still '-1', you can see by refreshing the curves that, when rate is less than 0, peaks curve is a horizontal flat curve which worth 1. In the same way, you can set it to 0 and get a flat 0 valued peaks curve. (This is still true, no matter the unit used.)

Now, let's set «rate» to 15 in «Frames» unit and refresh: you now see that the curve regulary goes from 0 to 1 to 0 and so on, at the rate of 2 peak each second. Now, set «rate» to 120 in «Peaks Per Minute» unit and refresh: you have exactly the same result. You can try to run the script and load the resulting animation to see the effect. 

Here is how it's work: If rate is define in frames unit, script get it directly. If rate is define in Peaks Per Minute (ppm), the value in frames is deduct like that : scene.frame_rate x 60 seconds / 120 ppm = 15 frames.

As usual in Blender, you can animate «rate» setting with fcurve. However, the unit is not animatable: when you set it, it's for all the animation.

Here is how it's work:
* At the first frame (frame 1), the script create a 0 valued keyframe in peaks curve , then get the «rate» setting at this frame and deduct at which frame is the following keyframe (half way, 7.5 frames later).
* So the script moved 7.5 frames forward (frame 8.5) and create a new keyframe valued 1. As before, «rate» value is reevaluate and script deduct the following keyframe (always 7.5 in our example, but it could be different if rate is animated).
* The script moved 7.5 frames forward (frame 16) and create a new keyframe valued 0. Again, «rate» value is reevaluate and script deduct the following keyframe (still 7.5 in our example).
* and so on until the last frame.


## «constant»

«Constant» setting active an option that automatically convert «rate» fcurve into constant interpolation mode. It's recomanded to let it checked when «rate» setting is animated using «Peaks Per Minute» unit, especially if you get close to 0 or negative value.

For example:
* unchecked «constant».
* set unit to «Peaks Per Minute».
* At frame 1, set «rate» to 120 and press I to create a keyframe.
* At frame 9, set «rate» to 0 and press I to create a keyframe.
* At frame 65, set «rate» to 120 and press I to create a keyframe.
* In Graph Editor, select the 3 keyframes of the ppm curve, press T and choose the Bezier interpolation mode.
* Now, click refreshing button and look at the result curve.

You'd probably expect to see a first peak from frame 1 to frame 16, then a flat line, then numerous peaks again from frame 65 to the end. Instead, if all goes well, you should get a curve with a 0 keyframe at frame 1, a 1 keyframe at frame 8.5 and, if you scroll enough to the right, a last 0 keyframe at frame 878. So what's append?

As explain above:
* At the first frame, the script create a 0 valued keyframe. Then, as rate is evaluated to 120 peaks per minutes, it deduct the peak length is 15 and the middle keyframe should be 7.5 frames further, at frame 8.5.
* To frame 8.5, script create a 1 valued keyframe. Then, the script reevaluate the «rate» value at this frame, Bezier interpolation for 120 to 0 made the script evaluate rate to 2.07 peaks per minutes at frame 8.5!It deduct that the peak length is now 1739 Frames and that the last peak keyframe is 869.5 frames further, at frame 878.
* So, the script jump to frame 878 without evaluating rate variation between frame 8.5 and 878!

This is why it's recommended to keep constant interpolation mode when animating «rate» in peaks per minute unit with value going closed to 0 or negative… Or to be cautious with wath you do!


## «accuracy»

We have seen previously that rate setting value is evaluated at creation of each peak keyframe. But what append if rate is less or equal to 0? As ther is no peaks, there is no keyframe creation and «rate» setting is not reevaluated… Of course not! Rate value is then regulary reevaluated until it get upper than 0. The gap between 2 reevaluations is then determine by the «accuracy» settings, expressed in frames. (You can't animate «accuracy»: it's set one for all).


## Combination

Now that you have seen the effect of peaks, you probably want the mouth of your chatty character to stop to move when he don't have to speak. We assume here that you have set «amplitude **(raw)**» curve to follow a sound volume variation as explained above and that you have set «rate» to be constantly at 15 frames, and frame rate still to 30 fps.


### visualize 

«Combination» will combine «amplitude **(net)**» curve and «peaks» curve into another curve going from 0 to 1: «combination» curve. As for «amplitude **(net)**» and «peaks» curve:
* The 0 and 1 value correspond respectively to first and last frame of source animation.
* It's associated to an uneditable «combination» setting in the panel.
* It's a generated curve which must not be directly edit.
* It's only provided to visualise settings effect.
* It's, by default, hidden in Graph Editor.
* It's refreshed by all refreshing button.

It's from this curve value that the script deduct the frame from source animation to use. Near of this settings is the «output frame» settings, which is provided to visualise output frame deduct from «combination» curve. Here, the value correspond to the number of the source animation frame to send as output animation frame. As for all generated curve:
* It's associated to a «output frame» curve.
* It's a generated curve which must not be directly edit.
* It's only provided to visualise settings effect.
* It's, by default, hidden in Graph Editor.
* It's refreshed by all refreshing button.


### «Combination mode»

You can choose between 5 «Combination mode»:
* «Only use amplitude curve», which ignore all peaks settings as you've already seen before set peaks settings.
* «Only use peaks curve», which ignore all amplitude settings as see above.
* «Peaks Curve Clamped to amplitude», which use peaks curve but avoid it to get over amplitude value.
* «Peaks Curve Multiplied by amplitude», which use peaks curve and multiply its value by «amplitude **(net)**» value at each frame.
* «Peaks Keyframe Clamped to amplitude», which use peaks curve but use «amplitude **(net)**» as max value. it's like «Peaks Curve Multiplied by amplitude» but only on peaks keyframe.

We recommande the last one. So set «Combination mode» to «Peaks Keyframe Clamped to amplitude» and run the script to see the result.


### Synchronize peaks curve to amplitude

By checking «Sync to amplitude», you activate a feature to synchronize «peaks» curve with «amplitude **(net)**» (except if amplitude settings are ignore by combination mode). If you visualize those curves, you'll see that there is no more peaks when amplitude is equal to 0. With this settings, each time «amplitude **(net)**» is 0, the script will act like rate is 0 too, and so it will use «accuracy» settings and go on until amplitude (and rate) exceed 0.

If «anticipate» settings is 0, the peaks start at the exact moment where amplitude exceed 0. If «anticipate» settings is greater, the peaks will start a little before, and if it's 1, the peaks will end at the exact moment amplitude exceed 0. In any case, the script avoid the peaks start to be before last peaks end.


## Peaks shape

Actually, you can see that peaks are made of straight line, going from 0 to 1 and so on. Maybe you want to change this. There is settings for that between peaks and combination mode settings:
«Peaks Shapes», «Start» and «End».


### Peaks shape settings

«Peaks Shapes» settings allow you to define the shape of the peaks, and «Start»/«End» allow you to define the frame range inside which the shape is define. For example, by default, Start is 0 and End is 2, and if you go to the Graph Editor and watch the «Peaks shapes» curve, you'll see that from frame 0 to 2, the curve have the same shape which is used as peaks shape. 

For a first look, let's hide all curves in Graph Editor and only show «Peaks Shapes» and «Peaks». Now select all «peaks shape» fcurve keyframe and press T then choose «Exponential», then press Ctrl + E and choose «Ease In and Out», you can see the change on «Peaks Shapes» curve. Now, click one of the refreshing curve button in the addon panel: you can now see this that the shape is used as peaks shape in «Peaks» curve. This way, you change the peaks shape any way you want: change keyframe number, position, extrapolation, easing and bezier handle position. Only remember that the first and last keyframe of a peak must have the same value and that «combination» curve will limit peak value between 0 and 1.

At the left of «Peaks Shapes» settings, a button allow you to reset default peaks shape curve and settings.


### Multiple peaks shape:

Maybe you want to use different peaks shape at different moment of the animation. To do this, first, create all the shape of peaks you want in «peaks shape» curve: for example, create a first shape between frame 0 and frame 2, a secound shape between frame 5 and frame 10, and a last one between frame 15 and frame 25. As before, you can use as many keyframe as you want between each interval, and use all interpolation/easing you want. Just remember: each defined interval must have a keyframe where it start and where it end, and this 2 keyframes must have the same value.

Now, go to frame 0 and set «Start»/«End» to 0 and 2 and create keyframes. Then go to frame 75 and set «Start»/«End» to 5 and 10 and create keyframes. Then go to frame 150 and set «Start»/«End» to 15 and 25 and create keyframes. Finally, set peak rate to be 5 Frames and refresh curves: «peaks» curve should use your first shape from frame 0 to frame 75 then the second shape until frame 150 then the thirst until the end. You should notice each peak shape have been horizontally stretch to fit in 5 frames. You should notice too that «Start»/«End» curve is automatically convert into constant interpolation.


### **Major rules to observed with Peaks Shape**

* First and last keyframe must have exactly the same value. Otherwise, the script will return an error.
* The curve value must never get under 0 or over 1. In any case, the combination curve will stay in this range.
* If «Start» and «End» is animated, there fcurve will automatically be convert into «constant» interpolation.


### Clarification

* Peaks length in frame is deduct from rate settings wich can vary. Therefore, the peak shape is horizontaly stretch and, as rate is reevaluated at each peaks keyframe, if rate change between 2 keyframes, the peaks may look more or less stretch from a part to another. If rate goes to 0 or negative value between 2 peaks keyframe, this one can even be stop prematurly.
* If you animate «Start» and «End» to change the peaks shape, the script only consider it after peaks last keyframe. If the value of the last keyframe is not exactly the same that the value of the first keyframe of the new peaks shape, a new keyframe is added (corresponding to the first keyframe of the new peaks shape) after a minimal gap of 0.01 frame.


















