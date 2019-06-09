import os
import bpy
from bpy_extras.io_utils import ExportHelper


    
# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
class MeshPSLGButton(bpy.types.Operator):
    bl_label = "Mesh a Planar Straight Line Graph"
    bl_idname = "chitech.pslgbutton"  
    bl_options = {"UNDO"}
    
    def invoke(self, context, event):
        print("executing")
        cur_objname = context.scene.chitech_properties.current_object
        if (cur_objname == ""):
            self.report({'WARNING'},"No object selected")
            return {"FINISHED"}
        
        pathexe = context.scene.chitech_properties.path_to_chitech_exe
        if ((pathexe == "") or (pathexe == "..")):
            self.report({'WARNING'},"ChiTech executable path not set")
            return {"FINISHED"}
        
        pathdir = context.scene.chitech_properties.path_to_workdir
        if ((pathdir == "") or (pathdir == "..")):
            self.report({'WARNING'},"Working directory not set")
            return {"FINISHED"}
        
        scene = context.scene
        bpy.ops.object.select_all(action='DESELECT')
        for obj in scene.objects:
            if (obj.name == cur_objname):
                bpy.data.objects[cur_objname].select = True
                bpy.context.scene.objects.active = bpy.data.objects[cur_objname]
                bpy.ops.export_scene.obj(
                   filepath       = pathdir+"/"+cur_objname+"PreMesh.obj",
                   check_existing = False,
                   axis_forward   = 'Y',
                   axis_up        = 'Z',
                   use_selection  = True,
                   use_materials  = False)
                self.report({'INFO'},"PSLG export to " + pathdir+"/"+cur_objname+"PreMesh.obj")
        
        h = open(pathdir+"/"+cur_objname+"PreMesh.lua",'w')  
        h.write('chiMeshHandlerCreate()\n')
        h.write('\n')
        h.write('newSurfMesh = chiSurfaceMeshCreate();\n')
        h.write('chiSurfaceMeshImportFromOBJFile(newSurfMesh,"')
        h.write(pathdir+"/"+cur_objname+'PreMesh.obj')
        h.write('",true)\n')
        h.write('\n')
        h.write('region1 = chiRegionCreate()\n')
        h.write('chiRegionAddSurfaceBoundary(region1,newSurfMesh);\n')
        h.write('\n')
        h.write('\n')
        h.write('chiSurfaceMesherCreate(SURFACEMESHER_TRIANGLE);\n')
        h.write('chiSurfaceMesherSetProperty(MAX_AREA,')
        h.write(str(context.scene.chitech_properties.triangle_area))
        h.write(')\n')
        h.write('\n')
        h.write('chiSurfaceMesherExecute();\n')
        h.write('\n')
        h.write('chiSurfaceMesherExportToObj("')
        h.write(pathdir+"/"+cur_objname+'PostMesh.obj')
        h.write('")\n')
        h.close()  
        
        print(os.popen(pathexe + ' ' + pathdir+"/"+cur_objname+"PreMesh.lua").read())  
        
        new_objname = cur_objname+'TriMesh'   
        
        for obj in scene.objects:
            if (obj.name == new_objname):
                bpy.ops.object.select_all(action='DESELECT')
                bpy.data.objects[new_objname].select = True
                bpy.ops.object.delete(use_global=True)
        
        bpy.ops.import_scene.obj(filepath=(pathdir+"/"+cur_objname+'PostMesh.obj'),
                                 axis_forward = 'Y',
                                 axis_up      = 'Z')    
                
                                               
        bpy.ops.object.select_all(action='DESELECT')
        bpy.ops.object.select_pattern(pattern="ChitechTriMesh*")
        for obj in bpy.context.selected_objects:
            obj.name = new_objname 
            
        bpy.context.scene.objects.active = bpy.data.objects[new_objname]
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
        
        
        return {"FINISHED"}

def register():
    bpy.utils.register_class(MeshPSLGButton)
   

def unregister():
    bpy.utils.unregister_class(MeshPSLGButton)
   