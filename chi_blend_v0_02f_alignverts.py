import os
import bpy
from bpy_extras.io_utils import ExportHelper
import subprocess
import mathutils

# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
class AlignVertices(bpy.types.Operator):
    bl_label = "Aligns the vertices along x and y cuts"
    bl_idname = "chitech.alignvertices"  
    bl_options = {"UNDO"}

    # ===========================================
    def invoke(self, context, event):
        chiprops = context.scene.chitech_properties
        cur_objname = chiprops.current_object+"TriMesh"
        pathdir = chiprops.path_to_workdir

        bpy.ops.object.mode_set(mode='OBJECT')

        obj = bpy.data.objects[cur_objname] # active object

        # dump(obj.data)
        mesh = obj.data
        print("# of vertices=%d" % len(mesh.vertices))
        num_verts_moved = 0
        for vert in mesh.vertices:
            if (not vert.select):
                continue
            vertex_moved = False
            for i in range(0,chiprops.num_x_cuts):
                xv = chiprops.x_cuts[i].value
                if abs(vert.co.x - xv)<chiprops.cut_epsilon:
                    vert.co.x = xv
                    vertex_moved = True
            for j in range(0,chiprops.num_y_cuts):
                yv = chiprops.y_cuts[j].value
                if abs(vert.co.y - yv)<chiprops.cut_epsilon:
                    vert.co.y = yv
                    vertex_moved = True
            if vertex_moved:
                num_verts_moved += 1

        bpy.ops.object.mode_set(mode='EDIT')

        print( 'Num vertices moved %d\n' % (num_verts_moved) )
        # vert.co = vert.co + mathutils.Vector([1.0,0.0,0.0])

        context.scene.chiutilsA.ShowMessageBox("Hello")

        return {"FINISHED"}

def register():
    bpy.utils.register_class(AlignVertices)
  
def unregister():
    bpy.utils.unregister_class(AlignVertices)