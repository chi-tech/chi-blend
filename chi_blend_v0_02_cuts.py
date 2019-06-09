import os
import bpy
from bpy_extras.io_utils import ExportHelper
import mathutils

    
# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
class AddCutLinesButton(bpy.types.Operator):
    bl_label = "Mesh a Planar Straight Line Graph"
    bl_idname = "chitech.addcutsbutton"  
    bl_options = {"UNDO"}
    already_invoked = False

    def CreateXCuts(self,chiprops,context):
        for i in range(0,chiprops.num_x_cuts):
            d = 0.1*(chiprops.ymax-chiprops.ymin)
            dmin = chiprops.ymin-d
            dmax = chiprops.ymax+d
            f = chiprops.x_cuts[i].value
            #print("Xcut %d = %g" %(i,chiprops.x_cuts[i].value))
            point1 = [ f, dmin, 0.0]
            point2 = [ f, dmax, 0.0]
            mesh = bpy.data.meshes.new("")
            mesh.from_pydata([point1,point2], [[0,1]], [])
            mesh.update()
            
            obj = bpy.data.objects.new("Xcut"+str(i),mesh)
            new_origin = mathutils.Vector((f,dmin,0.0))
            obj.data.transform(mathutils.Matrix.Translation(-new_origin))
            obj.matrix_world.translation += new_origin
            context.scene.objects.link(obj)
            
            #bpy.ops.object.select_all(action = "DESELECT")
            obj.select = True
            context.scene.objects.active = obj
            #bpy.ops.object.mode_set(mode="EDIT")

    def CreateYCuts(self,chiprops,context):
        for i in range(0,chiprops.num_y_cuts):
            d = 0.1*(chiprops.xmax-chiprops.xmin)
            dmin = chiprops.xmin-d
            dmax = chiprops.xmax+d
            f = chiprops.y_cuts[i].value
            #print("Xcut %d = %g" %(i,chiprops.x_cuts[i].value))
            point1 = [ dmin, f, 0.0]
            point2 = [ dmax, f, 0.0]
            mesh = bpy.data.meshes.new("")
            mesh.from_pydata([point1,point2], [[0,1]], [])
            mesh.update()
            
            obj = bpy.data.objects.new("Ycut"+str(i),mesh)
            new_origin = mathutils.Vector((dmin,f,0.0))
            obj.data.transform(mathutils.Matrix.Translation(-new_origin))
            obj.matrix_world.translation += new_origin
            context.scene.objects.link(obj)
            
            #bpy.ops.object.select_all(action = "DESELECT")
            obj.select = True
            context.scene.objects.active = obj
            #bpy.ops.object.mode_set(mode="EDIT")
    
    # ===========================================
    def invoke(self, context, event):
        print("executing")
        chiprops = context.scene.chitech_properties

        if ((chiprops.num_x_cuts == 0) and \
            (chiprops.num_y_cuts == 0)):
            self.report({'WARNING'},"No cuts specified")
            return {"FINISHED"}

        # =============== Clear all x and y cuts
        chiprops.x_cuts.clear()
        chiprops.y_cuts.clear()

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
            self.CreateXCuts(chiprops,context) 

        # ============== Create new y-cuts
        if (chiprops.num_y_cuts != 0):
            dy = (chiprops.ymax - chiprops.ymin)/(chiprops.num_y_cuts+1)

            for i in range(0,chiprops.num_y_cuts):
                new_cut = chiprops.y_cuts.add()
                new_cut.value = chiprops.ymin + (i+1)*dy
            self.CreateYCuts(chiprops,context) 

        lbf = context.scene.chiutilsA.ComputeLBF(context)
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