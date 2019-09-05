import os
import bpy
from bpy_extras.io_utils import ExportHelper
import subprocess


    
# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
class MeshPSLGButton(bpy.types.Operator):
    bl_label = "Mesh a Planar Straight Line Graph"
    bl_idname = "chitech.pslgbutton"  
    bl_options = {"UNDO"}
    
    def invoke(self, context, event):
        chiprops = context.scene.chitech_properties
        
        # Check object selection valid
        cur_objname = context.scene.chitech_properties.current_object
        if (cur_objname == ""):
            self.report({'WARNING'},"No object selected")
            return {"FINISHED"}
        
        # Check ChiTech Path is specified
        pathexe = context.scene.chitech_properties.path_to_chitech_exe
        if ((pathexe == "") or (pathexe == "..")):
            self.report({'WARNING'},"ChiTech executable path not set")
            return {"FINISHED"}

        # Strip the root folder from the path
        binstart = pathexe.find("bin")
        chitech_root = pathexe[0:binstart]
        tri_exe_path = chitech_root+"CHI_RESOURCES/Dependencies/triangle/"
        tri_exe_path += "triangle -pqa"+str(chiprops.triangle_area)
        
        # Check working directory specified
        pathdir = context.scene.chitech_properties.path_to_workdir
        if ((pathdir == "") or (pathdir == "..")):
            self.report({'WARNING'},"Working directory not set")
            return {"FINISHED"}

        # Create Mesh directory
        pathdir = chiprops.path_to_workdir
        if not os.path.exists(pathdir+'/Mesh'):
            os.mkdir(pathdir+'/Mesh')
        
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
        # h.write('region1 = chiRegionCreate()\n')
        # h.write('chiRegionAddSurfaceBoundary(region1,triSurfMesh);\n')
        # h.write('\n')
        # h.write('\n')
        # h.write('chiSurfaceMesherCreate(SURFACEMESHER_TRIANGLE);\n')
        # h.write('chiSurfaceMesherSetProperty(MAX_AREA,')
        # h.write(')\n')
        # h.write('chiSurfaceMesherCreate(SURFACEMESHER_PREDEFINED);\n')

        # h.write('\n')
        # h.write('chiSurfaceMesherExecute();\n')
        # h.write('\n')
        h.write('chiSurfaceMeshExportToObj(triSurfMesh,"')
        h.write("Mesh/"+cur_objname+'PostMesh.obj')
        h.write('")\n')
        h.close()  
        
        # $$$$$$$$$$$$$$$$$$$$$  Execute ChiTech
        #print(os.popen(pathexe + ' ' + pathdir+"/"+cur_objname+"PreMesh.lua").read())  
        process = subprocess.Popen([pathexe,
            "Mesh/" + cur_objname+"PreMesh.lua"],
            cwd=pathdir,
            stdout=subprocess.PIPE,
            universal_newlines=True)
        process.wait()
        out,err = process.communicate()
        print(out)
        # $$$$$$$$$$$$$$$$$$$$$

        new_objname = cur_objname+'TriMesh'   
        
        for obj in scene.objects:
            if (obj.name == new_objname):
                bpy.ops.object.select_all(action='DESELECT')
                bpy.data.objects[new_objname].select_set(True)
                bpy.ops.object.delete(use_global=True)
        
        bpy.ops.import_scene.obj(filepath=(pathdir+"/Mesh/"+cur_objname+'PostMesh.obj'),
                                 axis_forward = 'Y',
                                 axis_up      = 'Z')    
                
                                               
        bpy.ops.object.select_all(action='DESELECT')
        bpy.ops.object.select_pattern(pattern="ChitechTriMesh*")
        for obj in bpy.context.selected_objects:
            obj.name = new_objname 
            
        bpy.context.view_layer.objects.active = bpy.data.objects[new_objname]
        bpy.context.object.show_all_edges = True

        bbox = bpy.data.objects[new_objname].bound_box
        context.scene.chitech_properties.xmin = bbox[0][0]
        context.scene.chitech_properties.ymin = bbox[0][1]  
        context.scene.chitech_properties.xmax = bbox[7][0]
        context.scene.chitech_properties.ymax = bbox[7][1] 

        print(context.scene.chitech_properties.xmin)
        print(context.scene.chitech_properties.xmax)
        print(context.scene.chitech_properties.ymin)
        print(context.scene.chitech_properties.ymax)
        print(len(bpy.data.objects[new_objname].data.vertices))
        print(bpy.data.objects[new_objname].data.polygons[0])

        #bpy.ops.object.editmode_toggle()
        print(tri_exe_path)
        
        return {"FINISHED"}

def register():
    bpy.utils.register_class(MeshPSLGButton)
   

def unregister():
    bpy.utils.unregister_class(MeshPSLGButton)
   