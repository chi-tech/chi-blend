import os
import bpy
from bpy_extras.io_utils import ExportHelper
import numpy as np
import mathutils

class ChiUtilsA(bpy.types.PropertyGroup):
    def SayHello(self):
        print("Hello")

    
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
    
    def ComputeLBF(self,context):
        chiprops = context.scene.chitech_properties
        cur_objname = chiprops.current_object+"TriMesh"
        #if grid-wise
        num_x_cuts = chiprops.num_x_cuts
        num_y_cuts = chiprops.num_y_cuts
        num_subsets = (chiprops.num_x_cuts+1)*(chiprops.num_y_cuts+1)
        subset_counts = np.zeros(num_subsets)
        num_polys   = len(bpy.data.objects[cur_objname].data.polygons)
        for p in range(0,num_polys):
            
            poly = bpy.data.objects[cur_objname].data.polygons[p]
            poly_center_x = poly.center[0]
            poly_center_y = poly.center[1]

            x=-1
            for i in range(0,num_x_cuts):
                if bpy.data.objects.get("Xcut"+str(i)) is None:
                    continue
                xcut = bpy.data.objects["Xcut"+str(i)].location[0]
                chiprops.x_cuts[i].value = xcut
                if (poly_center_x <= xcut):
                    x=i
                    break
            if (x==-1):
                x = num_x_cuts

            y=-1
            for i in range(0,num_y_cuts):
                if bpy.data.objects.get("Ycut"+str(i)) is None:
                    continue
                ycut = bpy.data.objects["Ycut"+str(i)].location[1]
                chiprops.y_cuts[i].value = ycut
                if (poly_center_y <= ycut):
                    y=i
                    break
            if (y==-1):
                y = num_y_cuts

            subset = (num_x_cuts+1)*y + x 

            if subset<num_subsets:
                subset_counts[subset] += 1.0
        
        # Determine max
        max_cells = 0
        tot_cells = 0
        for p in range(0,num_subsets):
            tot_cells += subset_counts[p]
            if (subset_counts[p] > max_cells):
                max_cells = subset_counts[p]

        avg_cells = tot_cells/num_subsets
        max_to_avg = max_cells/avg_cells

        #print("Load balance factor = %g" %max_to_avg)

        return max_to_avg

    def ExportTriMesh(self,context):
        print("Exporting TriMesh")
        chiprops = context.scene.chitech_properties
        pathdir  = chiprops.path_to_workdir 
        if ((pathdir == "") or (pathdir == "..")):
            self.report({'WARNING'},"Working directory not set")
            return
        
        cur_objname = chiprops.current_object

        # Create mesh input file
        h = open(pathdir+"/"+cur_objname+"_MESH.lua",'w')
        h.write('newSurfMesh = chiSurfaceMeshCreate();\n')
        h.write('chiSurfaceMeshImportFromOBJFile(newSurfMesh,"')
        h.write(cur_objname+'Mesh.obj')
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

        h.close()

        # Export the object to .obj file
        exp_objname = chiprops.current_object+"TriMesh"
        bpy.ops.object.select_all(action='DESELECT')
        bpy.ops.object.select_pattern(pattern=exp_objname+"*")
        bpy.context.view_layer.objects.active = bpy.data.objects[exp_objname]

        bpy.ops.export_scene.obj(
                   filepath       = pathdir+"/"+cur_objname+'Mesh.obj',
                   check_existing = False,
                   axis_forward   = 'Y',
                   axis_up        = 'Z',
                   use_selection  = True,
                   use_materials  = False)

    def ShowMessageBox(self,message = "", title = "Message Box", icon = 'INFO'):

        def draw(self, context):
            lines = message.splitlines()
            for line in lines:
                self.layout.label(text=line)

        bpy.context.window_manager.popup_menu(draw, title = title, icon = icon)
    
    def CheckChiPath(self,context):
        chiprops = context.scene.chitech_properties
        if (not os.path.exists(chiprops.path_to_chitech_exe)):
            self.ShowMessageBox("Invalid path to ChiTech. Make sure " + \
                                "it is not relative.",
                                title="chi-blend error",
                                icon='ERROR')
            return False
        return True

    def CheckTrianglePath(self,context):
        chiprops = context.scene.chitech_properties
        if (not os.path.exists(chiprops.path_to_triangle_exe)):
            self.ShowMessageBox("Invalid path to triangle executable " + \
                                ". Make sure " + \
                                "it is not relative.",
                                title="chi-blend error",
                                icon='ERROR')
            return False
        return True                    

    def CheckWorkDirPath(self,context):
        chiprops = context.scene.chitech_properties
        if (chiprops.path_to_workdir[0:3]=="../"):
            self.ShowMessageBox("Invalid path to working directory." + \
                                "ChiTech requires absolute paths.",
                                title="chi-blend error",
                                icon='ERROR') 
        if (chiprops.path_to_workdir[0:3]=="./"):
            self.ShowMessageBox("Invalid path to working directory." + \
                                "ChiTech requires absolute paths.",
                                title="chi-blend error",
                                icon='ERROR')                         
        if (not os.path.isdir(chiprops.path_to_workdir)):
            self.ShowMessageBox("Invalid path to working directory.",
                                title="chi-blend error",
                                icon='ERROR')    
            return False
        return True   

    def CheckMeshDir(self,context):
        chiprops = context.scene.chitech_properties 
        pathdir = chiprops.path_to_workdir
        if not os.path.exists(pathdir+'/Mesh'):
            os.mkdir(pathdir+'/Mesh') 

    def CheckAllPaths(self,context):
        if (not self.CheckChiPath(context)):
            return False
        if (not self.CheckTrianglePath(context)):
            return False
        if (not self.CheckWorkDirPath(context)):
            return False
        # Create Mesh directory if not exist
        self.CheckMeshDir(context)  
        return True   

    def CheckChiAndMeshPaths(self,context):
        if (not self.CheckChiPath(context)):
            return False
        if (not self.CheckWorkDirPath(context)):
            return False
        # Create Mesh directory if not exist
        self.CheckMeshDir(context)  
        return True                                                                

def register():
    bpy.utils.register_class(ChiUtilsA)

    bpy.types.Scene.chiutilsA = bpy.props.PointerProperty(type=ChiUtilsA)
  
def unregister():
    bpy.utils.unregister_class(ChiUtilsA)