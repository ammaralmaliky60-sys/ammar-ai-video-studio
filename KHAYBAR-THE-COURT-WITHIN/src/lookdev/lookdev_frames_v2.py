"""
THE COURT WITHIN — GATE 3A Look-Development frames V2 (reference-driven: REF_01–REF_20) (Blender 4.2 LTS, Cycles CPU).
Usage:  blender -b --python lookdev_frames.py -- <A|B|C> <out.png> <scale%> <samples> <texdir>
Deterministic: every random value comes from a seeded RNG. No external services.
Assets: MPFB (CC0 human output), Poly Haven CC0 textures, everything else procedural.
"""
import bpy, bmesh, math, random, sys, importlib, addon_utils
from mathutils import Vector, Euler

argv = sys.argv[sys.argv.index("--") + 1:]
FRAME, OUT, SCALE, SAMPLES, TEX = argv[0], argv[1], int(argv[2]), int(argv[3]), argv[4]
RNG = random.Random(1405)

# ---------------- brand tokens (linearised in shader via sRGB->linear) ----------------
def srgb(h, a=1.0):
    h = h.lstrip("#"); c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    lin = [x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c]
    return (*lin, a)
TEAL_DEEP, TEAL_2, GOLD, IVORY, TURQ = srgb("#071F26"), srgb("#153840"), srgb("#D4AA61"), srgb("#F4E9D3"), srgb("#2DB9B6")

# ---------------- scene reset ----------------
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.render.engine = "CYCLES"
sc.cycles.device = "CPU"
sc.cycles.samples = SAMPLES
sc.cycles.use_adaptive_sampling = True
sc.cycles.adaptive_threshold = 0.02
sc.cycles.use_denoising = True
sc.cycles.denoiser = "OPENIMAGEDENOISE"
sc.cycles.max_bounces = 8; sc.cycles.glossy_bounces = 6; sc.cycles.transmission_bounces = 8
sc.cycles.volume_bounces = 1; sc.cycles.volume_step_rate = 4.0
sc.cycles.caustics_reflective = False; sc.cycles.caustics_refractive = False
sc.cycles.seed = 7
sc.render.resolution_x, sc.render.resolution_y = 1080, 1920
sc.render.resolution_percentage = SCALE
sc.render.film_transparent = False
sc.view_settings.view_transform = "AgX"
sc.view_settings.look = "AgX - Medium High Contrast"
sc.render.image_settings.file_format = "PNG"
sc.render.filepath = OUT
sc.render.threads_mode = "AUTO"

# ---------------- materials ----------------
def node_mat(name):
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; bsdf = nt.nodes["Principled BSDF"]; return m, nt, bsdf

def tex_mat(name, base, scale=1.0, tint=None, rough_mul=1.0, spec=0.5):
    m, nt, b = node_mat(name)
    tc = nt.nodes.new("ShaderNodeTexCoord"); mp = nt.nodes.new("ShaderNodeMapping")
    mp.inputs["Scale"].default_value = (scale, scale, scale)
    nt.links.new(tc.outputs["Object"], mp.inputs["Vector"])
    def img(suffix, noncolor):
        n = nt.nodes.new("ShaderNodeTexImage"); n.image = bpy.data.images.load(f"{TEX}/{base}_{suffix}.jpg")
        n.projection = "BOX"; n.projection_blend = 0.25
        if noncolor: n.image.colorspace_settings.name = "Non-Color"
        nt.links.new(mp.outputs["Vector"], n.inputs["Vector"]); return n
    d, r, nn = img("diff", False), img("rough", True), img("nor", True)
    if tint:
        mix = nt.nodes.new("ShaderNodeMix"); mix.data_type = "RGBA"; mix.blend_type = "MULTIPLY"
        mix.inputs["Factor"].default_value = 1.0; mix.inputs[7].default_value = tint
        nt.links.new(d.outputs["Color"], mix.inputs[6]); nt.links.new(mix.outputs[2], b.inputs["Base Color"])
    else:
        nt.links.new(d.outputs["Color"], b.inputs["Base Color"])
    mr = nt.nodes.new("ShaderNodeMath"); mr.operation = "MULTIPLY"; mr.inputs[1].default_value = rough_mul
    nt.links.new(r.outputs["Color"], mr.inputs[0]); nt.links.new(mr.outputs[0], b.inputs["Roughness"])
    nm = nt.nodes.new("ShaderNodeNormalMap"); nm.inputs["Strength"].default_value = 0.8
    nt.links.new(nn.outputs["Color"], nm.inputs["Color"]); nt.links.new(nm.outputs["Normal"], b.inputs["Normal"])
    b.inputs["Specular IOR Level"].default_value = spec
    return m

def aged_gold():
    m, nt, b = node_mat("AgedGold")
    b.inputs["Base Color"].default_value = srgb("#C9A05A"); b.inputs["Metallic"].default_value = 1.0
    noise = nt.nodes.new("ShaderNodeTexNoise"); noise.inputs["Scale"].default_value = 60; noise.inputs["Detail"].default_value = 8
    ramp = nt.nodes.new("ShaderNodeMapRange"); ramp.inputs["To Min"].default_value = 0.18; ramp.inputs["To Max"].default_value = 0.42
    nt.links.new(noise.outputs["Fac"], ramp.inputs["Value"]); nt.links.new(ramp.outputs["Result"], b.inputs["Roughness"])
    bump = nt.nodes.new("ShaderNodeBump"); bump.inputs["Strength"].default_value = 0.08
    nt.links.new(noise.outputs["Fac"], bump.inputs["Height"]); nt.links.new(bump.outputs["Normal"], b.inputs["Normal"])
    return m

