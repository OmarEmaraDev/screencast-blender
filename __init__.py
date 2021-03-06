'''
Copyright (C) 2020 Omar Emara
mail@OmarEmara.dev

Created by Omar Emara

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

bl_info = {
    "name": "Screen Cast",
    "author": "Omar Emara",
    "version": (1, 0),
    "blender": (2, 90, 0),
    "location": 'Search For "Screen Cast"',
    "description": (
        "Take a screencast of the screen in the scene's frame range "
        "and save it in ~/Videos/screencasts/<timestamp>/ creating "
        "an H.264 MP4 video using ffmpeg if possible"
    ),
    "warning": "",
    "doc_url": "",
    "tracker_url": "",
    "category": "Interface",
}

import bpy
import shutil
import subprocess
from datetime import datetime
from os.path import expanduser

class ScreenCast(bpy.types.Operator):
    bl_idname = "screen.screen_cast"
    bl_label = "Screen Cast"

    timerDuration: bpy.props.FloatProperty(name = "Timer Duration", default = 0.1)
    createVideo: bpy.props.BoolProperty(name = "Create Video", default = True)

    frame = None
    timer = None
    timestamp = None

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def modal(self, context, event):
        if self.frame > context.scene.frame_end:
            self.finish(context)
            return {"FINISHED"}

        if event.type == "ESC":
            self.cancel(context)
            return {"CANCELLED"}

        if event.type == "TIMER":
            path = f"~/Videos/screencasts/{self.timestamp}/{self.frame:05}.png"
            bpy.ops.screen.screenshot(filepath = expanduser(path))

            self.frame += 1
            context.scene.frame_set(self.frame)

        return {"PASS_THROUGH"}

    def execute(self, context):
        wm = context.window_manager
        self.timer = wm.event_timer_add(self.timerDuration, window = context.window)
        wm.modal_handler_add(self)

        self.frame = context.scene.frame_start
        self.timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

        context.scene.frame_set(self.frame)

        return {"RUNNING_MODAL"}

    def finish(self, context):
        wm = context.window_manager
        wm.event_timer_remove(self.timer)

        if self.createVideo and shutil.which("ffmpeg") is not None:
            subprocess.run([
                "ffmpeg",
                "-framerate",
                str(int(context.scene.render.fps / context.scene.render.fps_base)),
                "-pattern_type",
                "glob",
                "-i",
                expanduser(f"~/Videos/screencasts/{self.timestamp}/*.png"),
                "-c:v",
                "libx264",
                "-pix_fmt",
                "yuv420p",
                expanduser(f"~/Videos/screencasts/{self.timestamp}/output.mp4"),
            ])

    def cancel(self, context):
        self.finish(context)

def register():
    bpy.utils.register_class(ScreenCast)
    
def unregister():
    bpy.utils.unregister_class(ScreenCast)
