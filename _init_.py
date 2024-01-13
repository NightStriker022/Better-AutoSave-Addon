import bpy

class AutoSaveTimerThread:
    def __init__(self, interval):
        self.interval = interval
        self.timer = None

    def start(self):
        if self.timer is None:
            self.timer = bpy.app.timers.register(self.save_mainfile, first_interval=self.interval)

    def stop(self):
        if self.timer is not None:
            bpy.app.timers.unregister(self.timer)
            self.timer = None

    def save_mainfile(self):
        bpy.ops.wm.save_mainfile()
        return self.interval  # Reschedule the timer

class AutoSavePanel(bpy.types.Panel):
    bl_label = "AutoSave Panel"
    bl_idname = "PT_AutoSavePanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Tools'

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.operator("wm.start_auto_save")
        row.prop(context.scene, "auto_save_interval", text="Interval (seconds)")
        row.operator("wm.check_ssd_health", text="Check SSD Health")

class WM_OT_StartAutoSave(bpy.types.Operator):
    bl_idname = "wm.start_auto_save"
    bl_label = "Start AutoSave"
    
    def execute(self, context):
        bpy.types.Scene.auto_save_thread = AutoSaveTimerThread(context.scene.auto_save_interval)
        bpy.types.Scene.auto_save_thread.start()
        return {'FINISHED'}

class WM_OT_StopAutoSave(bpy.types.Operator):
    bl_idname = "wm.stop_auto_save"
    bl_label = "Stop AutoSave"
    
    def execute(self, context):
        if hasattr(bpy.types.Scene, "auto_save_thread"):
            bpy.types.Scene.auto_save_thread.stop()
            del bpy.types.Scene.auto_save_thread
        return {'FINISHED'}

class WM_OT_CheckSSDHealth(bpy.types.Operator):
    bl_idname = "wm.check_ssd_health"
    bl_label = "Check SSD Health"

    def execute(self, context):
        # Your SSD health check logic here
        self.report({'INFO'}, "Simulated SSD Health Check Passed")
        return {'FINISHED'}

def register():
    bpy.utils.register_class(AutoSavePanel)
    bpy.utils.register_class(WM_OT_StartAutoSave)
    bpy.utils.register_class(WM_OT_StopAutoSave)
    bpy.utils.register_class(WM_OT_CheckSSDHealth)
    bpy.types.Scene.auto_save_interval = bpy.props.IntProperty(
        name="AutoSave Interval",
        description="Time interval for autosave in seconds",
        default=5,
        min=1,
    )

def unregister():
    bpy.utils.unregister_class(AutoSavePanel)
    bpy.utils.unregister_class(WM_OT_StartAutoSave)
    bpy.utils.unregister_class(WM_OT_StopAutoSave)
    bpy.utils.unregister_class(WM_OT_CheckSSDHealth)
    del bpy.types.Scene.auto_save_interval

if __name__ == "__main__":
    register()