def smoked_mirror(rough=0.02):
    m, nt, b = node_mat("SmokedMirror")
    b.inputs["Base Color"].default_value = srgb("#5d7f80"); b.inputs["Metallic"].default_value = 1.0
    b.inputs["Roughness"].default_value = rough
    # faint surface imperfection (smudges) so it doesn't read as CG chrome
    noise = nt.nodes.new("ShaderNodeTexNoise"); noise.inputs["Scale"].default_value = 9; noise.inputs["Detail"].default_value = 6
    mr = nt.nodes.new("ShaderNodeMapRange"); mr.inputs["To Min"].default_value = rough; mr.inputs["To Max"].default_value = rough + 0.06
    nt.links.new(noise.outputs["Fac"], mr.inputs["Value"]); nt.links.new(mr.outputs["Result"], b.inputs["Roughness"])
    return m

def shard_glass():
    """Mirror shard: silvered back (metallic) + glass edge feel via coat."""
    m, nt, b = node_mat("ShardGlass")
    b.inputs["Base Color"].default_value = srgb("#6f9192"); b.inputs["Metallic"].default_value = 0.92
    b.inputs["Roughness"].default_value = 0.03; b.inputs["Coat Weight"].default_value = 1.0; b.inputs["Coat Roughness"].default_value = 0.0
    return m

def fabric():
    m, nt, b = node_mat("DarkFabric")
    b.inputs["Base Color"].default_value = srgb("#0c0e10"); b.inputs["Roughness"].default_value = 0.8
    b.inputs["Sheen Weight"].default_value = 0.2; b.inputs["Sheen Roughness"].default_value = 0.4
    b.inputs["Specular IOR Level"].default_value = 0.0    # wool: no specular veil (verified by A/B test)
    b.inputs["Sheen Tint"].default_value = srgb("#6b7b7e")
    w = nt.nodes.new("ShaderNodeTexWave"); w.inputs["Scale"].default_value = 3.0; w.inputs["Distortion"].default_value = 6; w.inputs["Detail"].default_value = 4
    bump = nt.nodes.new("ShaderNodeBump"); bump.inputs["Strength"].default_value = 0.25
    nt.links.new(w.outputs["Fac"], bump.inputs["Height"]); nt.links.new(bump.outputs["Normal"], b.inputs["Normal"])
    return m

def paper():
    m, nt, b = node_mat("Paper")
    b.inputs["Base Color"].default_value = srgb("#d9ccb0"); b.inputs["Roughness"].default_value = 0.7
    b.inputs["Subsurface Weight"].default_value = 0.15; b.inputs["Subsurface Radius"].default_value = (0.02, 0.02, 0.02)
    return m

def emissive(col, strength):
    m, nt, b = node_mat("Emit")
    b.inputs["Emission Color"].default_value = col; b.inputs["Emission Strength"].default_value = strength
    b.inputs["Base Color"].default_value = (0, 0, 0, 1); return m

M_WALNUT = tex_mat("Walnut", "black_walnut_veneer_01", 1.2, tint=srgb("#8a6a55"), rough_mul=0.75)
M_FLOOR = tex_mat("FloorPlanks", "dark_wooden_planks", 0.35, tint=srgb("#7b675a"), rough_mul=0.55)
M_BASALT = tex_mat("Basalt", "volcanic_rock_tiles", 0.45, tint=srgb("#6c6f70"), rough_mul=1.0)
M_GOLD, M_MIRROR, M_SHARD, M_FABRIC, M_PAPER = aged_gold(), smoked_mirror(), shard_glass(), fabric(), paper()

def skin():
    m, nt, b = node_mat("Skin")   # kept in shadow by lighting design (faceless)
    b.inputs["Base Color"].default_value = srgb("#2e231d"); b.inputs["Roughness"].default_value = 0.6
    b.inputs["Subsurface Weight"].default_value = 0.2; b.inputs["Subsurface Radius"].default_value = (0.012, 0.005, 0.003)
    return m
M_SKIN = skin()
for _m in bpy.data.materials: _m.use_fake_user = True  # MPFB purges unused materials when adding clothes

# ---------------- helpers ----------------
def link(o, mat=None):
    if mat: o.data.materials.clear(); o.data.materials.append(mat)
    return o

def box(name, loc, size, mat, bevel=0.0):
    bpy.ops.mesh.primitive_cube_add(location=loc); o = bpy.context.object; o.name = name
    o.scale = (size[0] / 2, size[1] / 2, size[2] / 2); bpy.ops.object.transform_apply(scale=True)
    if bevel:
        md = o.modifiers.new("bev", "BEVEL"); md.width = bevel; md.segments = 3
    return link(o, mat)

def column(name, x, y, h, r, mat):
    bpy.ops.mesh.primitive_cylinder_add(vertices=48, radius=r, depth=h, location=(x, y, h / 2)); o = bpy.context.object; o.name = name
    link(o, mat); bpy.ops.object.shade_smooth()
    # fluting via displacement
    tex = bpy.data.textures.new(name + "flute", "WOOD"); tex.wood_type = "RINGS"; tex.noise_basis_2 = "SAW"
    box(name + "_base", (x, y, 0.15), (r * 2.8, r * 2.8, 0.3), mat, 0.02)
    box(name + "_cap", (x, y, h - 0.15), (r * 2.6, r * 2.6, 0.3), mat, 0.02)
    return o

