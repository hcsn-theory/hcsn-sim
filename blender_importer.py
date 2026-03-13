import bpy
import json
import os

# =========================================================================
# HCSN Blender Cinematic Importer
# -------------------------------------------------------------------------
# INSTRUCTIONS:
# 1. Open Blender > Scripting Workspace
# 2. Paste this script into a New Text block.
# 3. Change the JSON_FILE_PATH below to point to your cinematic_frames.json
# 4. Click "Run Script" (Play Button).
# =========================================================================
JSON_FILE_PATH = "/home/saif/hcsn-sim/cinematic_frames.json" # Provide absolute path if needed
def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

def load_frames(filepath):
    with open(filepath, 'r') as f:
        return json.load(f)

def run_import():
    clear_scene()
    print("Loading HCSN Frames...")
    
    if not os.path.exists(JSON_FILE_PATH):
        print(f"Error: Could not find {JSON_FILE_PATH}")
        return

    frames = load_frames(JSON_FILE_PATH)
    if not frames:
        return

    # Create root collection
    collection = bpy.data.collections.new("HCSN_Simulation")
    bpy.context.scene.collection.children.link(collection)

    # We will instance a sphere for vertices
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=3, radius=1.0)
    base_sphere = bpy.context.active_object
    base_sphere.name = "VertexTemplate"
    base_sphere.hide_viewport = True
    base_sphere.hide_render = True

    # We will instance a cylinder for edges
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.08, depth=1.0)
    base_cylinder = bpy.context.active_object
    base_cylinder.name = "EdgeTemplate"
    base_cylinder.hide_viewport = True
    base_cylinder.hide_render = True

    # ---- AUTOMATED CINEMATIC SETUP ----
    
    # 1. Setup EEVEE rendering and Bloom
    bpy.context.scene.render.engine = 'BLENDER_EEVEE'
    if hasattr(bpy.context.scene.eevee, 'use_bloom'): # Blender 3.x to 4.1
        bpy.context.scene.eevee.use_bloom = True
        bpy.context.scene.eevee.bloom_intensity = 0.05
    
    # 2. Make World Pitch Black
    if bpy.data.worlds:
        world = bpy.data.worlds[0]
        world.use_nodes = True
        bg_node = world.node_tree.nodes.get("Background")
        if bg_node:
            bg_node.inputs[0].default_value = (0.01, 0.01, 0.02, 1.0) # Very dark void
            bg_node.inputs[1].default_value = 1.0

    # 3. Create Glowing Emission Material for Nodes
    mat_node = bpy.data.materials.new(name="NeonGlow_Node")
    mat_node.use_nodes = True
    bsdf_n = mat_node.node_tree.nodes.get("Principled BSDF")
    if bsdf_n:
        if 'Emission' in bsdf_n.inputs:
            bsdf_n.inputs['Emission'].default_value = (0.0, 1.0, 0.8, 1.0) # Cyan-Green
            bsdf_n.inputs['Emission Strength'].default_value = 12.0
        elif 'Emission Color' in bsdf_n.inputs:
            bsdf_n.inputs['Emission Color'].default_value = (0.0, 1.0, 0.8, 1.0)
            if 'Emission Strength' in bsdf_n.inputs: bsdf_n.inputs['Emission Strength'].default_value = 12.0
        if 'Base Color' in bsdf_n.inputs: bsdf_n.inputs['Base Color'].default_value = (0.0, 0.0, 0.0, 1.0)
    base_sphere.data.materials.append(mat_node)

    # Create distinct Emission Material for Edges
    mat_edge = bpy.data.materials.new(name="NeonGlow_Edge")
    mat_edge.use_nodes = True
    bsdf_e = mat_edge.node_tree.nodes.get("Principled BSDF")
    if bsdf_e:
        if 'Emission' in bsdf_e.inputs:
            bsdf_e.inputs['Emission'].default_value = (1.0, 0.2, 0.6, 1.0) # Pinkish-Red Edge
            bsdf_e.inputs['Emission Strength'].default_value = 5.0
        elif 'Emission Color' in bsdf_e.inputs:
            bsdf_e.inputs['Emission Color'].default_value = (1.0, 0.2, 0.6, 1.0)
            if 'Emission Strength' in bsdf_e.inputs: bsdf_e.inputs['Emission Strength'].default_value = 5.0
        if 'Base Color' in bsdf_e.inputs: bsdf_e.inputs['Base Color'].default_value = (0.0, 0.0, 0.0, 1.0)
    base_cylinder.data.materials.append(mat_edge)
    
    # 4. Setup a default Camera looking at the center
    camera_data = bpy.data.cameras.new(name="CinematicCam")
    camera_object = bpy.data.objects.new("CinematicCam", camera_data)
    bpy.context.scene.collection.objects.link(camera_object)
    bpy.context.scene.camera = camera_object
    # Position camera far back to see whole graph
    camera_object.location = (0, -80, 20)
    camera_object.rotation_euler = (1.2, 0, 0) # Tilted down slightly

    # -----------------------------------
    
    # Store instances by ID
    node_objects = {}
    edge_objects = {}

    bpy.context.scene.frame_start = 1
    bpy.context.scene.frame_end = len(frames)

    import mathutils

    for frame_idx, frame_data in enumerate(frames):
        current_frame = frame_idx + 1
        
        # ── Spawn/Update Vertices ──
        active_ids = set()
        v_pos_map = {}
        for v in frame_data["vertices"]:
            vid = str(v["id"])
            active_ids.add(vid)
            # Store position for edge mapping (Y-up to Z-up coordinate swap)
            vpos = mathutils.Vector((v["pos"][0] * 0.1, v["pos"][2] * 0.1, v["pos"][1] * 0.1))
            v_pos_map[vid] = vpos
            
            if vid not in node_objects:
                new_obj = base_sphere.copy()
                new_obj.data = base_sphere.data.copy()
                new_obj.name = f"Node_{vid}"
                collection.objects.link(new_obj)
                node_objects[vid] = new_obj
                
                new_obj.hide_viewport = True
                new_obj.hide_render = True
                new_obj.keyframe_insert(data_path="hide_viewport", frame=max(1, current_frame - 1))
                new_obj.keyframe_insert(data_path="hide_render", frame=max(1, current_frame - 1))

            obj = node_objects[vid]
            obj.hide_viewport = False
            obj.hide_render = False
            obj.keyframe_insert(data_path="hide_viewport", frame=current_frame)
            obj.keyframe_insert(data_path="hide_render", frame=current_frame)
            
            obj.location = vpos
            obj.keyframe_insert(data_path="location", frame=current_frame)
            
            scale = min(max(v["xi"] * 2.0, 0.2), 3.0)
            obj.scale = (scale, scale, scale)
            obj.keyframe_insert(data_path="scale", frame=current_frame)
            
        # Hide nodes that phased out
        for vid, obj in node_objects.items():
            if vid not in active_ids:
                obj.hide_viewport = True
                obj.hide_render = True
                obj.keyframe_insert(data_path="hide_viewport", frame=current_frame)
                obj.keyframe_insert(data_path="hide_render", frame=current_frame)


        # ── Spawn/Update Edges ──
        active_edges = set()
        for idx, edge_group in enumerate(frame_data.get("edges", [])):
            for i in range(len(edge_group) - 1):
                ida = str(edge_group[i])
                idb = str(edge_group[i+1])
                # Generate unique sort-independent edge key
                ekey = f"E_{min(ida, idb)}_{max(ida, idb)}_{idx}_{i}"
                
                pa = v_pos_map.get(ida)
                pb = v_pos_map.get(idb)
                if pa is None or pb is None:
                    continue
                    
                active_edges.add(ekey)
                
                if ekey not in edge_objects:
                    new_edge = base_cylinder.copy()
                    new_edge.data = base_cylinder.data.copy()
                    new_edge.name = ekey
                    collection.objects.link(new_edge)
                    edge_objects[ekey] = new_edge
                    
                    new_edge.hide_viewport = True
                    new_edge.hide_render = True
                    new_edge.keyframe_insert(data_path="hide_viewport", frame=max(1, current_frame - 1))
                    new_edge.keyframe_insert(data_path="hide_render", frame=max(1, current_frame - 1))
                
                eobj = edge_objects[ekey]
                eobj.hide_viewport = False
                eobj.hide_render = False
                eobj.keyframe_insert(data_path="hide_viewport", frame=current_frame)
                eobj.keyframe_insert(data_path="hide_render", frame=current_frame)
                
                # Math to align cylinder between pa and pb
                midpoint = (pa + pb) / 2.0
                eobj.location = midpoint
                eobj.keyframe_insert(data_path="location", frame=current_frame)
                
                direction = pb - pa
                length = direction.length
                
                if length > 0.001:
                    # Stretch cylinder to span distance (Z is depth in default cylinder)
                    eobj.scale = (1.0, 1.0, length)
                    eobj.keyframe_insert(data_path="scale", frame=current_frame)
                    
                    # Rotate to face direction
                    rot_quat = direction.to_track_quat('Z', 'Y')
                    eobj.rotation_euler = rot_quat.to_euler()
                    eobj.keyframe_insert(data_path="rotation_euler", frame=current_frame)

        # Hide old edges
        for ekey, eobj in edge_objects.items():
            if ekey not in active_edges:
                eobj.hide_viewport = True
                eobj.hide_render = True
                eobj.keyframe_insert(data_path="hide_viewport", frame=current_frame)
                eobj.keyframe_insert(data_path="hide_render", frame=current_frame)

    print("Import Complete! Hit Spacebar to play the timeline.")

if __name__ == "__main__":
    run_import()
