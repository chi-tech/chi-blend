import os
import bpy
from bpy_extras.io_utils import ExportHelper
import mathutils
import subprocess

    

# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
class AddBalancedCutLinesButton(bpy.types.Operator):
    bl_label = "Mesh a Planar Straight Line Graph"
    bl_idname = "chitech.addbalcutsbutton"  
    bl_options = {"UNDO"}
    already_invoked = False
    bl_description = "Uses ChiTech to generated balanced cutlines " + \
                     " across the 2D domain."

    # ===========================================
    def invoke(self, context, event):
        print("Executing balanced cutlines")
        chiprops = context.scene.chitech_properties
        chiutilsA = context.scene.chiutilsA

        # Check ChiTech Path is specified
        if (not chiutilsA.CheckChiAndMeshPaths(context)):
            return {"FINISHED"}
        pathdir = chiprops.path_to_workdir
        pathexe = context.scene.chitech_properties.path_to_chitech_exe

        if ((chiprops.num_x_cuts == 0) and \
            (chiprops.num_y_cuts == 0)):
            self.report({'WARNING'},"No cuts specified")
            return {"FINISHED"}

         # Clear all x and y cuts
        chiprops.x_cuts.clear()
        chiprops.y_cuts.clear()

        # Get selection bound box
        bbox = bpy.data.objects[chiprops.current_object+"TriMesh"].bound_box
        scale = bpy.data.objects[chiprops.current_object+"TriMesh"].scale
        location = bpy.data.objects[chiprops.current_object+"TriMesh"].location
        context.scene.chitech_properties.xmin = bbox[0][0]*scale[0]+location[0]
        context.scene.chitech_properties.ymin = bbox[0][1]*scale[1]+location[1]
        context.scene.chitech_properties.xmax = bbox[7][0]*scale[0]+location[0]
        context.scene.chitech_properties.ymax = bbox[7][1]*scale[1]+location[1]

        # Delete existing objects
        bpy.ops.object.select_all(action='DESELECT')
        bpy.ops.object.select_pattern(pattern="Xcut*")
        bpy.ops.object.delete(use_global=True)
        bpy.ops.object.select_all(action='DESELECT')
        bpy.ops.object.select_pattern(pattern="Ycut*")
        bpy.ops.object.delete(use_global=True)

        # Check object selection valid
        cur_objname = context.scene.chitech_properties.current_object
        if (cur_objname == ""):
            self.report({'WARNING'},"No object selected")
            return {"FINISHED"}
        
        # Export PSLG
        scene = context.scene
        bpy.ops.object.select_all(action='DESELECT')
        for obj in scene.objects:
            if (obj.name == (cur_objname+"TriMesh")):
                bpy.data.objects[cur_objname+"TriMesh"].select_set(True)
                bpy.context.view_layer.objects.active = bpy.data.objects[cur_objname+"TriMesh"]
                bpy.ops.export_scene.obj(
                   filepath       = pathdir+"/Mesh/"+cur_objname+"BalancedCuts.obj",
                   check_existing = False,
                   axis_forward   = 'Y',
                   axis_up        = 'Z',
                   use_selection  = True,
                   use_materials  = False)
                self.report({'INFO'},"PSLG export to " + pathdir+"/"+cur_objname+"BalancedCuts.obj")
        
        # Write ChiTech input
        h = open(pathdir+"/Mesh/"+cur_objname+"BalancedCuts.lua",'w')  
        h.write('chiMeshHandlerCreate()\n')
        h.write('\n')
        h.write('newSurfMesh = chiSurfaceMeshCreate();\n')
        h.write('chiSurfaceMeshImportFromOBJFile(newSurfMesh,"')
        h.write("Mesh/"+cur_objname+'BalancedCuts.obj')
        h.write('",true)\n')
        h.write('chiDecomposeSurfaceMeshPxPy(newSurfMesh,'+str(chiprops.num_x_cuts+1)+
               ',' + str(chiprops.num_y_cuts+1) + ')\n')
        h.close()  

        # $$$$$$$$$$$$$$$$$$$$$  Execute ChiTech
        process = subprocess.Popen([pathexe,
            "Mesh/" + cur_objname+"BalancedCuts.lua"],
            cwd=pathdir,
            stdout=subprocess.PIPE,
            universal_newlines=True)
        process.wait()
        out,err = process.communicate()
        print(out)

        # Extract x and y cut values
        cell_start = out.find('Number of cells in region = ')
        cell_end   = out.find('\n',cell_start)

        # ============== Create new x-cuts
        if (chiprops.num_x_cuts != 0):
            for i in range(0,chiprops.num_x_cuts):
                cut_start = out.find('X-cut'+str(i)+' ')
                cut_mid   = out.find(' ',cut_start)
                cut_end   = out.find('\n',cut_start)
                #print(out[cut_mid:cut_end])
                cut_value = float(out[cut_mid:cut_end])

                new_cut = chiprops.x_cuts.add()
                new_cut.value = cut_value
            chiutilsA.CreateXCuts(chiprops,context) 

        # ============== Create new y-cuts
        if (chiprops.num_y_cuts != 0):
            for i in range(0,chiprops.num_y_cuts):
                cut_start = out.find('Y-cut'+str(i)+' ')
                cut_mid   = out.find(' ',cut_start)
                cut_end   = out.find('\n',cut_start)
                cut_value = float(out[cut_mid:cut_end])

                new_cut = chiprops.y_cuts.add()
                new_cut.value = cut_value
            chiutilsA.CreateYCuts(chiprops,context) 

        # lbf = context.scene.chiutilsA.ComputeLBF(context)
        # chiprops.load_bal_factor_i = lbf

        return {'RUNNING_MODAL'}

def register():
    bpy.utils.register_class(AddBalancedCutLinesButton)
  
def unregister():
    bpy.utils.unregister_class(AddBalancedCutLinesButton)