def arch_curve(name, width, height, thick, depth, mat, loc, rot=(math.radians(90), 0, 0)):
    """KHAYBAR-inspired arch frame: rectangle + semicircle top, as a beveled curve outline."""
    r = width / 2; pts = []
    pts.append((-r, 0)); pts.append((-r, height - r))
    for i in range(1, 32):
        a = math.pi - math.pi * i / 32; pts.append((r * math.cos(a), height - r + r * math.sin(a)))
    pts.append((r, height - r)); pts.append((r, 0))
    cu = bpy.data.curves.new(name, "CURVE"); cu.dimensions = "3D"
    sp = cu.splines.new("POLY"); sp.points.add(len(pts) - 1)
    for p, (x, z) in zip(sp.points, pts): p.co = (x, 0, z, 1)
    sp.use_cyclic_u = False
    cu.bevel_mode = "PROFILE" if False else "ROUND"; cu.bevel_depth = thick; cu.bevel_resolution = 4; cu.extrude = 0
    o = bpy.data.objects.new(name, cu); bpy.context.collection.objects.link(o); o.location = loc
    o.data.materials.append(mat)
    return o, pts

def arch_panel(name, width, height, loc, mat):
    """Filled arch-shaped panel (mirror glass / gateway)."""
    r = width / 2; bm = bmesh.new(); vs = [bm.verts.new((-r, 0, 0)), bm.verts.new((r, 0, 0))]
    vs.append(bm.verts.new((r, 0, height - r)))
    for i in range(1, 32):
        a = math.pi * i / 32; vs.append(bm.verts.new((r * math.cos(a), 0, height - r + r * math.sin(a))))
    vs.append(bm.verts.new((-r, 0, height - r)))
    bm.faces.new(vs); me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(name, me); bpy.context.collection.objects.link(o); o.location = loc
    return link(o, mat)

def area(name, loc, rot, size, power, col, spot=None):
    bpy.ops.object.light_add(type="AREA", location=loc, rotation=rot); l = bpy.context.object; l.name = name
    l.data.size = size; l.data.energy = power; l.data.color = col[:3]
    if spot is not None: l.data.spread = math.radians(spot)
    return l

def no_reflect(l): l.visible_glossy = False; l.visible_transmission = False; return l

def spot(name, loc, target, power, col, angle=25, blend=0.4, radius=0.05):
    bpy.ops.object.light_add(type="SPOT", location=loc); l = bpy.context.object; l.name = name
    l.data.energy = power; l.data.color = col[:3]; l.data.spot_size = math.radians(angle); l.data.spot_blend = blend
    l.data.shadow_soft_size = radius
    d = Vector(target) - Vector(loc); l.rotation_euler = d.to_track_quat("-Z", "Y").to_euler(); return l

def fog(density, anis=0.35, col=(0.85, 0.88, 0.9, 1), loc=(0, 0, 6), scl=(30, 30, 12)):
    w = bpy.data.worlds.new("World"); sc.world = w; w.use_nodes = True
    nt = w.node_tree; bg = nt.nodes["Background"]; bg.inputs["Color"].default_value = (0.002, 0.004, 0.005, 1); bg.inputs["Strength"].default_value = 1
    # fog volume as a big box (more controllable than world volume)
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc); v = bpy.context.object; v.name = "FogVolume"; v.scale = scl
    m = bpy.data.materials.new("Fog"); m.use_nodes = True; nt2 = m.node_tree; nt2.nodes.remove(nt2.nodes["Principled BSDF"])
    pv = nt2.nodes.new("ShaderNodeVolumePrincipled"); pv.inputs["Density"].default_value = density; pv.inputs["Anisotropy"].default_value = anis
    pv.inputs["Color"].default_value = col
    nt2.links.new(pv.outputs["Volume"], nt2.nodes["Material Output"].inputs["Volume"]); v.data.materials.append(m)
    v.visible_shadow = False
    return v

def camera(loc, target, lens, focus_obj=None, fstop=2.0, shift_y=0.0):
    bpy.ops.object.camera_add(location=loc); c = bpy.context.object; sc.camera = c
    d = Vector(target) - Vector(loc); c.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
    c.data.lens = lens; c.data.sensor_width = 36; c.data.sensor_fit = "HORIZONTAL"; c.data.shift_y = shift_y
    c.data.dof.use_dof = True; c.data.dof.aperture_fstop = fstop
    if focus_obj is not None:
        c.data.dof.focus_object = focus_obj
    else:
        c.data.dof.focus_distance = d.length
    return c

