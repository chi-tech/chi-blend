import os
import bpy
from bpy_extras.io_utils import ExportHelper

# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# This is blender's implementation of a std::vector<double>
# Values are added to it using .add()
# The vector is cleared using .clear()
class VecDbl(bpy.types.PropertyGroup):
    value = bpy.props.FloatProperty(default=-1.0e16)

# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# Same as above but holds information on an extrusion layer
class VecExtrusionLayer(bpy.types.PropertyGroup):
    name   = bpy.props.StringProperty(default="")
    height = bpy.props.FloatProperty(default=1.0,min=0.000001)
    subdivs= bpy.props.IntProperty(default=1,min=1,step=1)

# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# Same as above but holds information on materials
class VecMaterial(bpy.types.PropertyGroup):
    name         = bpy.props.StringProperty(default="")
    object_group = bpy.props.PointerProperty(type=bpy.types.Collection)
   
    
# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# This is the main data structure that gets loaded onto the 
# blender context. It will always be available via
# context.scene.chitech_properties
class ChiTechProperties(bpy.types.PropertyGroup):
    bl_idname = "chitech.properties"
    
    path_to_chitech_exe = bpy.props.StringProperty(default="..",subtype='FILE_PATH')
    path_to_workdir     = bpy.props.StringProperty(default="..",subtype='DIR_PATH')
    current_object      = bpy.props.StringProperty()
    triangle_area       = bpy.props.FloatProperty(min=0.001,step=0.1,default=10.0,precision=3)
    tris_to_quads       = bpy.props.BoolProperty(default=True)
    
    xmin                = bpy.props.FloatProperty(default=-1.0e16)
    xmax                = bpy.props.FloatProperty(default=1.0e16)
    ymin                = bpy.props.FloatProperty(default=-1.0e16)
    ymax                = bpy.props.FloatProperty(default=1.0e16)
    num_x_cuts          = bpy.props.IntProperty(default=0,min=0,step=1)
    num_y_cuts          = bpy.props.IntProperty(default=0,min=0,step=1)

    x_cuts = bpy.props.CollectionProperty(type=VecDbl)
    y_cuts = bpy.props.CollectionProperty(type=VecDbl)

    load_bal_factor_i   = bpy.props.FloatProperty(default=1.0,precision=3)
    load_bal_factor_f   = bpy.props.FloatProperty(default=1.0,precision=3)
    lbf_live_update     = bpy.props.BoolProperty(default=False)

    extrusion_layers    = bpy.props.CollectionProperty(type=VecExtrusionLayer)
    num_materials       = bpy.props.IntProperty(default=0,min=0,step=1)
    layer_insert_before = bpy.props.IntProperty(default=-1,min=-1,step=1)

    materials           = bpy.props.CollectionProperty(type=VecMaterial)
    num_layers_created  = bpy.props.IntProperty(default=0)
    num_cells_created   = bpy.props.IntProperty(default=0)


def register():
    bpy.utils.register_class(VecDbl)
    bpy.utils.register_class(VecExtrusionLayer)
    bpy.utils.register_class(VecMaterial)
    bpy.utils.register_class(ChiTechProperties)
    
    bpy.types.Scene.chitech_properties = bpy.props.PointerProperty(type=ChiTechProperties)

    

    # if (os.environ.get('CHITECH_ROOT') != None):
    #     bpy.data.scenes[0].chitech_properties.path_to_chitech_exe = os.environ.get('CHITECH_ROOT')+"ChiTech"
    # else:
    #     bpy.data.scenes[0].chitech_properties.path_to_chitech_exe = ""
  
    

def unregister():
    bpy.utils.unregister_class(VecDbl)
    bpy.utils.unregister_class(VecExtrusionLayer)
    bpy.utils.unregister_class(VecMaterial)
    bpy.utils.unregister_class(ChiTechProperties)
    


if __name__ == "__main__":
    register()
