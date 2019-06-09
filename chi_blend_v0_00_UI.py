import os
import bpy
from bpy_extras.io_utils import ExportHelper

    
# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
class ToolsPanel(bpy.types.Panel):
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

        
        # Mesh PSLG
        #layout.operator("chitech.pslgbutton",text="ja")
        split = layout.split(percentage=0.66)
        col1 = split.column()
        col2 = split.column()
        split1 = col1.split(percentage=0.5)
        col1_1 = split1.column()
        col1_2 = split1.column()
        col1_2.operator("chitech.pslgbutton",text="Mesh PSLG")
        
       
# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
class SimpleLoadBalanceMenu(bpy.types.Panel):
    bl_label  = "Simple load balancing tools"
    bl_idname = "chiteh.simpleLB"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_context = "objectmode"
    bl_category = "ChiTech"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self,context):
        layout = self.layout
        scene = context.scene

        #Number of cuts properties
        split = layout.split(percentage=0.666)
        col1 = split.column()
        col2 = split.column()
        col1.label(text="Number of X-cuts")
        col2.prop(scene.chitech_properties,"num_x_cuts",text="")
        col1.label(text="Number of Y-cuts")
        col2.prop(scene.chitech_properties,"num_y_cuts",text="")

        #Load balance factors
        split = layout.split(percentage=0.8)
        col1 = split.column()
        col2 = split.column()
        col1.label(text="Estimated LBF before imprinting: ")
        col2.label(text=str(scene.chitech_properties.load_bal_factor_i))
        col1.label(text="After imprint LBF: ")
        col2.label(text=str(scene.chitech_properties.load_bal_factor_f))

        row = layout.row()
        row.label(text="Live update LBF: ")
        row.prop(scene.chitech_properties,"lbf_live_update",text="")


        # Generate cutlines button
        split = layout.split(percentage=0.75)
        col1 = split.column()
        col2 = split.column()
        split1 = col1.split(percentage=(1/3))
        col1_1 = split1.column()
        col1_2 = split1.column()
        #col1_2.scale_y = 2.0
        col1_2.operator("chitech.addcutsbutton",text="Generate Cutlines")

        # Imprint cutlines button
        split = layout.split(percentage=0.75)
        col1 = split.column()
        col2 = split.column()
        split1 = col1.split(percentage=(1/3))
        col1_1 = split1.column()
        col1_2 = split1.column()
        col1_2.operator("chitech.imprintcutsbutton",text="Imprint Cutlines")

        layout.operator("chitech.exporttemplatebutton",text="Export ChiTech Mesh")
        

# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
class ExtrusionMeshPanel(bpy.types.Panel):
    bl_label  = "Extrusion Mesh tools"
    bl_idname = "chiteh.extrusionmesh"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_context = "objectmode"
    bl_category = "ChiTech"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self,context):
        layout = self.layout
        scene = context.scene
        chiprops = scene.chitech_properties

        # row = layout.row()
        # row.label(text="Number of materials")
        # row.prop(chiprops,"num_materials",text="")

        row = layout.row()
        row.label(text="Materials")
        row.operator("chitech.addmaterial",icon='ZOOMIN',text="")
        row.operator("chitech.removematerial",icon='ZOOMOUT',text="")

        for i in range(0,len(chiprops.materials)):
            material = chiprops.materials[i]
            row = layout.row()
            row.prop(chiprops.materials[i],"name",text="")
            row.label(text="Object Group")
            row.prop(chiprops.materials[i],"object_group",text="")

        row = layout.row()
        row.label(text="Extrusion layers")
        row.operator("chitech.addextrusionlayer",icon='ZOOMIN',text="")
        row.operator("chitech.removeextrusionlayer",icon='ZOOMOUT',text="")

        for i in range(0,len(chiprops.extrusion_layers)):
            ext_layer = chiprops.extrusion_layers[i]
            row = layout.row()
            row.prop(chiprops.extrusion_layers[i],"name",text="")
            row.prop(chiprops.extrusion_layers[i],"height",text="")
            row.prop(chiprops.extrusion_layers[i],"subdivs",text="")

        layout.operator("chitech.generateextrusion",text="Generate Extrusion")
        layout.label(text="Number of cells created: "+\
                      str(chiprops.num_cells_created))

def register():
    bpy.utils.register_class(ToolsPanel)
    bpy.utils.register_class(SimpleLoadBalanceMenu)
    bpy.utils.register_class(ExtrusionMeshPanel)
    

def unregister():
    bpy.utils.unregister_class(ToolsPanel)    
    bpy.utils.unregister_class(SimpleLoadBalanceMenu)    
    bpy.utils.unregister_class(ExtrusionMeshPanel)  