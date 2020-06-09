import bpy
from bpy.props import (
        BoolProperty,
        EnumProperty,
        FloatProperty,
        IntProperty,
        FloatVectorProperty,
        StringProperty,
        )
import bmesh
from bmesh.types import BMVert, BMEdge
import random
import copy 
from mathutils import Vector

def extrude_and_move(bm, geom, vec):
    extruded = bmesh.ops.extrude_face_region(bm, geom = geom)
    translate_verts = [v for v in extruded['geom'] if isinstance(v, BMVert)]
    bmesh.ops.translate(bm, vec=vec, verts= translate_verts)
    bmesh.ops.delete(bm, geom=geom, context= 'FACES')
    return extruded

def bmverts_from_bmedges(bmedges):
    bmverts = []
    for value in bmedges:
        bmverts.append(value.verts[0])
    return bmverts

def edgeloop_and_slide(bm, edges, vec):
    loop_edges = bmesh.ops.offset_edgeloops(bm, edges = edges)
    loop_verts = bmverts_from_bmedges([v for v in loop_edges['edges'] if isinstance(v, BMEdge)])
    return bmesh.ops.translate(bm, vec=vec, verts= loop_verts)

def generate_skyscraper(props, context):
    random.seed(props.seed)
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1)
# generate base shape
    #random base height
    bm.faces.ensure_lookup_table()
    for face in bm.faces[:]:
        if(face.normal.z ==1):
            base_height = props.height/((random.random()*2)+1)
            bmesh.ops.translate(bm,
            verts=face.verts,
            vec=base_height * face.normal)
    loop_cut = False
    # maybe make random edge loop
    for face in bm.faces[:]:
        if(face.normal.z==0):
            if(random.random()<0.2):
                if(not loop_cut):
                    leng = 0
                    link_faces = face.edges[0].link_faces
                    for other_face in link_faces:
                        if(face!=other_face):
                            l = face.edges[0].calc_length()
                            
                            for other_edge in other_face.edges:
                                if(other_edge.calc_length()!=l):
                                    leng = other_edge.calc_length()
                    edgeloop_and_slide(bm, face.edges,face.normal*-(leng/4+random.random()*leng/2))
                    loop_cut = True
    # maybe make random horizontal extrusion
    for face in bm.faces[:]:
        if(face.normal.z==0):
            if(random.random()<0.3):
                extruded = extrude_and_move(bm,[face],face.normal*(0.25+random.random()*0.5))
    # random x y scale
    bmesh.ops.scale(bm, verts = bm.verts, vec = ((random.random()*4)+2,(random.random()*4)+2,1))
    # maybe move edges along normals - check for overlap

    # maybe bevel random edges

    # generate actual structure
        # select random top faces and extrude up OR extrude, scale in, extrude move up
        # maybe select random horizontal face and extrude out
        # maybe make horizontal loops and scale in
        # repeat

    #finishing touches
        # maybe select random outer edges paralell to inner ones and move up or down
        # maybe add antenna
        # maybe bevel?

    # write bmesh into new mesh
    bm.normal_update()
    me = bpy.data.meshes.new('Mesh')
    bm.to_mesh(me)
    bm.free()

    # Add mesh to the scene
    obj = bpy.data.objects.new('Skyscraper', me)
    bpy.context.collection.objects.link(obj)

class GenerateSkyscraper(bpy.types.Operator):
    """Construct a skyscraper """      # Use this as a tooltip for menu items and buttons.
    bl_idname = "mesh.add_skyscraper"        # Unique identifier for buttons and menu items to reference.
    bl_label = "Add Skyscraper"         # Display name in the interface.
    bl_options = {'REGISTER', 'UNDO'}  # Enable undo for the operator.

    #properties
    seed: bpy.props.IntProperty(name="Seed", default=0)
    height: bpy.props.IntProperty(name="Height", default=5, min=1, max=10)
    complexity: bpy.props.IntProperty(name="Complexity", default=5, min=1, max=10)
    random_height : bpy.props.FloatProperty(name="Random Height", default=0, min=0, max=5)
    random_complexity : bpy.props.FloatProperty(name="Random Complexity", default=0, min=0, max=1)
    detail: bpy.props.IntProperty(name="Detail", default=5, min=1, max=10)

    def execute(self, context):        # execute() is called when running the operator.
        #make a skyscraper lmaoooo
        generate_skyscraper(self, context)
        return {'FINISHED'}            # Lets Blender know the operator finished successfully.