def human(loc, rot_z, arms_down=62, head_bow=0.0):
    addon_utils.enable("bl_ext.user_default.mpfb", default_set=True)
    S = "bl_ext.user_default.mpfb.services."
    HS = importlib.import_module(S + "humanservice").HumanService
    TS = importlib.import_module(S + "targetservice").TargetService
    md = TS.get_default_macro_info_dict(); md["gender"] = 0.85; md["height"] = 0.62; md["muscle"] = 0.55; md["weight"] = 0.5; md["proportions"] = 0.7
    h = HS.create_human(macro_detail_dict=md)
    rig = HS.add_builtin_rig(h, "default")
    # CC0 suit (MakeHuman asset pack suits01 — toigo_male_suit_3), rigged to the same armature
    suit = HS.add_mhclo_asset(f"{TEX}/../mhassets/clothes/toigo_male_suit_3/toigo_male_suit_3.mhclo", h, asset_type="Clothes", subdiv_levels=1)
    # CC0 short natural hair (MakeHuman hair01 pack — culturalibre_hair_02); keeps its own alpha-card material, darkened
    hair = HS.add_mhclo_asset(f"{TEX}/../mhassets/hair/culturalibre_hair_02/culturalibre_hair_02.mhclo", h, asset_type="Hair", subdiv_levels=0)
    if hair is None:
        hair = next((o for o in bpy.data.objects if "culturalibre_hair_02" in o.name), None)
    if hair is not None:   # keep the strand alpha, force a natural near-black colour with low gloss
        hm = hair.data.materials[0]; hb = hm.node_tree.nodes["Principled BSDF"]
        tint = hm.node_tree.nodes.new("ShaderNodeMix"); tint.data_type = "RGBA"; tint.blend_type = "MULTIPLY"; tint.inputs["Factor"].default_value = 1.0
        tint.inputs[7].default_value = srgb("#1b1612")
        src = hb.inputs["Base Color"].links[0].from_socket if hb.inputs["Base Color"].is_linked else None
        if src is not None: hm.node_tree.links.new(src, tint.inputs[6])
        hm.node_tree.links.new(tint.outputs[2], hb.inputs["Base Color"])
        hb.inputs["Roughness"].default_value = 0.45; hb.inputs["Specular IOR Level"].default_value = 0.25
        hm.use_fake_user = True
    pb = rig.pose.bones
    # base mesh is in an A-pose: rotate the upper arms DOWN toward the body (sign verified by test render)
    for side, sgn in (("L", 1), ("R", -1)):
        b = pb["upperarm01." + side]; b.rotation_mode = "XYZ"; b.rotation_euler = Euler((0, 0, math.radians(-sgn * arms_down)))
        lb = pb["lowerarm01." + side]; lb.rotation_mode = "XYZ"; lb.rotation_euler = Euler((math.radians(-6), 0, 0))
    if head_bow:
        for n in ("neck01", "head"):
            if n in pb: pb[n].rotation_mode = "XYZ"; pb[n].rotation_euler = Euler((math.radians(head_bow), 0, 0))
    rig.location = loc; rig.rotation_euler = (0, 0, math.radians(rot_z))
    h.data.materials.clear(); h.data.materials.append(M_SKIN)
    for p in h.data.polygons: p.use_smooth = True
    for o in bpy.data.objects:
        if o.type == "MESH" and o is not h and ("toigo" in o.name.lower() or "suit" in o.name.lower()) and not o.data.materials or (o.type == "MESH" and ("toigo" in o.name.lower() or "suit" in o.name.lower())):
            o.data.materials.clear(); o.data.materials.append(M_FABRIC)
            for p in o.data.polygons: p.use_smooth = True
    return h, rig

def floor(mat, size=60):
    bpy.ops.mesh.primitive_plane_add(size=size, location=(0, 0, 0)); return link(bpy.context.object, mat)

def shard_mesh(name, radius, seed):
    r = random.Random(seed); n = r.randint(4, 7); bm = bmesh.new(); vs = []
    angs = sorted(r.uniform(0, 2 * math.pi) for _ in range(n))
    for a in angs:
        rr = radius * r.uniform(0.45, 1.0); vs.append(bm.verts.new((math.cos(a) * rr * r.uniform(0.6, 1.4), 0, math.sin(a) * rr)))
    bm.faces.new(vs); me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(name, me); bpy.context.collection.objects.link(o)
    s = o.modifiers.new("thick", "SOLIDIFY"); s.thickness = 0.008; b = o.modifiers.new("bev", "BEVEL"); b.width = 0.0015
    return link(o, M_SHARD)

def glare(threshold=0.9, size=8, mix=-0.75):
    sc.use_nodes = True; nt = sc.node_tree
    rl = nt.nodes["Render Layers"]; comp = nt.nodes["Composite"]
    g = nt.nodes.new("CompositorNodeGlare"); g.glare_type = "FOG_GLOW"; g.threshold = threshold; g.size = size; g.mix = mix
    lens = nt.nodes.new("CompositorNodeLensdist"); lens.inputs[1].default_value = -0.005; lens.inputs[2].default_value = 0.012
    lens.use_fit = True
    vig = nt.nodes.new("CompositorNodeEllipseMask"); vig.width = 0.95; vig.height = 0.82
    blur = nt.nodes.new("CompositorNodeBlur"); blur.size_x = 200; blur.size_y = 200; blur.use_relative = False
    mixv = nt.nodes.new("CompositorNodeMixRGB"); mixv.blend_type = "MULTIPLY"; mixv.inputs[0].default_value = 0.55
    inv = nt.nodes.new("CompositorNodeMath"); inv.operation = "MAXIMUM"; inv.inputs[1].default_value = 0.35
    nt.links.new(rl.outputs["Image"], g.inputs["Image"]); nt.links.new(g.outputs["Image"], lens.inputs["Image"])
    nt.links.new(vig.outputs["Mask"], blur.inputs["Image"]); nt.links.new(blur.outputs["Image"], inv.inputs[0])
    nt.links.new(lens.outputs["Image"], mixv.inputs[1]); nt.links.new(inv.outputs[0], mixv.inputs[2])
    nt.links.new(mixv.outputs["Image"], comp.inputs["Image"])

# ======================= V2 helpers =======================
def glass_edge():
    m, nt, b = node_mat("GlassEdge")   # visible thickness of the mirror glass (slightly green, refractive)
    b.inputs["Base Color"].default_value = srgb("#cfe3d6"); b.inputs["Transmission Weight"].default_value = 1.0
    b.inputs["IOR"].default_value = 1.52; b.inputs["Roughness"].default_value = 0.02; m.use_fake_user = True
    return m

def mirror_bright(name="MirrorV2", tint="#b9c7c6", rough=0.008):
    m, nt, b = node_mat(name)        # silvered glass: brighter, near-perfect reflection + faint smudges
    b.inputs["Base Color"].default_value = srgb(tint); b.inputs["Metallic"].default_value = 1.0
    noise = nt.nodes.new("ShaderNodeTexNoise"); noise.inputs["Scale"].default_value = 14; noise.inputs["Detail"].default_value = 8
    mr = nt.nodes.new("ShaderNodeMapRange"); mr.inputs["To Min"].default_value = rough; mr.inputs["To Max"].default_value = rough + 0.035
    nt.links.new(noise.outputs["Fac"], mr.inputs["Value"]); nt.links.new(mr.outputs["Result"], b.inputs["Roughness"])
    b.inputs["Coat Weight"].default_value = 1.0; b.inputs["Coat Roughness"].default_value = 0.0; m.use_fake_user = True
    return m

