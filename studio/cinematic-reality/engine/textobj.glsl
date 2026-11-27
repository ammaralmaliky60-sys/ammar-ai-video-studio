// ---- extruded 3D text object (SDF textures, morphable) ----
uniform sampler2D uTxtA;
uniform sampler2D uTxtB;
uniform vec4 uTxtBox;     // xy = world size of texture rect (w,h), z = sdf range (world units for 0..1 of encoded value), w = visible (0/1)
uniform vec4 uTxtPos;     // xyz centre, w = uniform scale
uniform vec4 uTxtRot;     // x = yaw, y = pitch, z = morph A->B (0..1), w = extrude half-depth
uniform vec4 uTxtCol;     // rgb base colour (linear), a = roughness
uniform vec4 uTxtMat;     // x = metallic, y = reveal (0..1, right->left), z = edge glow, w = bevel
uniform vec4 uTxtCol2;    // second colour for paint wipe, a = wipe progress (0..1, top->bottom)
uniform float uTxtDir;    // 1 = reveal right->left (Arabic), -1 = left->right (Latin)
uniform float uTxtFill;   // front fill light from the camera

mat3 txtRotM(){
  float cy = cos(uTxtRot.x), sy = sin(uTxtRot.x), cp = cos(uTxtRot.y), sp = sin(uTxtRot.y);
  mat3 ry = mat3(cy,0.,-sy, 0.,1.,0., sy,0.,cy);
  mat3 rx = mat3(1.,0.,0., 0.,cp,sp, 0.,-sp,cp);
  return ry*rx;
}
float txt2d(vec2 xy){
  vec2 uv = xy/uTxtBox.xy + 0.5;
  vec2 q = abs(xy) - uTxtBox.xy*0.5;
  float outside = length(max(q,0.0));
  vec2 c = clamp(uv, vec2(0.002), vec2(0.998));
  float a = (textureLod(uTxtA, c, 0.0).r - 0.5)*uTxtBox.z;
  float b = (textureLod(uTxtB, c, 0.0).r - 0.5)*uTxtBox.z;
  return mix(a, b, uTxtRot.z) + outside;
}
float txtSDF(vec3 pw){
  vec3 p = transpose(txtRotM())*(pw - uTxtPos.xyz)/uTxtPos.w;
  float d2 = txt2d(p.xy);
  float bev = uTxtMat.w;
  vec2 w = vec2(d2 + bev, abs(p.z) - uTxtRot.w + bev);
  float d = min(max(w.x,w.y),0.0) + length(max(w,0.0)) - bev;
  // assembly reveal: right -> left (Arabic reading order)
  float dir = uTxtDir < 0.0 ? -1.0 : 1.0;
  float xr = mix(uTxtBox.x*0.55, -uTxtBox.x*0.55, uTxtMat.y)*dir;
  d = max(d, (xr - p.x)*dir);
  return d*uTxtPos.w;
}
vec3 txtNormal(vec3 p){
  vec2 e = vec2(0.0045*uTxtPos.w, 0.0);
  return normalize(vec3(txtSDF(p+e.xyy)-txtSDF(p-e.xyy), txtSDF(p+e.yxy)-txtSDF(p-e.yxy), txtSDF(p+e.yyx)-txtSDF(p-e.yyx)));
}
float gTxtCov = 0.0; float gTxtT = 0.0;
// returns t (or -1); on a near miss sets gTxtCov (edge coverage) and gTxtT
float txtTraceAA(vec3 ro, vec3 rd, float tmax, out float cov){ float t = -1.0; return t; }
float txtTrace(vec3 ro, vec3 rd, float tmax){
  if (uTxtBox.w < 0.5 || uTxtMat.y <= 0.0) return -1.0;
  // bounding sphere
  vec3 oc = ro - uTxtPos.xyz; float R = 0.6*length(uTxtBox.xy)*uTxtPos.w + uTxtRot.w*uTxtPos.w;
  float b = dot(oc, rd); float c = dot(oc,oc) - R*R; float h = b*b - c;
  if (h < 0.0) return -1.0;
  h = sqrt(h); float t = max(-b - h, 0.0); float t1 = -b + h;
  float pa = 2.0*tan(radians(uFov)*0.5)/uRes.y;
  float best = 1e9;
  for (int i = 0; i < 110; i++) {
    float d = txtSDF(ro + rd*t);
    if (d < 0.0003*t) { gTxtCov = 1.0; return t; }
    float r = d/(t*pa);
    if (r < best) { best = r; gTxtT = t; }
    t += d*0.9;
    if (t > t1 || t > tmax) break;
  }
  gTxtCov = 1.0 - smoothstep(0.0, 1.0, best);
  if (gTxtT > tmax) gTxtCov = 0.0;
  return -1.0;
}
// local coordinate (for paint wipe)
vec3 txtLocal(vec3 pw){ return transpose(txtRotM())*(pw - uTxtPos.xyz)/uTxtPos.w; }
float txtWipe(vec3 lp){ return smoothstep(-0.03, 0.03, lp.y - mix(uTxtBox.y*0.7, -uTxtBox.y*0.7, uTxtCol2.a)); }
float txtEdge(vec3 lp){
  float dir = uTxtDir < 0.0 ? -1.0 : 1.0;
  float xr = mix(uTxtBox.x*0.55, -uTxtBox.x*0.55, uTxtMat.y)*dir;
  return smoothstep(0.10, 0.0, (lp.x - xr)*dir)*(1.0-step(0.999, uTxtMat.y));
}
// generic PBR shading of the text given an environment lookup colour
vec3 txtShade(vec3 q, vec3 n, vec3 rd, vec3 env, vec3 sunCol, vec3 sunDir, vec3 amb){
  vec3 lp = txtLocal(q);
  vec3 base = mix(uTxtCol.rgb, uTxtCol2.rgb, txtWipe(lp));
  float rough = uTxtCol.a; float met = uTxtMat.x;
  vec3 v = -rd;
  vec3 F0 = mix(vec3(0.04), base, met);
  float fr = pow(1.0-SAT(dot(n,v)),5.0);
  vec3 F = F0 + (1.0-F0)*fr;
  vec3 kd = (1.0-F)*(1.0-met);
  float ndl = SAT(dot(n, sunDir));
  vec3 c = kd*base*(ndl*sunCol + amb) + F*env*mix(1.0, 0.25, rough) + sunCol*ggx(n, v, sunDir, max(rough,0.04))*F;
  c += kd*base*SAT(dot(n, v))*uTxtFill;
  c += vec3(0.04 + 0.96*fr)*env*0.18*(1.0-met);   // clear coat
  c += vec3(1.0,0.72,0.38)*uTxtMat.z*txtEdge(lp)*4.0;
  return c;
}
