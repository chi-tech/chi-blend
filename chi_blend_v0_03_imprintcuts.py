import os
import bpy
from bpy_extras.io_utils import ExportHelper
import mathutils
import numpy as np
    
# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
class ImprintCutLines(bpy.types.Operator):
    bl_label = "Mesh a Planar Straight Line Graph"
    bl_idname = "chitech.imprintcutsbutton"  
    bl_options = {"UNDO"}

    # ===========================================
    def invoke(self, context, event):
        chiprops = context.scene.chitech_properties
        cur_objname = chiprops.current_object+"TriMesh"

        # Perform knife operation
        bpy.ops.object.select_all(action='DESELECT')
        bpy.ops.object.select_pattern(pattern="Xcut*")
        bpy.ops.object.select_pattern(pattern="Ycut*")
        bpy.ops.object.select_pattern(pattern=cur_objname+"*")

        bpy.context.scene.objects.active = bpy.data.objects[cur_objname]
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.knife_project(cut_through=True)
        bpy.ops.object.mode_set(mode='OBJECT')

        # Make current_object active
        bpy.ops.object.select_all(action='DESELECT')
        bpy.ops.object.select_pattern(pattern=cur_objname+"*")
        bpy.context.scene.objects.active = bpy.data.objects[cur_objname]

        lbf = context.scene.chiutilsA.ComputeLBF(context)

        chiprops.load_bal_factor_f = lbf
        return {"FINISHED"}

def register():
    bpy.utils.register_class(ImprintCutLines)
  
def unregister():
    bpy.utils.unregister_class(ImprintCutLines)