M_EDGE = glass_edge(); M_MIRROR2 = mirror_bright(); M_SHARD2 = mirror_bright("ShardV2", "#c3d0cf", 0.004)
M_STONE = tex_mat("StoneFloor", "volcanic_rock_tiles", 0.28, tint=srgb("#8d9294"), rough_mul=0.45)
M_PANEL = tex_mat("Panel", "black_walnut_veneer_01", 2.2, tint=srgb("#9a7860"), rough_mul=0.55)
for _m in bpy.data.materials: _m.use_fake_user = True

def fluted_column(name, x, y, h, r, mat, flutes=20, depth=0.06):
    """Fluted shaft (scalloped profile, extruded) + stepped base and capital."""
    bm = bmesh.new(); ring = []
    n = flutes * 4
    for i in range(n):
        a = 2 * math.pi * i / n; rr = r - depth * r * (0.5 + 0.5 * math.cos(a * flutes))
        ring.append(bm.verts.new((math.cos(a) * rr, math.sin(a) * rr, 0)))
    f = bm.faces.new(ring)
    ext = bmesh.ops.extrude_face_region(bm, geom=[f]); vs = [e for e in ext["geom"] if isinstance(e, bmesh.types.BMVert)]
    bmesh.ops.translate(bm, verts=vs, vec=(0, 0, h))
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(name, me); bpy.context.collection.objects.link(o); o.location = (x, y, 0.55)
    for p in o.data.polygons: p.use_smooth = True
    link(o, mat)
    for i, (z, s, hh) in enumerate([(0.12, 2.9, 0.24), (0.36, 2.5, 0.24), (0.5, 2.2, 0.1)]):
        box(f"{name}_b{i}", (x, y, z), (r * s, r * s, hh), mat, 0.015)
    for i, (z, s, hh) in enumerate([(h + 0.6, 2.2, 0.1), (h + 0.75, 2.6, 0.22), (h + 0.95, 3.0, 0.2)]):
        box(f"{name}_c{i}", (x, y, z), (r * s, r * s, hh), mat, 0.015)
    return o

def wall_panels(name, x, y0, y1, z0, z1, facing, mat, gold=None):
    """Raised wooden wainscot panels with moulding (on a wall at x, facing +1/-1 in x)."""
    w = (y1 - y0); n = max(1, int(w / 1.4)); pw = w / n
    box(name + "_back", (x, (y0 + y1) / 2, (z0 + z1) / 2), (0.06, w, z1 - z0), mat)
    for i in range(n):
        cy = y0 + pw * (i + 0.5)
        box(f"{name}_p{i}", (x + facing * 0.04, cy, (z0 + z1) / 2), (0.05, pw * 0.8, (z1 - z0) * 0.78), mat, 0.012)
    box(name + "_rail", (x + facing * 0.06, (y0 + y1) / 2, z1), (0.1, w, 0.09), gold or mat, 0.01)

def pew(name, x, y, length, mat):
    box(name + "_seat", (x, y, 0.45), (length, 0.45, 0.07), mat, 0.01)
    box(name + "_back", (x, y + 0.22, 0.85), (length, 0.06, 0.8), mat, 0.01)
    for sx in (-1, 1): box(f"{name}_end{sx}", (x + sx * length / 2, y + 0.05, 0.55), (0.07, 0.6, 1.1), mat, 0.015)

def chandelier(name, loc, r=0.55, bulbs=8, power=6.0):
    bpy.ops.mesh.primitive_torus_add(major_radius=r, minor_radius=0.025, location=loc); link(bpy.context.object, M_GOLD)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.01, depth=4.0, location=(loc[0], loc[1], loc[2] + 2.0)); link(bpy.context.object, M_GOLD)
    em = emissive(srgb("#ffd59a"), power)
    for i in range(bulbs):
        a = 2 * math.pi * i / bulbs
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.05, location=(loc[0] + math.cos(a) * r, loc[1] + math.sin(a) * r, loc[2] + 0.08)); link(bpy.context.object, em)
    bpy.ops.object.light_add(type="POINT", location=(loc[0], loc[1], loc[2] + 0.1)); l = bpy.context.object
    l.data.energy = 120; l.data.color = srgb("#ffd59a")[:3]; l.data.shadow_soft_size = r

def ref_floor(mat, size=60):
    o = floor(mat, size); return o

