import os
import bpy
from bpy_extras.io_utils import ExportHelper
import subprocess

# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
class GetOpenEdgesButton(bpy.types.Operator):
    bl_label = "Gets the open edges from a chitech server"
    bl_idname = "chitech.getopenedgesbutton"  
    bl_options = {"UNDO"}

    # ===========================================
    def invoke(self, context, event):
        chiprops = context.scene.chitech_properties
        cur_objname = chiprops.current_object+"TriMesh"
        pathdir = chiprops.path_to_workdir

        # Select the TriMesh
        bpy.ops.object.select_all(action='DESELECT')
        bpy.ops.object.select_pattern(pattern=cur_objname+"*")
        bpy.context.scene.objects.active = bpy.data.objects[cur_objname]

        bpy.ops.export_scene.obj(
                   filepath       = pathdir + "/Mesh/" + \
                       cur_objname+"SurfaceMesh.obj",
                   check_existing = False,
                   axis_forward   = 'Y',
                   axis_up        = 'Z',
                   use_selection  = True,
                   use_materials  = False)

        h = open(pathdir+"/Mesh/"+cur_objname+"OE.lua",'w')    
        h.write('chiMeshHandlerCreate()\n')
        h.write('\n')
        h.write('newSurfMesh = chiSurfaceMeshCreate();\n')
        h.write('chiSurfaceMeshImportFromOBJFile(newSurfMesh,"')
        h.write(pathdir+"Mesh/"+cur_objname+'SurfaceMesh.obj')
        h.write('",true)\n')
        h.write('\n')
        h.write('chiSurfaceMeshExtractOpenEdgesToObj(newSurfMesh,"')
        h.write('ZEdgesTest.obj")\n')
        h.close()      

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

        return {"FINISHED"}

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
    bpy.utils.register_class(GetOpenEdgesButton)
  
def unregister():
    bpy.utils.unregister_class(ExportTemplateMesh)
    bpy.utils.unregister_class(GetOpenEdgesButton)