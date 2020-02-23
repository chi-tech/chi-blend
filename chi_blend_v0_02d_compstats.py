import os
import bpy
from bpy_extras.io_utils import ExportHelper
import subprocess


# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
class ComputeMeshStats(bpy.types.Operator):
    bl_label = "Gets the open edges from a chitech server"
    bl_idname = "chitech.computemeshstats"  
    bl_options = {"UNDO"}
    bl_description = "Exports Triangle mesh to ChiTech and computes " + \
                     "mesh statistics. <Object>TriMesh"

    # ===========================================
    def invoke(self, context, event):
        chiprops = context.scene.chitech_properties
        cur_objname = chiprops.current_object+"TriMesh"
        pathdir = chiprops.path_to_workdir

        # Delete Existing edge analyses
        bpy.ops.object.select_all(action='DESELECT')
        bpy.ops.object.select_pattern(pattern="EdgeAnalysis*")
        bpy.ops.object.delete(use_global=True)

        # Select the TriMesh
        bpy.ops.object.select_all(action='DESELECT')
        bpy.ops.object.select_pattern(pattern=cur_objname+"*")
        bpy.context.view_layer.objects.active = bpy.data.objects[cur_objname]

        # Export the TriMesh
        bpy.ops.export_scene.obj(
                   filepath       = pathdir + "/Mesh/" + \
                       cur_objname+"SurfaceMesh.obj",
                   check_existing = False,
                   axis_forward   = 'Y',
                   axis_up        = 'Z',
                   use_selection  = True,
                   use_materials  = False)

        xcuts=[]
        ycuts=[]

        # Write Chitech commands
        h = open(pathdir+"/Mesh/"+cur_objname+"OE.lua",'w')    
        h.write('chiMeshHandlerCreate()\n')
        h.write('\n')
        h.write('newSurfMesh = chiSurfaceMeshCreate();\n')
        h.write('chiSurfaceMeshImportFromOBJFile(newSurfMesh,"')
        h.write(pathdir+"Mesh/"+cur_objname+'SurfaceMesh.obj')
        h.write('",true)\n')
        h.write('\n')
        # h.write('chiSurfaceMeshExtractOpenEdgesToObj(newSurfMesh,"')
        # h.write('Mesh/EdgeAnalysis.obj")\n')
        h.write('chiSurfaceMeshCheckCycles(newSurfMesh,64*4)\n\n')
        # Extract current Xcut-lines
        bpy.ops.object.select_all(action='DESELECT')
        bpy.ops.object.select_pattern(pattern="Xcut*")
        h.write('xcuts={\n')
        for obj in bpy.context.selected_objects:
            h.write(str(obj.location[0])+',\n')
            xcuts.append(obj.location[0])
        h.write('}\n\n')
        # Extract current Ycut-lines
        bpy.ops.object.select_all(action='DESELECT')
        bpy.ops.object.select_pattern(pattern="Ycut*")
        h.write('ycuts={\n')
        for obj in bpy.context.selected_objects:
            h.write(str(obj.location[1])+',\n')
            ycuts.append(obj.location[1])
        h.write('}\n\n')
        h.write('chiComputeLoadBalancing(newSurfMesh,xcuts,ycuts)\n')
        h.close()      

        # Execute ChiTech
        pathexe = chiprops.path_to_chitech_exe
        print("RUNNING CHITECH")
        process = subprocess.Popen([pathexe,
            "Mesh/" + cur_objname+"OE.lua"],
            cwd=pathdir,
            stdout=subprocess.PIPE,
            universal_newlines=True)
        process.wait()
        out,err = process.communicate()
        print(out)

        # Update x and y cuts
        chiprops.num_x_cuts = len(xcuts)
        chiprops.num_y_cuts = len(ycuts)

        chiprops.x_cuts.clear()
        chiprops.y_cuts.clear()

        xcuts.sort()
        ycuts.sort()

        for i in range(0,chiprops.num_x_cuts):
                new_cut = chiprops.x_cuts.add()
                new_cut.value = xcuts[i]

        for j in range(0,chiprops.num_y_cuts):
                new_cut = chiprops.y_cuts.add()
                new_cut.value = ycuts[j]

        context.scene.chiutilsA.ShowMessageBox(out)
        
        # Import the generated file
        # bpy.ops.import_scene.obj(filepath=(pathdir+"/Mesh/"+'EdgeAnalysis.obj'),
        #                          axis_forward = 'Y',
        #                          axis_up      = 'Z')  

        return {"FINISHED"}

def register():
    bpy.utils.register_class(ComputeMeshStats)
  
def unregister():
    bpy.utils.unregister_class(ComputeMeshStats)