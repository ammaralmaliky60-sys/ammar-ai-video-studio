"""
THE COURT WITHIN — GATE 3A Look-Development frames (Blender 4.2 LTS, Cycles CPU).
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
    b.inputs["Base Color"].default_value = srgb("#3a2c25"); b.inputs["Roughness"].default_value = 0.6
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

# ======================================================================
if FRAME == "A":   # THE MIRROR
    floor(M_FLOOR)
    box("BackWall", (0, 3.2, 4), (14, 0.3, 8), M_WALNUT)
    for x in (-2.6, 2.6): column(f"Col{x}", x, 2.6, 7.5, 0.32, M_BASALT)
    mirror_w, mirror_h = 1.7, 3.3
    arch_panel("MirrorGlass", mirror_w, mirror_h, (0, 2.98, 0.25), M_MIRROR)
    arch_curve("MirrorFrame", mirror_w + 0.08, mirror_h + 0.04, 0.06, 0.1, M_GOLD, (0, 2.95, 0.23))
    arch_curve("MirrorFrameInner", mirror_w - 0.04, mirror_h - 0.02, 0.018, 0.1, M_GOLD, (0, 2.93, 0.25))
    box("Plinth", (0, 2.95, 0.12), (2.2, 0.5, 0.24), M_BASALT, 0.01)
    h, rig = human((0.42, 1.25, 0), 180 + 10, arms_down=62, head_bow=7)
    focus = bpy.data.objects.new("Focus", None); bpy.context.collection.objects.link(focus); focus.location = (0, 2.98, 1.75)
    # lighting: cold motivated top spill, warm rim on shoulders only (head stays in shadow = faceless),
    # warm kick so the aged gold reads gold (not green) — teal kept for reflections only
    spot("TopKey", (0.1, 2.6, 6.5), (0.0, 2.95, 1.2), 380, srgb("#bcd6dc"), angle=13, blend=0.6, radius=0.3)
    area("RimL", (-1.3, 1.9, 1.35), (math.radians(90), 0, math.radians(-130)), 0.45, 120, GOLD)
    area("RimR", (1.6, 2.0, 1.3), (math.radians(90), 0, math.radians(130)), 0.4, 35, srgb("#5fd3cf"))
    no_reflect(area("FrameKick", (0.0, 0.2, 0.6), (math.radians(80), 0, 0), 0.6, 45, srgb("#ffd9a0")))
    area("MirrorWash", (0, 1.8, 4.8), (math.radians(-35), 0, 0), 1.2, 25, srgb("#2DB9B6"))
    spot("WindowShaft", (-4.0, -0.5, 9), (-1.25, 2.6, 0), 9000, srgb("#e8d9b8"), angle=9, blend=0.15, radius=0.02)
    fog(0.008)
    camera((-0.15, -0.35, 1.5), (0.05, 2.9, 1.9), 35, focus_obj=focus, fstop=2.0, shift_y=0.0)
    sc.view_settings.exposure = 0.6
    glare(0.85, 8, -0.8)

elif FRAME == "B":  # THE FRACTURE
    floor(M_FLOOR)
    box("BackWall", (0, 3.6, 4), (14, 0.3, 8), M_WALNUT)
    mirror_w, mirror_h = 1.7, 3.3
    arch_curve("MirrorFrame", mirror_w + 0.08, mirror_h + 0.04, 0.06, 0.1, M_GOLD, (0, 3.35, 0.23))
    box("Plinth", (0, 3.35, 0.12), (2.2, 0.5, 0.24), M_BASALT, 0.01)
    # warm light only behind the glass: visible exclusively through the cracks
    arch_panel("GlowBehind", mirror_w * 0.99, mirror_h * 0.99, (0, 3.42, 0.25), emissive(srgb("#ffbf6a"), 0.9))
    no_reflect(area("BehindMirror", (0, 3.55, 2.0), (math.radians(-90), 0, 0), 1.2, 260, srgb("#f2c879")))
    # --- fracture: bisect the arch panel with radial + concentric (tangent) planes through the impact point
    glass = arch_panel("Glass", mirror_w, mirror_h, (0, 3.32, 0.25), M_SHARD)
    me = glass.data; bm = bmesh.new(); bm.from_mesh(me)
    imp = Vector((0.18, 0, 1.95))
    for i in range(14):
        a = i / 14 * 2 * math.pi + RNG.uniform(-0.15, 0.15); n = Vector((-math.sin(a), 0, math.cos(a)))
        bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], plane_co=imp, plane_no=n)
    for rad in (0.12, 0.3, 0.55, 0.85, 1.25):
        for j in range(14):
            a = (j + 0.5) / 14 * 2 * math.pi + RNG.uniform(-0.1, 0.1); d = Vector((math.cos(a), 0, math.sin(a)))
            bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], plane_co=imp + d * rad * RNG.uniform(0.85, 1.15), plane_no=d)
    bmesh.ops.split_edges(bm, edges=bm.edges[:])
    fly = []
    for f in bm.faces:
        c = f.calc_center_median(); dist = (Vector((c.x, 0, c.z)) - imp).length
        shrink = 0.975 if dist < 0.5 else 0.992                    # thin gaps = visible cracks
        for v in f.verts: v.co = c + (v.co - c) * shrink
        if dist < 1.0 and RNG.random() < 0.75 - dist * 0.45:
            fly.append(f)
    # move flying shards toward camera, with rotation (deterministic)
    for f in fly:
        c = f.calc_center_median(); dist = (Vector((c.x, 0, c.z)) - imp).length
        t = RNG.uniform(0.25, 1.6) * (1.2 - dist)
        out = (Vector((c.x, 0, c.z)) - imp).normalized() * 0.5 + Vector((0, -1, 0))
        rot = Euler((RNG.uniform(-1, 1), RNG.uniform(-0.6, 0.6), RNG.uniform(-1, 1))).to_matrix()
        for v in f.verts: v.co = c + rot @ (v.co - c) + out * t
    bm.to_mesh(me); bm.free()
    sol = glass.modifiers.new("thick", "SOLIDIFY"); sol.thickness = 0.008
    bev = glass.modifiers.new("bev", "BEVEL"); bev.width = 0.0012
    # motion blur on the whole fracture object (slight push toward camera between frames)
    glass.keyframe_insert("location", frame=1); glass.location.y -= 0.03; glass.keyframe_insert("location", frame=2); sc.frame_set(1)
    sc.render.use_motion_blur = True; sc.render.motion_blur_shutter = 0.5
    h, rig = human((-1.05, 0.9, 0), 160, arms_down=62, head_bow=4)
    spot("TopKey", (-0.6, 1.6, 6.0), (-0.8, 1.2, 1.0), 500, srgb("#bcd6dc"), angle=20, blend=0.6, radius=0.3)
    area("Teal", (2.2, 0.6, 2.4), (math.radians(75), 0, math.radians(120)), 1.0, 260, srgb("#2DB9B6"))
    area("GoldRim", (-2.0, 2.6, 2.2), (math.radians(80), 0, math.radians(-60)), 0.6, 160, GOLD)
    fog(0.012, anis=0.6)
    focus = bpy.data.objects.new("Focus", None); bpy.context.collection.objects.link(focus); focus.location = (0.2, 2.6, 1.95)
    camera((0.55, 0.45, 1.6), (0.12, 3.3, 2.0), 30, focus_obj=focus, fstop=2.4)
    sc.view_settings.exposure = 0.4
    glare(0.75, 9, -0.55)

elif FRAME == "C":  # THE COURTROOM
    floor(M_FLOOR, 80)
    L = 30
    # side walls with high window openings (light shafts motivated by real openings)
    for sx in (-7.5, 7.5):
        for wy in range(-4, 26, 6):
            box(f"WallLow{sx}{wy}", (sx, wy + 3, 3.75), (0.4, 6, 7.5), M_WALNUT)
            box(f"WallHigh{sx}{wy}", (sx, wy + 3, 13.25), (0.4, 6, 3.5), M_WALNUT)
            # tall narrow window (1.2 m) between wide piers -> distinct light shafts
            box(f"Pier{sx}{wy}", (sx, wy + 1.05, 9.5), (0.4, 2.1, 4.0), M_WALNUT)
            box(f"Pier2{sx}{wy}", (sx, wy + 4.95, 9.5), (0.4, 2.1, 4.0), M_WALNUT)
    box("Ceiling", (0, 11, 15.2), (16, 34, 0.4), M_WALNUT)
    box("EndWall", (0, 24, 7.5), (16, 0.4, 15), M_WALNUT)
    # KHAYBAR arch motif behind the bench (inlaid gold)
    arch_curve("BenchArch", 5.2, 9.0, 0.09, 0.1, M_GOLD, (0, 23.7, 1.6))
    arch_panel("BenchArchPanel", 5.1, 8.95, (0, 23.75, 1.6), tex_mat("Walnut2", "black_walnut_veneer_01", 0.8, tint=srgb("#5a4537"), rough_mul=0.6))
    # colonnade
    for y in range(-2, 22, 4):
        for x in (-4.6, 4.6): column(f"C{x}_{y}", x, y, 12.5, 0.45, M_BASALT)
    # judge bench + gold rail, witness stand, accused platform
    box("JudgeDais", (0, 21, 0.5), (8, 3.2, 1.0), M_WALNUT, 0.02)
    box("JudgeBench", (0, 20.0, 2.0), (6.5, 1.0, 2.0), M_WALNUT, 0.02)
    box("BenchRail", (0, 19.48, 2.95), (6.6, 0.08, 0.08), M_GOLD, 0.01)
    box("Witness", (4.0, 16.5, 0.9), (1.6, 1.6, 1.8), M_WALNUT, 0.02)
    box("WitnessRail", (4.0, 15.69, 1.78), (1.65, 0.06, 0.06), M_GOLD)
    box("AccusedPlatform", (0, 7.5, 0.15), (2.6, 2.0, 0.3), M_BASALT, 0.02)
    box("AccusedRail", (0, 6.45, 1.05), (2.6, 0.08, 0.08), M_GOLD)
    for x in (-1.25, 1.25): box(f"RailPost{x}", (x, 6.45, 0.65), (0.08, 0.08, 0.8), M_GOLD)
    # benches (rows) for depth
    for y in (2.0, 4.0):
        for x in (-2.6, 2.6): box(f"Pew{x}_{y}", (x, y, 0.5), (3.2, 0.6, 1.0), M_WALNUT, 0.02)
    # gavel on bench
    bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=0.07, depth=0.32, location=(1.2, 19.75, 3.08), rotation=(0, math.radians(90), 0))
    link(bpy.context.object, M_WALNUT)
    bpy.ops.mesh.primitive_torus_add(major_radius=0.071, minor_radius=0.012, location=(1.2, 19.75, 3.08), rotation=(0, math.radians(90), 0))
    link(bpy.context.object, M_GOLD)
    # judge (backlit silhouette) and witness — same body model (identity hidden by light)
    j, jr = human((0, 20.9, 1.0), 180, arms_down=60)
    jr.scale = (1, 1, 1)
    w, wr = human((4.0, 16.9, 0.0), 215, arms_down=62)
    a, ar = human((0, 7.6, 0.3), 0, arms_down=62, head_bow=8)
    # evidence papers suspended INSIDE the light shafts (positions along the window-beam paths, seeded)
    sdp = Vector((-0.6, 0.18, -0.78)).normalized()
    for i in range(18):
        wy = RNG.choice([2, 8, 14]); t = RNG.uniform(3.0, 8.5)
        pos = Vector((7.5, wy + 3.0, 9.5)) + sdp * t + Vector((RNG.uniform(-0.4, 0.4), RNG.uniform(-0.5, 0.5), RNG.uniform(-0.4, 0.4)))
        bpy.ops.mesh.primitive_plane_add(size=0.3, location=tuple(pos), rotation=(RNG.uniform(-1.2, 1.2), RNG.uniform(-1.2, 1.2), RNG.uniform(0, 6.28)))
        pp = bpy.context.object; pp.scale = (0.75, 1, 1); link(pp, M_PAPER)
        sd2 = pp.modifiers.new("bend", "SIMPLE_DEFORM"); sd2.deform_method = "BEND"; sd2.angle = math.radians(RNG.uniform(-35, 35))
        sub = pp.modifiers.new("s", "SUBSURF"); sub.levels = 2; sub.render_levels = 2; sub.subdivision_type = "SIMPLE"
    # light: low sun through the high windows (strong volumetric shafts), cool fill, gold rim on judge
    # motivated window light: one narrow spot outside each right-hand window, aimed through it (sun direction)
    sd = Vector((-0.6, 0.18, -0.78)).normalized()
    for wy in range(-4, 26, 6):
        win = Vector((7.5, wy + 3.0, 9.5))
        spot(f"Win{wy}", tuple(win - sd * 6.0), tuple(win + sd * 4.0), 30000, srgb("#f4e2bd"), angle=13, blend=0.25, radius=0.15)
    area("JudgeBack", (0, 22.6, 6.5), (math.radians(-80), 0, 0), 3.0, 2600, GOLD)
    area("BenchFront", (0, 15.0, 4.5), (math.radians(-70), 0, 0), 2.0, 500, srgb("#e8d9b8"))
    area("WitnessRim", (6.5, 18.5, 3.5), (math.radians(80), 0, math.radians(140)), 1.0, 300, srgb("#5fd3cf"))
    area("AccusedTop", (0, 7.5, 6), (0, 0, 0), 1.5, 220, srgb("#bcd6dc"))
    for l in bpy.data.objects:   # only the sun scatters in the air -> distinct shafts, no flat haze
        if l.type == "LIGHT" and not l.name.startswith("Win"): l.visible_volume_scatter = False
    fog(0.03, anis=0.3, loc=(0, 10, 7.4), scl=(14.8, 30, 14.6))
    focus = bpy.data.objects.new("Focus", None); bpy.context.collection.objects.link(focus); focus.location = (0, 7.6, 1.5)
    camera((0.6, -2.2, 1.45), (0.0, 16, 4.9), 20, focus_obj=focus, fstop=5.6, shift_y=0.0)
    sc.view_settings.exposure = 0.9
    glare(0.9, 8, -0.8)

bpy.ops.render.render(write_still=True)
print("RENDERED", OUT)
