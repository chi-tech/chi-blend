import os
import bpy
from bpy_extras.io_utils import ExportHelper
import subprocess

# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
class ExportTemplateMesh(bpy.types.Operator):
    bl_label = "Exports the 2D mesh as a chitech template"
    bl_idname = "chitech.exporttemplatebutton"  
    bl_options = {"UNDO"}

    # ===========================================
    def invoke(self, context, event):
        chiprops = context.scene.chitech_properties
        context.scene.chiutilsA.ExportTriMesh(context)
        self.report({'INFO'}, "Exported to " + \
                              chiprops.current_object + "_MESH.lua")
        return {"FINISHED"}

def register():
    bpy.utils.register_class(ExportTemplateMesh)
  
def unregister():
    bpy.utils.unregister_class(ExportTemplateMesh)