# ======================================================================
if FRAME == "A":   # THE MIRROR — REF_18 (centred figure from behind, single mirror), REF_06 (top shaft + long shadow), REF_01 (receding arches), REF_05 (silhouette)
    ref_floor(M_STONE)
    # layered architecture: receding KHAYBAR arches behind the mirror (background), basalt walls, walnut wainscot (mid)
    for k, y in enumerate([5.0, 8.0, 11.0, 14.0]):
        arch_curve(f"BgArch{k}", 3.4, 5.6, 0.07, 0.1, M_GOLD if k == 0 else M_BASALT, (0, y, 0))
        for sx in (-1, 1): box(f"BgPier{k}{sx}", (sx * 2.15, y, 3.0), (0.9, 0.6, 6.0), M_BASALT, 0.02)
    box("FarWall", (0, 15.5, 4), (12, 0.3, 8), M_BASALT)
    for sx in (-1, 1):
        box(f"SideWall{sx}", (sx * 3.2, 7, 4), (0.3, 18, 8), M_BASALT)
        wall_panels(f"Wains{sx}", sx * 3.04, -2, 14, 0, 1.4, -sx, M_PANEL, M_GOLD)
    mirror_w, mirror_h = 1.8, 3.4
    arch_panel("MirrorGlass", mirror_w, mirror_h, (0, 2.98, 0.3), M_MIRROR2)
    arch_curve("MirrorFrame", mirror_w + 0.1, mirror_h + 0.05, 0.07, 0.1, M_GOLD, (0, 2.95, 0.27))
    arch_curve("MirrorFrameInner", mirror_w - 0.02, mirror_h - 0.01, 0.02, 0.1, M_GOLD, (0, 2.93, 0.3))
    box("Plinth", (0, 2.95, 0.15), (2.3, 0.55, 0.3), M_BASALT, 0.015)
    box("Backing", (0, 3.06, 2.0), (2.0, 0.08, 3.6), M_BASALT)
    h, rig = human((0.0, 1.55, 0), 180, arms_down=64, head_bow=4)
    focus = bpy.data.objects.new("Focus", None); bpy.context.collection.objects.link(focus); focus.location = (0, 1.55, 1.4)
    # REF_06/18: single cold top shaft on the figure -> long shadow toward camera; face never lit (back to camera)
    spot("TopShaft", (0.0, 2.15, 7.5), (0.0, 1.45, 0.0), 3400, srgb("#d7e3e6"), angle=10, blend=0.35, radius=0.12)
    # REF_01: distant warm practicals in the receding arches (depth layers)
    for k, y in enumerate([8.0, 11.0, 14.0]):
        for sx in (-1, 1): no_reflect(area(f"Practical{k}{sx}", (sx * 1.6, y - 0.4, 2.6), (math.radians(90), 0, math.radians(180 if sx < 0 else 0)), 0.25, 18 + k * 6, GOLD))
    no_reflect(area("FrameWarm", (0, 0.4, 1.6), (math.radians(90), 0, 0), 1.4, 22, srgb("#ffd9a6")))  # keeps the gold gold (no teal on frame)
    no_reflect(area("TealSide", (2.6, 3.6, 2.0), (math.radians(90), 0, math.radians(100)), 0.6, 30, srgb("#2DB9B6")))
    no_reflect(area("FloorBounce", (0, 0.2, 0.25), (math.radians(60), 0, 0), 2.5, 35, srgb("#d9c7a8")))   # teal only grazing the far side
    fog(0.012, anis=0.5, loc=(0, 6, 4), scl=(6.2, 22, 8), col=(0.92, 0.89, 0.84, 1))
    camera((0.0, -0.55, 1.3), (0.0, 3.0, 1.95), 30, focus_obj=focus, fstop=2.8)
    sc.view_settings.exposure = 1.5
    glare(0.9, 8, -0.8)

