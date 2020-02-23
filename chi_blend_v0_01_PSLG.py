import os
import bpy
from bpy_extras.io_utils import ExportHelper
import subprocess


    
# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
class MeshPSLGButton(bpy.types.Operator):
    bl_label = "Mesh a Planar Straight Line Graph"
    bl_idname = "chitech.pslgbutton"  
    bl_description = "Export the edges of the current object as " + \
                     "a Planar Straight Line Graph and create a " + \
                     "triangular mesh"
    bl_options = {"UNDO"}
    
    def invoke(self, context, event):
        print("Executing Mesh PSLG")
        chiprops = context.scene.chitech_properties
        chiutilsA = context.scene.chiutilsA

        # Check valid path to ChiTech, Triangle and Workdir
        if (not chiutilsA.CheckAllPaths(context)):
            return {"FINISHED"}
        pathdir = chiprops.path_to_workdir

        # Check ChiTech Path is specified
        pathexe = context.scene.chitech_properties.path_to_chitech_exe

        # Get path to triangle
        tri_exe_path = context.scene.chitech_properties.path_to_triangle_exe
        tri_exe_path += " -pqa"+str(chiprops.triangle_area)
        
        # Check working directory specified
        pathdir = context.scene.chitech_properties.path_to_workdir
        
        # Check object selection valid
        cur_objname = context.scene.chitech_properties.current_object
        if (cur_objname == ""):
            self.report({'WARNING'},"No object selected")
            return {"FINISHED"}
        
        # Export PSLG
        scene = context.scene
        bpy.ops.object.select_all(action='DESELECT')
        for obj in scene.objects:
            if (obj.name == cur_objname):
                bpy.data.objects[cur_objname].select_set(True)
                # bpy.context.scene.objects.active = bpy.data.objects[cur_objname]
                bpy.ops.export_scene.obj(
                   filepath       = pathdir+"/Mesh/"+cur_objname+"PreMesh.obj",
                   check_existing = False,
                   axis_forward   = 'Y',
                   axis_up        = 'Z',
                   use_selection  = True,
                   use_materials  = False)
                self.report({'INFO'},"PSLG export to " + pathdir+"/"+cur_objname+"PreMesh.obj")
        
        # Write ChiTech input
        h = open(pathdir+"/Mesh/"+cur_objname+"PreMesh.lua",'w')  
        h.write('chiMeshHandlerCreate()\n')
        h.write('\n')
        h.write('newSurfMesh = chiSurfaceMeshCreate();\n')
        h.write('chiSurfaceMeshImportFromOBJFile(newSurfMesh,"')
        h.write("Mesh/"+cur_objname+'PreMesh.obj')
        h.write('",true)\n')
        h.write('chiSurfaceMeshExportPolyFile(newSurfMesh,"Mesh/')
        h.write(cur_objname+"PreMesh.poly" + '")\n\n')
        h.write('command = "' + tri_exe_path+' "\n')
        h.write('command = command .. "' + \
            pathdir+'/Mesh/'+cur_objname+"PreMesh.poly"+'"\n')
        h.write('os.execute(command)\n')
        h.write('triSurfMesh = chiSurfaceMeshCreate();\n')
        h.write('chiSurfaceMeshImportFromTriangleFiles(triSurfMesh,')
        h.write('"Mesh/' + cur_objname+"PreMesh"+'")\n')
        h.write('\n')
        h.write('chiSurfaceMeshExportToObj(triSurfMesh,"')
        h.write("Mesh/"+cur_objname+'PostMesh.obj')
        h.write('")\n')
        h.close()  
        
        # $$$$$$$$$$$$$$$$$$$$$  Execute ChiTech
        process = subprocess.Popen([pathexe,
            "Mesh/" + cur_objname+"PreMesh.lua"],
            cwd=pathdir,
            stdout=subprocess.PIPE,
            universal_newlines=True)
        process.wait()
        out,err = process.communicate()
        print(out)
        # $$$$$$$$$$$$$$$$$$$$$

        # $$$$$$$$$$$$$$$$$$$$$ Import meshed object
        new_objname = cur_objname+'TriMesh'   
        
        # Delete objects with new_objname
        for obj in scene.objects:
            if (obj.name == new_objname):
                bpy.ops.object.select_all(action='DESELECT')
                bpy.data.objects[new_objname].select_set(True)
                bpy.ops.object.delete(use_global=True)
        
        # Import
        bpy.ops.import_scene.obj(filepath=(pathdir+"/Mesh/"+cur_objname+'PostMesh.obj'),
                                 axis_forward = 'Y',
                                 axis_up      = 'Z')    
                
        # Rename                                       
        bpy.ops.object.select_all(action='DESELECT')
        bpy.ops.object.select_pattern(pattern="ChitechTriMesh*")
        for obj in bpy.context.selected_objects:
            obj.name = new_objname 
            
        # Make object display edges
        bpy.context.view_layer.objects.active = bpy.data.objects[new_objname]
        bpy.data.objects[new_objname].show_all_edges = True

        # Get bound box
        bbox = bpy.data.objects[new_objname].bound_box
        context.scene.chitech_properties.xmin = bbox[0][0]
        context.scene.chitech_properties.ymin = bbox[0][1]  
        context.scene.chitech_properties.xmax = bbox[7][0]
        context.scene.chitech_properties.ymax = bbox[7][1] 
        
        return {"FINISHED"}

def register():
    bpy.utils.register_class(MeshPSLGButton)
   

def unregister():
    bpy.utils.unregister_class(MeshPSLGButton)
   