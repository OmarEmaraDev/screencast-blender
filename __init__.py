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
        "and save it in ~/Videos/screencasts/<timestamp>/"
    ),
    "warning": "",
    "doc_url": "",
    "tracker_url": "",
    "category": "Interface",
}

import bpy
from datetime import datetime
from os.path import expanduser

class ScreenCast(bpy.types.Operator):
    bl_idname = "screen.screen_cast"
    bl_label = "Screen Cast"

    frame = None
    timer = None
    timestamp = None

    def modal(self, context, event):
        if self.frame > context.scene.frame_end:
            self.finish(context)
            return {"FINISHED"}

        if event.type == "ESC":
            self.cancel(context)
            return {"CANCELLED"}

        if event.type == "TIMER":
            context.scene.frame_set(self.frame)
            path = f"~/Videos/screencasts/{self.timestamp}/{self.frame:05}.png"
            bpy.ops.screen.screenshot(filepath = expanduser(path))

            self.frame += 1

        return {"PASS_THROUGH"}

    def execute(self, context):
        wm = context.window_manager
        self.timer = wm.event_timer_add(0.1, window = context.window)
        wm.modal_handler_add(self)

        self.frame = context.scene.frame_start
        self.timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

        context.scene.frame_set(self.frame)

        return {"RUNNING_MODAL"}

    def finish(self, context):
        wm = context.window_manager
        wm.event_timer_remove(self.timer)

    def cancel(self, context):
        self.finish(context)

def register():
    bpy.utils.register_class(ScreenCast)
    
def unregister():
    bpy.utils.unregister_class(ScreenCast)