elif FRAME == "B":  # THE FRACTURE — REF_15 (thick glass, bright edges, memories inside reflections, foreground defocus), REF_16 (fracture detail)
    ref_floor(M_STONE)
    box("BackWall", (0, 3.9, 4), (14, 0.3, 8), M_BASALT)
    for k, y in enumerate([4.2]):
        for sx in (-1, 1): box(f"Pier{sx}", (sx * 2.2, 3.7, 3.0), (0.8, 0.5, 6.0), M_BASALT, 0.02)
    mirror_w, mirror_h = 1.8, 3.4
    arch_curve("MirrorFrame", mirror_w + 0.1, mirror_h + 0.05, 0.07, 0.1, M_GOLD, (0, 3.35, 0.27))
    box("Plinth", (0, 3.35, 0.15), (2.3, 0.55, 0.3), M_BASALT, 0.015)
    arch_panel("DarkBacking", mirror_w * 0.99, mirror_h * 0.99, (0, 3.46, 0.3), M_WALNUT)
    bpy.ops.object.light_add(type="POINT", location=(0.2, 3.40, 2.0)); _pl = bpy.context.object; _pl.data.energy = 25; _pl.data.color = srgb("#ffc070")[:3]; _pl.data.shadow_soft_size = 0.05
    # lit environment IN FRONT of the mirror so the shards have something to reflect (REF_15)
    box("FrontWall", (0, -2.2, 4), (14, 0.3, 8), M_PANEL)
    no_reflect(area("FrontWallWash", (0, -0.6, 3.5), (math.radians(-90), 0, 0), 4.0, 260, srgb("#e9d2a8")))
    no_reflect(area("FrontTeal", (2.5, -1.0, 2.0), (math.radians(-90), 0, math.radians(-30)), 1.5, 120, srgb("#2DB9B6")))
    glass = arch_panel("Glass", mirror_w, mirror_h, (0, 3.32, 0.3), M_SHARD2)
    glass.data.materials.append(M_EDGE)  # slot 1 = glass edge (rim of solidify)
    me = glass.data; bm = bmesh.new(); bm.from_mesh(me)
    imp = Vector((0.2, 0, 2.0))
    for i in range(16):
        a = i / 16 * 2 * math.pi + RNG.uniform(-0.18, 0.18); n = Vector((-math.sin(a), 0, math.cos(a)))
        bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], plane_co=imp + Vector((RNG.uniform(-0.03, 0.03), 0, RNG.uniform(-0.03, 0.03))), plane_no=n)
    for rad in (0.1, 0.26, 0.48, 0.78, 1.15, 1.6):
        for j in range(16):
            a = (j + 0.5) / 16 * 2 * math.pi + RNG.uniform(-0.12, 0.12); d = Vector((math.cos(a), 0, math.sin(a)))
            tilt = Vector((math.cos(a + 0.35 * RNG.uniform(-1, 1)), 0, math.sin(a + 0.35 * RNG.uniform(-1, 1))))  # irregular, not perfectly tangent
            bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], plane_co=imp + d * rad * RNG.uniform(0.85, 1.15), plane_no=tilt)
    bmesh.ops.split_edges(bm, edges=bm.edges[:])
    fly = []
    for f in bm.faces:
        c = f.calc_center_median(); dist = (Vector((c.x, 0, c.z)) - imp).length
        shrink = 0.985 if dist < 0.5 else 0.996
        for v in f.verts: v.co = c + (v.co - c) * shrink
        if dist < 1.05 and RNG.random() < 0.78 - dist * 0.5: fly.append(f)
    for f in fly:
        c = f.calc_center_median(); dist = (Vector((c.x, 0, c.z)) - imp).length
        t = RNG.uniform(0.3, 2.2) * (1.25 - dist)
        out = (Vector((c.x, 0, c.z)) - imp).normalized() * 0.55 + Vector((0, -1, 0))
        rot = Euler((RNG.uniform(-1.1, 1.1), RNG.uniform(-0.7, 0.7), RNG.uniform(-1.1, 1.1))).to_matrix()
        for v in f.verts: v.co = c + rot @ (v.co - c) + out * t
    bm.to_mesh(me); bm.free()
    sol = glass.modifiers.new("thick", "SOLIDIFY"); sol.thickness = 0.012; sol.material_offset_rim = 1   # glass thickness w/ edge material
    bev = glass.modifiers.new("bev", "BEVEL"); bev.width = 0.002; bev.limit_method = "ANGLE"
    glass.keyframe_insert("location", frame=1); glass.location.y -= 0.035; glass.keyframe_insert("location", frame=2); sc.frame_set(1)
    sc.render.use_motion_blur = True; sc.render.motion_blur_shutter = 0.5
    # REF_15 foreground: large out-of-focus shards close to camera
    for i in range(6):
        o = shard_mesh(f"FG{i}", RNG.uniform(0.12, 0.22), 900 + i); o.data.materials.clear(); o.data.materials.append(M_SHARD2); o.data.materials.append(M_EDGE)
        o.modifiers["thick"].material_offset_rim = 1
        o.location = (RNG.choice([-1, 1]) * RNG.uniform(0.35, 0.8), RNG.uniform(0.75, 1.25), RNG.uniform(1.2, 2.6))
        o.rotation_euler = (RNG.uniform(-1, 1), RNG.uniform(-1, 1), RNG.uniform(0, 6.28))
    # the figure stands in front of the mirror, so its (faceless, back-lit) reflections appear inside the shards = "memories in the glass"
    h, rig = human((-0.55, 1.75, 0), 15, arms_down=64, head_bow=3)
    spot("TopKey", (-0.55, 2.2, 6.0), (-0.55, 1.6, 0.8), 900, srgb("#d7e3e6"), angle=14, blend=0.5, radius=0.2)
    area("TealKey", (2.0, 0.8, 2.6), (math.radians(78), 0, math.radians(115)), 0.9, 140, srgb("#2DB9B6"))
    no_reflect(area("EdgeKick", (-1.6, 0.3, 2.4), (math.radians(80), 0, math.radians(-110)), 0.5, 70, srgb("#fff1d8")))
    fog(0.01, anis=0.55, loc=(0, 1, 4), scl=(10, 6, 8), col=(0.92, 0.89, 0.84, 1))
    focus = bpy.data.objects.new("Focus", None); bpy.context.collection.objects.link(focus); focus.location = (0.2, 2.55, 2.0)
    camera((0.75, 0.35, 1.7), (0.15, 3.3, 2.05), 32, focus_obj=focus, fstop=2.0)
    sc.view_settings.exposure = 0.8
    glare(0.85, 8, -0.75)

