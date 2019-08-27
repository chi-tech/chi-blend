import os
import bpy
from bpy_extras.io_utils import ExportHelper
import mathutils
import subprocess

    
# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
class AddCutLinesButton(bpy.types.Operator):
    bl_label = "Mesh a Planar Straight Line Graph"
    bl_idname = "chitech.addcutsbutton"  
    bl_options = {"UNDO"}
    already_invoked = False

    def CreateXCuts(self,chiprops,context):
        newCol = bpy.data.collections.get('X_cuts')
        if newCol == None:
            newCol = bpy.data.collections.new('X_cuts')
            masterCol = bpy.data.collections[0]
            masterCol.children.link(newCol)
        for i in range(0,chiprops.num_x_cuts):
            d = 0.1*(chiprops.ymax-chiprops.ymin)
            dmin = chiprops.ymin-d
            dmax = chiprops.ymax+d
            f = chiprops.x_cuts[i].value
            #print("Xcut %d = %g" %(i,chiprops.x_cuts[i].value))
            point1 = [ f, dmin, 0.0]
            point2 = [ f, dmax, 0.0]
            mesh = bpy.data.meshes.new("")
            mesh.from_pydata([point1,point2], [[0,1]], [])
            mesh.update()
            
            obj = bpy.data.objects.new("Xcut"+str(i),mesh)
            new_origin = mathutils.Vector((f,dmin,0.0))
            obj.data.transform(mathutils.Matrix.Translation(-new_origin))
            obj.matrix_world.translation += new_origin
 
            newCol.objects.link(obj)

            obj.select_set(True)
            #context.scene.objects.active = obj
            #bpy.ops.object.mode_set(mode="EDIT")

    def CreateYCuts(self,chiprops,context):
        newCol = bpy.data.collections.get('Y_cuts')
        if newCol == None:
            newCol = bpy.data.collections.new('Y_cuts')
            masterCol = bpy.data.collections[0]
            masterCol.children.link(newCol)
        for i in range(0,chiprops.num_y_cuts):
            d = 0.1*(chiprops.xmax-chiprops.xmin)
            dmin = chiprops.xmin-d
            dmax = chiprops.xmax+d
            f = chiprops.y_cuts[i].value
            print("Xcut %d = %g" %(i,chiprops.x_cuts[i].value))
            point1 = [ dmin, f, 0.0]
            point2 = [ dmax, f, 0.0]
            mesh = bpy.data.meshes.new("")
            mesh.from_pydata([point1,point2], [[0,1]], [])
            mesh.update()
            
            obj = bpy.data.objects.new("Ycut"+str(i),mesh)
            new_origin = mathutils.Vector((dmin,f,0.0))
            obj.data.transform(mathutils.Matrix.Translation(-new_origin))
            obj.matrix_world.translation += new_origin
            # context.scene.objects.link(obj)
            newCol.objects.link(obj)
            
            #bpy.ops.object.select_all(action = "DESELECT")
            obj.select_set(True)
            #context.scene.objects.active = obj
            #bpy.ops.object.mode_set(mode="EDIT")
    
    # ===========================================
    def invoke(self, context, event):
        print("executing")
        chiprops = context.scene.chitech_properties

        if ((chiprops.num_x_cuts == 0) and \
            (chiprops.num_y_cuts == 0)):
            self.report({'WARNING'},"No cuts specified")
            return {"FINISHED"}

        # =============== Clear all x and y cuts
        chiprops.x_cuts.clear()
        chiprops.y_cuts.clear()

        # ============== Get selection bound box
        bbox = bpy.data.objects[chiprops.current_object+"TriMesh"].bound_box
        scale = bpy.data.objects[chiprops.current_object+"TriMesh"].scale
        location = bpy.data.objects[chiprops.current_object+"TriMesh"].location
        context.scene.chitech_properties.xmin = bbox[0][0]*scale[0]+location[0]
        context.scene.chitech_properties.ymin = bbox[0][1]*scale[1]+location[1]
        context.scene.chitech_properties.xmax = bbox[7][0]*scale[0]+location[0]
        context.scene.chitech_properties.ymax = bbox[7][1]*scale[1]+location[1]

        # ============== Delete existing objects
        bpy.ops.object.select_all(action='DESELECT')
        bpy.ops.object.select_pattern(pattern="Xcut*")
        bpy.ops.object.delete(use_global=True)
        bpy.ops.object.select_all(action='DESELECT')
        bpy.ops.object.select_pattern(pattern="Ycut*")
        bpy.ops.object.delete(use_global=True)
            

           
        # ============== Create new x-cuts
        if (chiprops.num_x_cuts != 0):
            dx = (chiprops.xmax - chiprops.xmin)/(chiprops.num_x_cuts+1)

            for i in range(0,chiprops.num_x_cuts):
                new_cut = chiprops.x_cuts.add()
                new_cut.value = chiprops.xmin + (i+1)*dx
            self.CreateXCuts(chiprops,context) 

        # ============== Create new y-cuts
        if (chiprops.num_y_cuts != 0):
            dy = (chiprops.ymax - chiprops.ymin)/(chiprops.num_y_cuts+1)

            for i in range(0,chiprops.num_y_cuts):
                new_cut = chiprops.y_cuts.add()
                new_cut.value = chiprops.ymin + (i+1)*dy
            self.CreateYCuts(chiprops,context) 

        lbf = context.scene.chiutilsA.ComputeLBF(context)
        chiprops.load_bal_factor_i = lbf

        if (not self.already_invoked):
            self.already_invoked = True
            print("Event handler started")
            context.window_manager.modal_handler_add(self)

        return {'RUNNING_MODAL'}

    # ======================================
    def modal(self, context, event):
        chiprops = context.scene.chitech_properties

        if (chiprops.lbf_live_update):
            #if (event.type == 'MOUSEMOVE'):
                lbf = context.scene.chiutilsA.ComputeLBF(context)
                chiprops.load_bal_factor_i = lbf
                for region in context.area.regions:
                    if region.type == "TOOLS":
                        region.tag_redraw()
        

        if event.type == 'ESC':
            print("Finished")
            return {'CANCELLED'}  
       
        return {'PASS_THROUGH'}

# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
class AddBalancedCutLinesButton(bpy.types.Operator):
    bl_label = "Mesh a Planar Straight Line Graph"
    bl_idname = "chitech.addbalcutsbutton"  
    bl_options = {"UNDO"}
    already_invoked = False

    def CreateXCuts(self,chiprops,context):
        newCol = bpy.data.collections.get('X_cuts')
        if newCol == None:
            newCol = bpy.data.collections.new('X_cuts')
            masterCol = bpy.data.collections[0]
            masterCol.children.link(newCol)
        for i in range(0,chiprops.num_x_cuts):
            d = 0.1*(chiprops.ymax-chiprops.ymin)
            dmin = chiprops.ymin-d
            dmax = chiprops.ymax+d
            f = chiprops.x_cuts[i].value
            #print("Xcut %d = %g" %(i,chiprops.x_cuts[i].value))
            point1 = [ f, dmin, 0.0]
            point2 = [ f, dmax, 0.0]
            print(point1)
            print(point2)
            mesh = bpy.data.meshes.new("")
            mesh.from_pydata([point1,point2], [[0,1]], [])
            mesh.update()
            
            obj = bpy.data.objects.new("Xcut"+str(i),mesh)
            new_origin = mathutils.Vector((f,dmin,0.0))
            obj.data.transform(mathutils.Matrix.Translation(-new_origin))
            obj.matrix_world.translation += new_origin
            newCol.objects.link(obj)

            obj.select_set(True)
            #bpy.ops.object.mode_set(mode="EDIT")

    def CreateYCuts(self,chiprops,context):
        newCol = bpy.data.collections.get('Y_cuts')
        if newCol == None:
            newCol = bpy.data.collections.new('Y_cuts')
            masterCol = bpy.data.collections[0]
            masterCol.children.link(newCol)
        for i in range(0,chiprops.num_y_cuts):
            d = 0.1*(chiprops.xmax-chiprops.xmin)
            dmin = chiprops.xmin-d
            dmax = chiprops.xmax+d
            f = chiprops.y_cuts[i].value
            #print("Xcut %d = %g" %(i,chiprops.x_cuts[i].value))
            point1 = [ dmin, f, 0.0]
            point2 = [ dmax, f, 0.0]
            mesh = bpy.data.meshes.new("")
            mesh.from_pydata([point1,point2], [[0,1]], [])
            mesh.update()
            
            obj = bpy.data.objects.new("Ycut"+str(i),mesh)
            new_origin = mathutils.Vector((dmin,f,0.0))
            obj.data.transform(mathutils.Matrix.Translation(-new_origin))
            obj.matrix_world.translation += new_origin
            newCol.objects.link(obj)

            obj.select_set(True)
            #bpy.ops.object.mode_set(mode="EDIT")

    # ===========================================
    def invoke(self, context, event):
        print("executing balanced cutlines button")
        chiprops = context.scene.chitech_properties

        if ((chiprops.num_x_cuts == 0) and \
            (chiprops.num_y_cuts == 0)):
            self.report({'WARNING'},"No cuts specified")
            #return {"FINISHED"}

         # =============== Clear all x and y cuts
        chiprops.x_cuts.clear()
        chiprops.y_cuts.clear()

        # ============== Get selection bound box
        bbox = bpy.data.objects[chiprops.current_object+"TriMesh"].bound_box
        scale = bpy.data.objects[chiprops.current_object+"TriMesh"].scale
        location = bpy.data.objects[chiprops.current_object+"TriMesh"].location
        context.scene.chitech_properties.xmin = bbox[0][0]*scale[0]+location[0]
        context.scene.chitech_properties.ymin = bbox[0][1]*scale[1]+location[1]
        context.scene.chitech_properties.xmax = bbox[7][0]*scale[0]+location[0]
        context.scene.chitech_properties.ymax = bbox[7][1]*scale[1]+location[1]

        # ============== Delete existing objects
        bpy.ops.object.select_all(action='DESELECT')
        bpy.ops.object.select_pattern(pattern="Xcut*")
        bpy.ops.object.delete(use_global=True)
        bpy.ops.object.select_all(action='DESELECT')
        bpy.ops.object.select_pattern(pattern="Ycut*")
        bpy.ops.object.delete(use_global=True)

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
            if (obj.name == (cur_objname+"TriMesh")):
                bpy.data.objects[cur_objname+"TriMesh"].select_set(True)
                bpy.context.view_layer.objects.active = bpy.data.objects[cur_objname+"TriMesh"]
                bpy.ops.export_scene.obj(
                   filepath       = pathdir+"/Mesh/"+cur_objname+"BalancedCuts.obj",
                   check_existing = False,
                   axis_forward   = 'Y',
                   axis_up        = 'Z',
                   use_selection  = True,
                   use_materials  = False)
                self.report({'INFO'},"PSLG export to " + pathdir+"/"+cur_objname+"BalancedCuts.obj")
        
        h = open(pathdir+"/Mesh/"+cur_objname+"BalancedCuts.lua",'w')  
        h.write('chiMeshHandlerCreate()\n')
        h.write('\n')
        h.write('newSurfMesh = chiSurfaceMeshCreate();\n')
        h.write('chiSurfaceMeshImportFromOBJFile(newSurfMesh,"')
        h.write("Mesh/"+cur_objname+'BalancedCuts.obj')
        h.write('",true)\n')
        h.write('chiDecomposeSurfaceMeshPxPy(newSurfMesh,'+str(chiprops.num_x_cuts+1)+
               ',' + str(chiprops.num_y_cuts+1) + ')\n')
        h.close()  

        # $$$$$$$$$$$$$$$$$$$$$  Execute ChiTech
        process = subprocess.Popen([pathexe,
            "Mesh/" + cur_objname+"BalancedCuts.lua"],
            cwd=pathdir,
            stdout=subprocess.PIPE,
            universal_newlines=True)
        process.wait()
        out,err = process.communicate()
        print(out)

        # Extract x and y cut values
        cell_start = out.find('Number of cells in region = ')
        cell_end   = out.find('\n',cell_start)

        # ============== Create new x-cuts
        if (chiprops.num_x_cuts != 0):
            for i in range(0,chiprops.num_x_cuts):
                cut_start = out.find('X-cut'+str(i)+' ')
                cut_mid   = out.find(' ',cut_start)
                cut_end   = out.find('\n',cut_start)
                print(out[cut_mid:cut_end])
                cut_value = float(out[cut_mid:cut_end])

                new_cut = chiprops.x_cuts.add()
                new_cut.value = cut_value
            self.CreateXCuts(chiprops,context) 

        # ============== Create new y-cuts
        if (chiprops.num_y_cuts != 0):
            for i in range(0,chiprops.num_y_cuts):
                cut_start = out.find('Y-cut'+str(i)+' ')
                cut_mid   = out.find(' ',cut_start)
                cut_end   = out.find('\n',cut_start)
                cut_value = float(out[cut_mid:cut_end])

                new_cut = chiprops.y_cuts.add()
                new_cut.value = cut_value
            self.CreateYCuts(chiprops,context) 

        lbf = context.scene.chiutilsA.ComputeLBF(context)
        chiprops.load_bal_factor_i = lbf

        return {'RUNNING_MODAL'}

def register():
    bpy.utils.register_class(AddCutLinesButton)
    bpy.utils.register_class(AddBalancedCutLinesButton)
  
def unregister():
    bpy.utils.unregister_class(AddCutLinesButton)
    bpy.utils.unregister_class(AddBalancedCutLinesButton)