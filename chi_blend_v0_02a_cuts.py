import os
import bpy
from bpy_extras.io_utils import ExportHelper
import mathutils
import subprocess

    
# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
class AddCutLinesButton(bpy.types.Operator):
    bl_label = "Mesh a Planar Straight Line Graph"
    bl_idname = "chitech.addcutsbutton" 
    bl_description = "Generates equally spaced cutlines " + \
                     "across the 2D domain." 
    bl_options = {"UNDO"}
    already_invoked = False
    
    # ===========================================
    def invoke(self, context, event):
        print("Executing Equally spaced cutlines.")
        chiprops = context.scene.chitech_properties
        chiutilsA = context.scene.chiutilsA

        if ((chiprops.num_x_cuts == 0) and \
            (chiprops.num_y_cuts == 0)):
            self.report({'WARNING'},"No cuts specified")
            return {"FINISHED"}

        # =============== Clear all x and y cuts
        chiprops.x_cuts.clear()
        chiprops.y_cuts.clear()

        # ============== Get selection bound box
        bbox = bpy.data.objects[chiprops.current_object+"TriMesh"].bound_box
        scale = bpy.data.objects[chiprops.current_object+"TriMesh"].scale
        location = bpy.data.objects[chiprops.current_object+"TriMesh"].location
        context.scene.chitech_properties.xmin = bbox[0][0]*scale[0]+location[0]
        context.scene.chitech_properties.ymin = bbox[0][1]*scale[1]+location[1]
        context.scene.chitech_properties.xmax = bbox[7][0]*scale[0]+location[0]
        context.scene.chitech_properties.ymax = bbox[7][1]*scale[1]+location[1]

        # ============== Delete existing objects
        bpy.ops.object.select_all(action='DESELECT')
        bpy.ops.object.select_pattern(pattern="Xcut*")
        bpy.ops.object.delete(use_global=True)
        bpy.ops.object.select_all(action='DESELECT')
        bpy.ops.object.select_pattern(pattern="Ycut*")
        bpy.ops.object.delete(use_global=True)
            

           
        # ============== Create new x-cuts
        if (chiprops.num_x_cuts != 0):
            dx = (chiprops.xmax - chiprops.xmin)/(chiprops.num_x_cuts+1)

            for i in range(0,chiprops.num_x_cuts):
                new_cut = chiprops.x_cuts.add()
                new_cut.value = chiprops.xmin + (i+1)*dx
            chiutilsA.CreateXCuts(chiprops,context) 

        # ============== Create new y-cuts
        if (chiprops.num_y_cuts != 0):
            dy = (chiprops.ymax - chiprops.ymin)/(chiprops.num_y_cuts+1)

            for i in range(0,chiprops.num_y_cuts):
                new_cut = chiprops.y_cuts.add()
                new_cut.value = chiprops.ymin + (i+1)*dy
            chiutilsA.CreateYCuts(chiprops,context) 

        lbf = -1.0 #context.scene.chiutilsA.ComputeLBF(context)
        chiprops.load_bal_factor_i = lbf

        if (not self.already_invoked):
            self.already_invoked = True
            print("Event handler started")
            context.window_manager.modal_handler_add(self)

        return {'RUNNING_MODAL'}

    # ======================================
    def modal(self, context, event):
        chiprops = context.scene.chitech_properties

        if (chiprops.lbf_live_update):
            #if (event.type == 'MOUSEMOVE'):
                lbf = context.scene.chiutilsA.ComputeLBF(context)
                chiprops.load_bal_factor_i = lbf
                for region in context.area.regions:
                    if region.type == "TOOLS":
                        region.tag_redraw()
        

        if event.type == 'ESC':
            print("Finished")
            return {'CANCELLED'}  
       
        return {'PASS_THROUGH'}



def register():
    bpy.utils.register_class(AddCutLinesButton)
  
def unregister():
    bpy.utils.unregister_class(AddCutLinesButton)