elif FRAME == "C":  # THE COURTROOM — REF_02 (backlit judge vs tall window), REF_03 (chandeliers, raised platform), REF_20/07 (stone arches, window shafts), REF_09 (papers), REF_12 (volumetric)
    ref_floor(M_FLOOR, 80)
    for sx in (-7.5, 7.5):
        for wy in range(-4, 26, 6):
            box(f"WallLow{sx}{wy}", (sx, wy + 3, 3.75), (0.4, 6, 7.5), M_BASALT)
            box(f"WallHigh{sx}{wy}", (sx, wy + 3, 13.25), (0.4, 6, 3.5), M_BASALT)
            box(f"Pier{sx}{wy}", (sx, wy + 1.05, 9.5), (0.4, 2.1, 4.0), M_BASALT)
            box(f"Pier2{sx}{wy}", (sx, wy + 4.95, 9.5), (0.4, 2.1, 4.0), M_BASALT)
        wall_panels(f"Wains{sx}", sx - (0.25 if sx > 0 else -0.25), -3, 22, 0, 2.6, -1 if sx > 0 else 1, M_PANEL, M_GOLD)
    box("Ceiling", (0, 11, 15.2), (16, 34, 0.4), M_WALNUT)
    for y in range(-2, 24, 3): box(f"Beam{y}", (0, y, 14.8), (15, 0.35, 0.5), M_WALNUT, 0.02)
    # REF_02/20: tall arched window behind the judge -> judge read as a backlit silhouette
    box("EndWallL", (-4.6, 24, 7.5), (6.2, 0.5, 15), M_BASALT); box("EndWallR", (4.6, 24, 7.5), (6.2, 0.5, 15), M_BASALT)
    box("EndWallTop", (0, 24, 14.0), (3.0, 0.5, 2.0), M_BASALT)
    arch_curve("WindowArch", 3.0, 10.5, 0.1, 0.1, M_GOLD, (0, 23.7, 2.5))
    for i in range(1, 4): box(f"Mullion{i}", (-1.5 + i * 0.75, 23.8, 7.0), (0.05, 0.05, 9.0), M_BASALT)
    for z in (4.5, 7.0, 9.5): box(f"Transom{z}", (0, 23.8, z), (3.0, 0.05, 0.05), M_BASALT)
    box("Sky", (0, 26, 7.5), (8, 0.2, 15), emissive(srgb("#f7e7c6"), 3.2))
    spot("WindowBeam", (0, 30, 12), (0, 12, 0), 60000, srgb("#f6e6c4"), angle=16, blend=0.3, radius=0.4)
    # colonnade with fluted columns
    for y in range(0, 22, 4):
        for x in (-4.6, 4.6): fluted_column(f"C{x}_{y}", x, y, 11.0, 0.42, M_BASALT)
    # judicial platform with steps, bench with gold rail, witness stand, accused dock
    for i, (y, z, w) in enumerate([(18.2, 0.15, 9.0), (18.7, 0.45, 8.5), (19.2, 0.75, 8.0)]): box(f"Step{i}", (0, y + 1.4, z), (w, 3.4 - i * 0.5, 0.3), M_BASALT, 0.01)
    box("JudgeBench", (0, 19.6, 1.95), (6.0, 1.1, 2.1), M_WALNUT, 0.02)
    for i in range(6): box(f"BenchPanel{i}", (-2.5 + i * 1.0, 19.03, 1.9), (0.8, 0.04, 1.5), M_PANEL, 0.01)
    box("BenchRail", (0, 19.0, 3.02), (6.1, 0.1, 0.1), M_GOLD, 0.01)
    box("Witness", (4.0, 15.5, 1.0), (1.8, 1.8, 2.0), M_WALNUT, 0.02)
    box("WitnessRail", (4.0, 14.58, 2.02), (1.85, 0.07, 0.07), M_GOLD)
    box("AccusedPlatform", (0, 8.5, 0.18), (2.8, 2.2, 0.36), M_BASALT, 0.02)
    box("AccusedRail", (0, 7.35, 1.15), (2.8, 0.08, 0.08), M_GOLD)
    for k in range(9): box(f"Baluster{k}", (-1.35 + k * 0.3375, 7.35, 0.75), (0.05, 0.05, 0.8), M_GOLD)
    for y in (2.0, 3.6, 5.2):
        for x in (-2.7, 2.7): pew(f"Pew{x}_{y}", x, y, 3.2, M_WALNUT)
    # REF_03 chandeliers
    for y in (6.0, 14.0):
        for x in (-2.8, 2.8): chandelier(f"Ch{x}_{y}", (x, y, 7.2))
    # gavel on bench
    bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=0.08, depth=0.34, location=(1.3, 19.4, 3.15), rotation=(0, math.radians(90), 0)); link(bpy.context.object, M_WALNUT)
    bpy.ops.mesh.primitive_torus_add(major_radius=0.081, minor_radius=0.013, location=(1.3, 19.4, 3.15), rotation=(0, math.radians(90), 0)); link(bpy.context.object, M_GOLD)
    j, jr = human((0, 20.5, 0.9), 180, arms_down=62)
    w, wr = human((4.0, 15.9, 0.0), 215, arms_down=63)
    a, ar = human((0, 8.6, 0.36), 0, arms_down=64, head_bow=8)
    # REF_09: larger evidence papers inside the shafts, some near camera
    sd = Vector((-0.6, 0.18, -0.78)).normalized()
    for i in range(22):
        wy = RNG.choice([2, 8, 14]); t = RNG.uniform(3.0, 8.5)
        pos = Vector((7.5, wy + 3.0, 9.5)) + sd * t + Vector((RNG.uniform(-0.4, 0.4), RNG.uniform(-0.5, 0.5), RNG.uniform(-0.4, 0.4)))
        bpy.ops.mesh.primitive_plane_add(size=0.5, location=tuple(pos), rotation=(RNG.uniform(-1.2, 1.2), RNG.uniform(-1.2, 1.2), RNG.uniform(0, 6.28)))
        pp = bpy.context.object; pp.scale = (0.72, 1, 1); link(pp, M_PAPER)
        b2 = pp.modifiers.new("bend", "SIMPLE_DEFORM"); b2.deform_method = "BEND"; b2.angle = math.radians(RNG.uniform(-40, 40))
        sb = pp.modifiers.new("s", "SUBSURF"); sb.levels = 2; sb.render_levels = 2; sb.subdivision_type = "SIMPLE"
    for wy in range(-4, 26, 6):
        win = Vector((7.5, wy + 3.0, 9.5))
        spot(f"Win{wy}", tuple(win - sd * 6.0), tuple(win + sd * 4.0), 45000, srgb("#f4e2bd"), angle=13, blend=0.25, radius=0.15)
    area("WitnessRim", (6.5, 17.5, 3.5), (math.radians(80), 0, math.radians(140)), 1.0, 200, srgb("#5fd3cf"))
    area("AccusedTop", (0, 8.5, 6), (0, 0, 0), 1.2, 160, srgb("#d7e3e6"))
    for l in bpy.data.objects:
        if l.type == "LIGHT" and not (l.name.startswith("Win") or l.name == "WindowBeam"): l.visible_volume_scatter = False
    fog(0.03, anis=0.3, loc=(0, 10, 7.4), scl=(14.8, 30, 14.6), col=(0.92, 0.89, 0.84, 1))
    focus = bpy.data.objects.new("Focus", None); bpy.context.collection.objects.link(focus); focus.location = (0, 8.6, 1.5)
    camera((0.0, -1.6, 2.6), (0.0, 18, 4.6), 26, focus_obj=focus, fstop=5.6)
    sc.view_settings.exposure = 0.7
    glare(0.9, 8, -0.8)

bpy.ops.render.render(write_still=True)
print("RENDERED", OUT)
