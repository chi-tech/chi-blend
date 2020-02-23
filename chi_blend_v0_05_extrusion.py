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

        in_pnt = chiprops.layer_insert_before
        num_layers = len(chiprops.extrusion_layers)
        # if (chiprops.layer_insert_before<len(chiprops.extrusion_layers)):
        #     new_layer = chiprops.extrusion_layers.add()
        #     last_num = -1
        #     for i in range(chiprops.layer_insert_before,num_layers+1):
        #         chiprops.extrusion_layers.move(i,i+1)
        #         last_num = i+1
        #     chiprops.extrusion_layers.move(last_num,in_pnt)
            
        # else:
        #     new_layer = chiprops.extrusion_layers.add()
        new_layer = chiprops.extrusion_layers.add()
        new_layer.name = "Layer"

        if in_pnt>=0:
            chiprops.extrusion_layers.move(num_layers,in_pnt)
        
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

        in_pnt = chiprops.layer_insert_before
        if in_pnt>=0:
            chiprops.extrusion_layers.remove(chiprops.layer_insert_before)
        else:
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
        bpy.context.view_layer.objects.active = \
            bpy.data.objects[cur_objname+"TriMesh"]
        bpy.ops.export_scene.obj(
                   filepath       = pathdir + "/Mesh/" + \
                       cur_objname+"SurfaceMesh.obj",
                   check_existing = False,
                   axis_forward   = 'Y',
                   axis_up        = 'Z',
                   use_selection  = True,
                   use_materials  = False)

        # Unhide all logical volumes
        for m in range(0,len(chiprops.materials)):
            mater = chiprops.materials[m]
            grp   = mater.object_group

            grp_data = bpy.data.collections[grp.name]
            for obj in grp_data.objects:
                bpy.data.objects[obj.name].hide_set(False)

        # Export all logical volumes
        for m in range(0,len(chiprops.materials)):
            mater = chiprops.materials[m]
            grp   = mater.object_group

            grp_data = bpy.data.collections[grp.name]
            for obj in grp_data.objects:
                bpy.ops.object.select_all(action='DESELECT')
                bpy.data.objects[obj.name].select_set(True)
                bpy.ops.export_scene.obj(
                   filepath       = pathdir + "/Mesh/" + \
                       "LV_" + obj.name + ".obj",
                   check_existing = False,
                   axis_forward   = 'Y',
                   axis_up        = 'Z',
                   use_selection  = True,
                   use_materials  = False,
                   use_triangles  = True )

        # Hide all logical volumes
        for m in range(0,len(chiprops.materials)):
            mater = chiprops.materials[m]
            grp   = mater.object_group

            grp_data = bpy.data.collections[grp.name]
            for obj in grp_data.objects:
                bpy.data.objects[obj.name].hide_set(True)

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
        h.write('\n')
        for ycuts in chiprops.y_cuts:
            h.write('chiSurfaceMesherSetProperty(CUT_Y,')
            h.write(str(ycuts.value)+')\n')

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

            grp_data = bpy.data.collections[grp.name]
            for obj in grp_data.objects:
                lv_count+=1
                h.write('surf_lv'+str(lv_count) + " = chiSurfaceMeshCreate();\n")
                

        # Write material logical volumes surfaces
        h.write('\n')
        lv_count=-1
        for m in range(0,len(chiprops.materials)):
            mater = chiprops.materials[m]
            grp   = mater.object_group

            grp_data = bpy.data.collections[grp.name]
            for obj in grp_data.objects:
                lv_count+=1
                h.write('chiSurfaceMeshImportFromOBJFile(')
                h.write('surf_lv'+str(lv_count)+',"')
                h.write("Mesh/LV_" + obj.name + '.obj",false)\n') 

        # Write material logical volumes creation
        h.write('\n')
        lv_count=-1
        for m in range(0,len(chiprops.materials)):
            mater = chiprops.materials[m]
            grp   = mater.object_group

            grp_data = bpy.data.collections[grp.name]
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

            grp_data = bpy.data.collections[grp.name]
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
        h.write('chiRegionExportMeshToVTK(region1,"Z_VTK_Mesh")')
        h.close()  

        # $$$$$$$$$$$$$$$$$$$$$  Execute ChiTech
        pathexe = chiprops.path_to_chitech_exe
        print("RUNNING CHITECH")
        process = subprocess.Popen([pathexe,
            "Mesh/" + cur_objname+"Extrusion.lua"],
            cwd=pathdir,
            stdout=subprocess.PIPE,
            universal_newlines=True)
        process.wait()
        out,err = process.communicate()
        print(out)

        # Extracting number of layers generated
        cell_start = out.find('Total number of cell layers is')
        cell_end   = out.find('\n',cell_start)
        num_lay = int(out[(cell_start+30):cell_end])
        chiprops.num_layers_created = num_lay

        # Extracting number of cells generated
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
        
        bpy.context.view_layer.objects.active = \
            bpy.data.objects[cur_objname+'_VM']
        bpy.data.objects[cur_objname+'_VM'].show_all_edges = True
        bpy.data.objects[cur_objname+'_VM'].show_wire = True

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

            
                bpy.context.view_layer.objects.active = \
                    bpy.data.objects[cur_objname+'_VM_m'+str(m)]
                bpy.data.objects[cur_objname+'_VM_m'+str(m)].show_all_edges = True
                bpy.data.objects[cur_objname+'_VM_m'+str(m)].show_wire = True    
        
        return {"FINISHED"}

# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
class ExportExtrusion(bpy.types.Operator):
    bl_label = "Generate extruded mesh"
    bl_idname = "chitech.exportextrusion"  
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

        cur_objname = chiprops.current_object

        # Generate ChiTech inputs for extrusion
        h = open(pathdir+"/Mesh/"+"Mesh.lua",'w')  
        h.write('chiMeshHandlerCreate()\n')
        h.write('\n')
        h.write('newSurfMesh = chiSurfaceMeshCreate();\n')
        h.write('chiSurfaceMeshImportFromOBJFile(newSurfMesh,"')
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
        h.write('\n')
        for ycuts in chiprops.y_cuts:
            h.write('chiSurfaceMesherSetProperty(CUT_Y,')
            h.write(str(ycuts.value)+')\n')

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
        h.write('\n')
        h.write('chiSurfaceMesherSetProperty(PARTITION_X,CHI_PX)\n')
        h.write('chiSurfaceMesherSetProperty(PARTITION_Y,CHI_PY)\n')
        h.write('chiVolumeMesherSetProperty(PARTITION_Z,CHI_PZ)\n')
        h.write('\n')
        h.write('chiVolumeMesherExecute()\n')
        
        # Write material logical volumes surfaces init
        h.write('\n')
        lv_count=-1
        for m in range(0,len(chiprops.materials)):
            mater = chiprops.materials[m]
            grp   = mater.object_group

            grp_data = bpy.data.collections[grp.name]
            for obj in grp_data.objects:
                lv_count+=1
                h.write('surf_lv'+str(lv_count) + " = chiSurfaceMeshCreate();\n")
                

        # Write material logical volumes surfaces
        h.write('\n')
        lv_count=-1
        for m in range(0,len(chiprops.materials)):
            mater = chiprops.materials[m]
            grp   = mater.object_group

            grp_data = bpy.data.collections[grp.name]
            for obj in grp_data.objects:
                lv_count+=1
                h.write('chiSurfaceMeshImportFromOBJFile(')
                h.write('surf_lv'+str(lv_count)+',"')
                h.write("Mesh/LV_" + obj.name + '.obj",false)\n') 

        # Write material logical volumes creation
        h.write('\n')
        lv_count=-1
        for m in range(0,len(chiprops.materials)):
            mater = chiprops.materials[m]
            grp   = mater.object_group

            grp_data = bpy.data.collections[grp.name]
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

            grp_data = bpy.data.collections[grp.name]
            for obj in grp_data.objects:
                lv_count+=1
                h.write('chiVolumeMesherSetProperty(')
                h.write('MATID_FROMLOGICAL,')
                h.write('vol_lv'+str(lv_count)+','+str(m)+')\n')

        # Write material creation
        h.write('\n')
        h.write('materials = {}\n')
        for m in range(0,len(chiprops.materials)):
            mater = chiprops.materials[m]
            h.write('materials['+str(m+1)+'] = ')
            h.write('chiPhysicsAddMaterial("')
            h.write(mater.name + '")\n')
        
  
        
        return {"FINISHED"}

def register():
    bpy.utils.register_class(AddExtrusionLayerButton)
    bpy.utils.register_class(RemoveExtrusionLayerButton)
    bpy.utils.register_class(AddMaterialButton)
    bpy.utils.register_class(RemoveMaterialButton)
    bpy.utils.register_class(GenerateExtrusion)
    bpy.utils.register_class(ExportExtrusion)
  
def unregister():
    bpy.utils.unregister_class(AddExtrusionLayerButton)
    bpy.utils.unregister_class(RemoveExtrusionLayerButton)
    bpy.utils.unregister_class(AddMaterialButton)
    bpy.utils.unregister_class(RemoveMaterialButton)
    bpy.utils.unregister_class(GenerateExtrusion)
    bpy.utils.unregister_class(ExportExtrusion)