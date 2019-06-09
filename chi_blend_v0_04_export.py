import os
import bpy
from bpy_extras.io_utils import ExportHelper

# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
class ExportTemplateMesh(bpy.types.Operator):
    bl_label = "Exports the 2D mesh as a chitech template"
    bl_idname = "chitech.exporttemplatebutton"  
    bl_options = {"UNDO"}

    # ===========================================
    def invoke(self, context, event):
        context.scene.chiutilsA.ExportTriMesh(context)
        return {"FINISHED"}

def register():
    bpy.utils.register_class(ExportTemplateMesh)
  
def unregister():
    bpy.utils.unregister_class(ExportTemplateMesh)