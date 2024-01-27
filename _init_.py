bl_info = {
    "name": "Better AutoSave Addon",
    "blender": (4, 0, 2),
    "category": "System",
}

import bpy
import threading
import subprocess
import time
import os

class AutoSaveTimerThread(threading.Thread):
    def __init__(self, interval, auto_save_folder):
        threading.Thread.__init__(self)
        self.daemon = True
        self.interval = interval
        self.auto_save_folder = auto_save_folder
        self.stopped = threading.Event()  # Event to signal the thread to stop

    def run(self):
        while not self.stopped.is_set():
            time.sleep(self.interval)
            self.save_mainfile()

    def save_mainfile(self):
        timestamp = bpy.context.scene.frame_current
        file_path = os.path.join(self.auto_save_folder, f"auto_save_{timestamp}.blend")
        bpy.ops.wm.save_as_mainfile(filepath=file_path, check_existing=False)

    def stop(self):
        self.stopped.set()

class AutoSavePanel(bpy.types.Panel):
    bl_label = "Better AutoSave"
    bl_idname = "PT_AutoSavePanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Better AutoSave'

    def draw(self, context):
        layout = self.layout

        # Start AutoSave button
        row = layout.row()
        row.operator("wm.start_auto_save")
        row.prop(context.scene, "auto_save_interval", text="Interval (seconds)")

        # Stop AutoSave button
        row = layout.row()
        row.operator("wm.stop_auto_save", text="Stop AutoSave")

        # Check SSD Health button
        row = layout.row()
        row.operator("wm.check_ssd_health", text="Check SSD Health")

class WM_OT_StartAutoSave(bpy.types.Operator):
    bl_idname = "wm.start_auto_save"
    bl_label = "Start AutoSave"
    
    def execute(self, context):
        desktop = os.path.join(os.path.expanduser("~"), "Desktop")
        auto_save_folder = os.path.join(desktop, "AutoSaves")
        
        if not os.path.exists(auto_save_folder):
            os.makedirs(auto_save_folder)
        
        bpy.types.Scene.auto_save_thread = AutoSaveTimerThread(context.scene.auto_save_interval, auto_save_folder)
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
        try:
            # Run the smartctl command to get SMART data from the SSD
            result = subprocess.run(["smartctl", "--all", "/dev/sdX"], capture_output=True, text=True)
            
            # Check if the command was successful
            if result.returncode == 0:
                smart_data = result.stdout
                
                # Example: Look for the Wear Leveling Count attribute
                wear_leveling_count = self.extract_attribute_value(smart_data, "Wear_Leveling_Count")
                
                # Example: Check if Wear Leveling Count is below a threshold
                if wear_leveling_count is not None and wear_leveling_count < 100:
                    self.report({'WARNING'}, f"SSD Wear Leveling Count is {wear_leveling_count}. Consider replacing the SSD.")
                else:
                    self.report({'INFO'}, "SSD Health Check Passed")
            else:
                self.report({'ERROR'}, "Failed to retrieve SMART data. Ensure smartctl is installed.")
        
        except Exception as e:
            self.report({'ERROR'}, f"An error occurred: {str(e)}")
        
        return {'FINISHED'}

    def extract_attribute_value(self, smart_data, attribute_name):
        # Example: Extract attribute value from SMART data
        lines = smart_data.split('\n')
        for line in lines:
            if attribute_name in line:
                parts = line.split()
                if len(parts) >= 10:
                    value = int(parts[9])
                    return value
        return None

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
