bl_info = {
    "name": "ChiTech Mesh Operations",
    "author": "Jan Vermaak",
    "description" : "",
    "blender" : (2, 80, 0),
    "version" : (0, 0, 1),
    "location" : "",
    "warning" : "",
    "category": "ChiTech"
}
modulesNames = ['chi_blend_v0',
                'chi_blend_v0_00_UI',
                'chi_blend_v0_01_PSLG',
                'chi_blend_v0_02a_cuts',
                'chi_blend_v0_02b_cuts',
                'chi_blend_v0_02c_imprintcuts',
                'chi_blend_v0_02d_compstats',
                'chi_blend_v0_02e_exporttrimesh',
                'chi_blend_v0_02f_alignverts',
                'chi_blend_v0_05_extrusion',
                'chi_blend_v0_tools_a']
 
import sys
import importlib
 
modulesFullNames = {}
for currentModuleName in modulesNames:
    if 'DEBUG_MODE' in sys.argv:
        modulesFullNames[currentModuleName] = ('{}'.format(currentModuleName))
    else:
        modulesFullNames[currentModuleName] = ('{}.{}'.format(__name__, currentModuleName))
 
for currentModuleFullName in modulesFullNames.values():
    if currentModuleFullName in sys.modules:
        importlib.reload(sys.modules[currentModuleFullName])
    else:
        globals()[currentModuleFullName] = importlib.import_module(currentModuleFullName)
        setattr(globals()[currentModuleFullName], 'modulesNames', modulesFullNames)
 
def register():
    for currentModuleName in modulesFullNames.values():
        if currentModuleName in sys.modules:
            if hasattr(sys.modules[currentModuleName], 'register'):
                sys.modules[currentModuleName].register()
 
def unregister():
    for currentModuleName in modulesFullNames.values():
        if currentModuleName in sys.modules:
            if hasattr(sys.modules[currentModuleName], 'unregister'):
                sys.modules[currentModuleName].unregister()
 
# if __name__ == "__main__":
#     register()
#register()
# import bpy
# from . chi_blend_v0 import VecDbl

# classes = (chi_blend_v0.VecDbl,
#            chi_blend_v0.VecExtrusionLayer,
#            chi_blend_v0.VecMaterial,
#            chi_blend_v0.ChiTechProperties)

# register, unregister = bpy.utils.register_classes_factory(classes)