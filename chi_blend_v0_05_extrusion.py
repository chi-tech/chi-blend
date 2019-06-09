import os
import bpy
from bpy_extras.io_utils import ExportHelper
import subprocess

# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
class AddExtrusionLayerButton(bpy.types.Operator):
    bl_label = "Add an extrusion layer"
    bl_idname = "chitech.addextrusionlayer"  
    bl_options = {"UNDO"}

    # ===========================================
    def invoke(self, context, event):
        scene = context.scene
        chiprops = scene.chitech_properties

        new_layer = chiprops.extrusion_layers.add()
        new_layer.name = "Layer " + str(len(chiprops.extrusion_layers))
        
        return {"FINISHED"}

# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
class RemoveExtrusionLayerButton(bpy.types.Operator):
    bl_label = "Remove an extrusion layer"
    bl_idname = "chitech.removeextrusionlayer"  
    bl_options = {"UNDO"}

    # ===========================================
    def invoke(self, context, event):
        scene = context.scene
        chiprops = scene.chitech_properties

        chiprops.extrusion_layers.remove(len(chiprops.extrusion_layers)-1)
        
        return {"FINISHED"}

# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
class AddMaterialButton(bpy.types.Operator):
    bl_label = "Add a material"
    bl_idname = "chitech.addmaterial"  
    bl_options = {"UNDO"}

    # ===========================================
    def invoke(self, context, event):
        scene = context.scene
        chiprops = scene.chitech_properties

        new_mat = chiprops.materials.add()
        new_mat.name = "Material " + str(len(chiprops.materials))
        
        return {"FINISHED"}

# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
class RemoveMaterialButton(bpy.types.Operator):
    bl_label = "Remove a material"
    bl_idname = "chitech.removematerial"  
    bl_options = {"UNDO"}

    # ===========================================
    def invoke(self, context, event):
        scene = context.scene
        chiprops = scene.chitech_properties

        chiprops.materials.remove(len(chiprops.materials)-1)
        
        return {"FINISHED"}

# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
class GenerateExtrusion(bpy.types.Operator):
    bl_label = "Generate extruded mesh"
    bl_idname = "chitech.generateextrusion"  
    bl_options = {"UNDO"}

    # ===========================================
    def invoke(self, context, event):
        print("Executing extrusion")
        chiprops = context.scene.chitech_properties

        if (len(chiprops.extrusion_layers) == 0):
            self.report({'WARNING'},"No layers specified")
            return {"FINISHED"}

        # Create Mesh directory
        pathdir = chiprops.path_to_workdir
        if not os.path.exists(pathdir+'/Mesh'):
            os.mkdir(pathdir+'/Mesh')

        # Re-export TriMesh as SurfaceMesh
        cur_objname = chiprops.current_object
        bpy.ops.object.select_all(action='DESELECT')
        bpy.ops.object.select_pattern(pattern="*TriMesh*")
        bpy.context.scene.objects.active = \
            bpy.data.objects[cur_objname+"TriMesh"]
        bpy.ops.export_scene.obj(
                   filepath       = pathdir + "/Mesh/" + \
                       cur_objname+"SurfaceMesh.obj",
                   check_existing = False,
                   axis_forward   = 'Y',
                   axis_up        = 'Z',
                   use_selection  = True,
                   use_materials  = False)

        # Export all logical volumes
        for m in range(0,len(chiprops.materials)):
            mater = chiprops.materials[m]
            grp   = mater.object_group

            print(grp.name)
            grp_data = bpy.data.groups[grp.name]
            for obj in grp_data.objects:
                print(obj.name)
                bpy.ops.object.select_all(action='DESELECT')
                bpy.data.objects[obj.name].select = True
                bpy.ops.export_scene.obj(
                   filepath       = pathdir + "/Mesh/" + \
                       "LV_" + obj.name + ".obj",
                   check_existing = False,
                   axis_forward   = 'Y',
                   axis_up        = 'Z',
                   use_selection  = True,
                   use_materials  = False,
                   use_triangles  = True )


        # Generate ChiTech inputs for extrusion
        h = open(pathdir+"/Mesh/"+cur_objname+"Extrusion.lua",'w')  
        h.write('chiMeshHandlerCreate()\n')
        h.write('\n')
        h.write('newSurfMesh = chiSurfaceMeshCreate();\n')
        h.write('chiSurfaceMeshImportFromOBJFile(newSurfMesh,"')
        #h.write(pathdir+"/"+cur_objname+'SurfaceMesh.obj')
        h.write("Mesh/" + cur_objname+'SurfaceMesh.obj')
        h.write('",true)\n')
        h.write('\n')
        h.write('region1 = chiRegionCreate()\n')
        h.write('chiRegionAddSurfaceBoundary(region1,newSurfMesh);\n')
        h.write('\n')
        h.write('\n')
        h.write('chiSurfaceMesherCreate(SURFACEMESHER_PREDEFINED);\n')
        for xcuts in chiprops.x_cuts:
            h.write('chiSurfaceMesherSetProperty(CUT_X,')
            h.write(str(xcuts.value)+')\n')

        h.write('chiSurfaceMesherExecute();\n')
        h.write('\n')
        h.write('chiVolumeMesherCreate(VOLUMEMESHER_EXTRUDER);\n')
        
        for i in range(0,len(chiprops.extrusion_layers)):
            exlayer = chiprops.extrusion_layers[i]
            h.write('chiVolumeMesherSetProperty(EXTRUSION_LAYER,')
            h.write(str(exlayer.height)+',')
            h.write(str(exlayer.subdivs)+',"') 
            h.write(exlayer.name+'");\n')      

        h.write('\n')
        h.write('chiVolumeMesherSetProperty(FORCE_POLYGONS,true);\n')
        h.write('chiVolumeMesherExecute();\n\n')
        
        # Write material logical volumes surfaces init
        h.write('\n')
        lv_count=-1
        for m in range(0,len(chiprops.materials)):
            mater = chiprops.materials[m]
            grp   = mater.object_group

            grp_data = bpy.data.groups[grp.name]
            for obj in grp_data.objects:
                lv_count+=1
                h.write('surf_lv'+str(lv_count) + " = chiSurfaceMeshCreate();\n")
                

        # Write material logical volumes surfaces
        h.write('\n')
        lv_count=-1
        for m in range(0,len(chiprops.materials)):
            mater = chiprops.materials[m]
            grp   = mater.object_group

            grp_data = bpy.data.groups[grp.name]
            for obj in grp_data.objects:
                lv_count+=1
                h.write('chiSurfaceMeshImportFromOBJFile(')
                h.write('surf_lv'+str(lv_count)+',"')
                h.write("Mesh/LV_" + obj.name + '.obj")\n') 

        # Write material logical volumes creation
        h.write('\n')
        lv_count=-1
        for m in range(0,len(chiprops.materials)):
            mater = chiprops.materials[m]
            grp   = mater.object_group

            grp_data = bpy.data.groups[grp.name]
            for obj in grp_data.objects:
                lv_count+=1
                h.write('vol_lv'+str(lv_count)+' = ')
                h.write('chiLogicalVolumeCreate(SURFACE,')
                h.write('surf_lv'+str(lv_count)+')\n') 

        # Write material logical volumes executions
        h.write('\n')
        lv_count=-1
        for m in range(0,len(chiprops.materials)):
            mater = chiprops.materials[m]
            grp   = mater.object_group

            grp_data = bpy.data.groups[grp.name]
            for obj in grp_data.objects:
                lv_count+=1
                h.write('chiVolumeMesherSetProperty(')
                h.write('MATID_FROMLOGICAL,')
                h.write('vol_lv'+str(lv_count)+','+str(m)+')\n')

        # Write material creation
        h.write('\n')
        for m in range(0,len(chiprops.materials)):
            mater = chiprops.materials[m]
            h.write('chiPhysicsAddMaterial("')
            h.write(mater.name + '")\n')
        

        h.write('\n')
        if (len(chiprops.materials) == 0):
            h.write('chiRegionExportMeshToObj(region1,"')
            h.write("Mesh/" + cur_objname+'_VM.obj",false)\n')
        else:
            h.write('chiRegionExportMeshToObj(region1,"')
            h.write("Mesh/" + cur_objname+'_VM.obj",false)\n')
            h.write('chiRegionExportMeshToObj(region1,"')
            h.write("Mesh/" + cur_objname+'_VM.obj",true)\n')
        h.close()  

        # $$$$$$$$$$$$$$$$$$$$$  Execute ChiTech
        pathexe = chiprops.path_to_chitech_exe

        process = subprocess.Popen([pathexe,
            "Mesh/" + cur_objname+"Extrusion.lua"],
            cwd=pathdir,
            stdout=subprocess.PIPE,
            universal_newlines=True)
        process.wait()
        out,err = process.communicate()
        print(out)
        cell_start = out.find('Number of cells in region = ')
        cell_end   = out.find('\n',cell_start)
        num_cell = int(out[(cell_start+27):cell_end])
        chiprops.num_cells_created = num_cell
        print("Chitech executed")
        
        # $$$$$$$$$$$$$$$$$$$$$

        # Delete previous renditions
        bpy.ops.object.select_all(action='DESELECT')
        bpy.ops.object.select_pattern(pattern="*_VM*")
        bpy.ops.object.delete(use_global=True)

        # Import base extruded mesh
        bpy.ops.import_scene.obj(filepath=pathdir+"/Mesh/"+\
                                cur_objname+'_VM.obj',
                                axis_forward = 'Y',
                                axis_up      = 'Z')

        bpy.ops.object.select_all(action='DESELECT')
        bpy.ops.object.select_pattern(pattern="*_VM*")
        for obj in bpy.context.selected_objects:
            obj.name = cur_objname+'_VM'
        
        bpy.context.scene.objects.active = \
            bpy.data.objects[cur_objname+'_VM']
        bpy.context.object.show_all_edges = True
        bpy.context.object.show_wire = True

        # Import individual material meshes
        if (len(chiprops.materials) != 0):
            for m in range(0,len(chiprops.materials)):
                bpy.ops.import_scene.obj(filepath=pathdir+"/Mesh/"+\
                                    cur_objname+'_VM_m' + \
                                    str(m) + '.obj',
                                    axis_forward = 'Y',
                                    axis_up      = 'Z')

                bpy.ops.object.select_all(action='DESELECT')
                pat = '*_VM_m' + str(m) + '*'
                print(pat)
                bpy.ops.object.select_pattern(pattern='*_VM_m' + str(m) + '*')
                for obj in bpy.context.selected_objects:
                    obj.name = cur_objname+'_VM_m' + str(m)

            
                bpy.context.scene.objects.active = \
                    bpy.data.objects[cur_objname+'_VM_m'+str(m)]
                bpy.context.object.show_all_edges = True
                bpy.context.object.show_wire = True    
        
        return {"FINISHED"}

def register():
    bpy.utils.register_class(AddExtrusionLayerButton)
    bpy.utils.register_class(RemoveExtrusionLayerButton)
    bpy.utils.register_class(AddMaterialButton)
    bpy.utils.register_class(RemoveMaterialButton)
    bpy.utils.register_class(GenerateExtrusion)
  
def unregister():
    bpy.utils.unregister_class(AddExtrusionLayerButton)
    bpy.utils.unregister_class(RemoveExtrusionLayerButton)
    bpy.utils.unregister_class(AddMaterialButton)
    bpy.utils.unregister_class(RemoveMaterialButton)
    bpy.utils.unregister_class(GenerateExtrusion)