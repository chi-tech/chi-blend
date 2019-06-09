bl_info = {
    "name": "ChiTech Mesh Operations",
    "author": "Jan Vermaak",
    "category": "ChiTech"
}

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
        
        
        print(bpy.data.objects[new_objname].bound_box[0])
        print(bpy.data.objects[new_objname].bound_box[1])
        print(bpy.data.objects[new_objname].bound_box[2])
        print(bpy.data.objects[new_objname].bound_box[3])
        print(bpy.data.objects[new_objname].dimensions)
        
        loc = bpy.data.objects[new_objname].location
        dim = bpy.data.objects[new_objname].dimensions
        
        #context.scene.chitech_properties.xmin = 
        
        

        #bpy.ops.object.editmode_toggle()
        
        
        return {"FINISHED"}
    
# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
class AddCutLinesButton(bpy.types.Operator):
    bl_label = "Mesh a Planar Straight Line Graph"
    bl_idname = "chitech.addcutsbutton"  
    bl_options = {"UNDO"}
    
    def invoke(self, context, event):
        print("executing")
        
        point1 = [ 0.0, -1.0, 0.0]
        point2 = [ 0.0,  1.0, 0.0]
        mesh = bpy.data.meshes.new("")
        mesh.from_pydata([point1,point2], [[0,1]], [])
        mesh.update()
        
        obj = bpy.data.objects.new("Xcut",mesh)
        context.scene.objects.link(obj)
        
        bpy.ops.object.select_all(action = "DESELECT")
        obj.select = True
        context.scene.objects.active = obj
        bpy.ops.object.mode_set(mode="EDIT")

        return {"FINISHED"}


# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
class ChiTechProperties(bpy.types.PropertyGroup):
    bl_idname = "chitech.properties"
    
    path_to_chitech_exe = bpy.props.StringProperty(default="..",subtype='FILE_PATH')
    path_to_workdir     = bpy.props.StringProperty(default="..",subtype='DIR_PATH')
    current_object      = bpy.props.StringProperty()
    triangle_area       = bpy.props.FloatProperty(min=0.001,step=0.1,default=10.0,precision=3)
    tris_to_quads       = bpy.props.BoolProperty(default=True)
    
    xmin                =-1.0e16
    xmax                = 1.0e16
    ymin                =-1.0e16
    ymax                = 1.0e16
    num_x_cuts          = bpy.props.IntProperty(default=0,min=0,step=1)
    num_y_cuts          = bpy.props.IntProperty(default=0,min=0,step=1)
    x_cuts              = []
    y_cuts              = []


    
    
# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
class LayoutDemoPanel(bpy.types.Panel):
    """Creates a Panel in the scene context of the properties editor"""
    bl_label = "ChiTech Mesh Operations"
    bl_idname = "chitech.panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_context = "objectmode"
    bl_category = "ChiTech"
    
    props=[]

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        
        # Path to executable
        layout.label(text=" Path to ChiTech executable:")
        layout.prop(scene.chitech_properties, 'path_to_chitech_exe',text="")
        
        # Path to working dir
        layout.label(text=" Path to Working Directory:")
        col = layout.column()
        row = col.row(align=True)
        layout.prop(scene.chitech_properties, 'path_to_workdir',text="")
        
        
        layout.row().separator()

        layout.label(text=" Meshing parameters:")
        # Currently selected object
        row = layout.row()
        row.label(text=" Current Object:")
        row.prop_search(scene.chitech_properties, "current_object", scene, "objects",text="")
        
        # Triangle area selector
        row = layout.row(align=True)
        row.label(text=" Max Triangle Area:")
        row.prop(scene.chitech_properties,"triangle_area",text="")
        
        # Triangle-Quads selector
        row = layout.row(align=True)
        row.label(text=" Convert triangles to quads:")
        row.prop(scene.chitech_properties,"tris_to_quads",text="")
        
        layout.row().separator()
        layout.row().separator()
        
        # Mesh PSLG
        #layout.operator("chitech.pslgbutton",text="ja")
        split = layout.split(percentage=0.66)
        col1 = split.column()
        col2 = split.column()
        split1 = col1.split(percentage=0.5)
        col1_1 = split1.column()
        col1_2 = split1.column()
        col1_2.operator("chitech.pslgbutton",text="Mesh PSLG")
        
        layout.operator

        layout.row().separator()
        layout.row().separator()
        
        #Add cuts
        split = layout.split(percentage=0.666)
        col1 = split.column()
        col2 = split.column()
        col1.label(text="Number of X-cuts")
        col2.prop(scene.chitech_properties,"num_x_cuts",text="")
        col1.label(text="Number of Y-cuts")
        col2.prop(scene.chitech_properties,"num_y_cuts",text="")

        layout.row().separator()

        split = layout.split(percentage=0.75)
        col1 = split.column()
        col2 = split.column()
        split1 = col1.split(percentage=(1/3))
        col1_1 = split1.column()
        col1_2 = split1.column()
        col1_2.scale_y = 2.0
        col1_2.operator("chitech.addcutsbutton",text="Generate Cutlines")



def register():
    bpy.utils.register_class(ChiTechProperties)
    bpy.utils.register_class(MeshPSLGButton)
    bpy.utils.register_class(LayoutDemoPanel)
    bpy.utils.register_class(AddCutLinesButton)
    bpy.types.Scene.chitech_properties = bpy.props.PointerProperty(type=ChiTechProperties)
    
    # os.environ.get('PETSC_ROOT')
    if (os.environ.get('CHITECH_ROOT') != None):
        bpy.data.scenes[0].chitech_properties.path_to_chitech_exe = os.environ.get('CHITECH_ROOT')+"ChiTech"
    else:
        bpy.data.scenes[0].chitech_properties.path_to_chitech_exe = ""


def unregister():
    bpy.utils.unregister_class(ChiTechProperties)
    bpy.utils.unregister_class(MeshPSLGButton)
    bpy.utils.unregister_class(LayoutDemoPanel)
    bpy.utils.unregister_class(AddCutLinesButton)



if __name__ == "__main__":
    register()
