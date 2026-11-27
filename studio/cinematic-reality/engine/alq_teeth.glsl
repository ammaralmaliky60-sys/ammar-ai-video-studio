// ---- upper anterior teeth (canine-to-canine, labial view) with fixed orthodontic appliance ----
// Proportions: central incisor 8.5, lateral 6.5, canine 7.5 (relative widths); crown heights 10.5/9/10.
// Brackets centred on the labial crown surface, stainless archwire through the slots, coloured elastic ligatures.
uniform float uScale;     // pop-in
uniform vec4 uBrA;        // bracket scale, teeth 0..3
uniform vec2 uBrB;        // bracket scale, teeth 4..5
uniform float uWire;      // archwire draw progress 0..1 (right -> left)
uniform float uSheen;
uniform vec3 uAccent;

float sdBox(vec3 p, vec3 b){ vec3 q = abs(p) - b; return length(max(q,0.0)) + min(max(q.x,max(q.y,q.z)),0.0); }
float sdRBox(vec3 p, vec3 b, float r){ return sdBox(p, b - r) - r; }
mat2 rot(float a){ float c = cos(a), s = sin(a); return mat2(c, -s, s, c); }

const float ARCH = 0.16;                 // arch curvature: z = -ARCH*x^2
float archZ(float x){ return -ARCH*x*x; }
void tooth(int i, out float cx, out float hw, out float hh, out float typ){
  float w[6] = float[6](0.75, 0.65, 0.85, 0.85, 0.65, 0.75);
  float hgt[6] = float[6](1.00, 0.90, 1.05, 1.05, 0.90, 1.00);
  float x = -(0.75+0.65+0.85+0.85+0.65+0.75 + 5.0*0.04)*0.5;
  cx = 0.0; hw = 0.4; hh = 0.5;
  for (int k = 0; k < 6; k++) { if (k == i) { cx = x + w[k]*0.5; hw = w[k]*0.5; hh = hgt[k]*0.5; } x += w[k] + 0.04; }
  typ = (i == 0 || i == 5) ? 1.0 : 0.0;
}
float lift(float cx){ return abs(cx) > 0.6 ? 0.06 : 0.0; }   // smile arc: laterals/canines slightly higher
float brScale(int i){ return i < 4 ? uBrA[i] : uBrB[i - 4]; }
const float BRY = -0.02;                 // bracket / wire height on the crown

// returns (distance, material) 1 enamel, 2 gum, 3 bracket metal, 4 wire, 5 ligature
vec2 map(vec3 p){
  p /= max(uScale, 1e-3);
  vec2 res = vec2(1e9, 0.0);
  float near = 1e9, mg = 0.0, top = 0.0;
  for (int i = 0; i < 6; i++) {
    float cx, hw, hh, typ; tooth(i, cx, hw, hh, typ);
    float z0 = archZ(cx); float ang = atan(2.0*ARCH*cx);        // follow the arch tangent
    vec3 q = p - vec3(cx, 0.0, z0); q.xz = rot(-ang)*q.xz;
    q.y -= lift(cx);
    float bulge = 0.05*(1.0 - (q.x*q.x)/(hw*hw));               // labial convexity
    float d = sdRBox(q - vec3(0.0, 0.0, -0.05), vec3(hw*0.94, hh, 0.20 + bulge), 0.19);
    d = max(d, abs(q.x) - hw*0.94*(1.0 - 0.18*smoothstep(-0.1, hh, q.y)));   // narrower cervical third
    if (typ > 0.5) { float cusp = (-q.y - hh) + abs(q.x)*0.55 + 0.10; d = max(d, cusp*0.8); }  // canine cusp
    if (d < res.x) res = vec2(d, 1.0);
    // gingival margin of the nearest tooth: zenith over the crown, papilla between teeth
    float dx = p.x - cx;
    if (abs(dx) < near) { near = abs(dx);
      float u = clamp(dx/(hw + 0.02), -1.0, 1.0);
      mg = hh + lift(cx) - 0.10 - 0.26*u*u; top = 0.80; }
    // bracket + ligature
    float s = brScale(i);
    if (s > 0.001) {
      vec3 bq = (q - vec3(0.0, BRY, 0.22 + bulge*0.9))/s;
      float br = sdRBox(bq, vec3(0.15, 0.13, 0.06), 0.03);
      br = max(br, -sdBox(bq - vec3(0.0, 0.0, 0.05), vec3(0.2, 0.025, 0.05)));        // archwire slot
      br = min(br, sdRBox(bq - vec3(0.0, 0.0, -0.04), vec3(0.11, 0.17, 0.03), 0.02)); // tie wings
      br *= s;
      if (br < res.x) res = vec2(br, 3.0);
      float lg = (length(vec2(length(bq.xy*vec2(1.0, 1.15)) - 0.15, bq.z - 0.02)) - 0.03)*s;
      if (lg < res.x) res = vec2(lg, 5.0);
    }
  }
  // continuous gingiva band following the arch
  float zl = p.z - archZ(p.x) + 0.02;
  // rounded 3-axis band: lower edge = scalloped margin, short height, rounded top and ends
  float hy = 0.5*(top - mg), cy = 0.5*(top + mg);
  vec3 w = vec3(abs(p.x) - 2.35, abs(p.y - cy) - hy, abs(zl) - 0.26);
  float g = length(max(w, 0.0)) + min(max(w.x, max(w.y, w.z)), 0.0) - 0.08;
  g *= 0.8;
  if (g < res.x) res = vec2(g, 2.0);
  // archwire at bracket height, drawn right -> left
  if (uWire > 0.0) {
    float xmax = 2.35; float xEnd = mix(xmax, -xmax, uWire);
    float zf = archZ(p.x) + 0.30;
    float wd = length(vec2(p.y - BRY - 0.06*smoothstep(0.5, 0.8, abs(p.x)), (p.z - zf)/sqrt(1.0 + 4.0*ARCH*ARCH*p.x*p.x))) - 0.022;
    wd = max(wd, abs(p.x) - xmax);
    wd = max(wd, xEnd - p.x);
    if (wd*0.9 < res.x) res = vec2(wd*0.9, 4.0);
  }
  res.x *= max(uScale, 1e-3);
  return res;
}
vec3 nrm(vec3 p){ vec2 e = vec2(0.0012, 0.0);
  return normalize(vec3(map(p+e.xyy).x-map(p-e.xyy).x, map(p+e.yxy).x-map(p-e.yxy).x, map(p+e.yyx).x-map(p-e.yyx).x)); }
vec3 envStudio(vec3 r){
  float up = r.y*0.5 + 0.5;
  vec3 c = mix(vec3(0.03, 0.02, 0.03), vec3(0.35, 0.33, 0.34), smoothstep(0.35, 0.9, up));
  c += vec3(2.4)*smoothstep(0.95, 0.985, dot(r, normalize(vec3(-0.5, 0.6, 0.6))));
  c += vec3(3.0,2.8,2.5)*smoothstep(0.03, 0.0, abs(r.x*0.7 + r.y*0.3 - mix(-1.2, 1.2, uSheen)))*0.6;
  return c;
}

void main(){
  vec3 ro, rd; camRay(gl_FragCoord.xy, ro, rd);
  vec4 o = vec4(0.0);
  if (uScale > 0.002) {
    float t = 0.0; vec2 h = vec2(1.0, 0.0); bool hit = false; float best = 1e9, tb = 0.0;
    float pa = 2.0*tan(radians(uFov)*0.5)/uRes.y;
    for (int i = 0; i < 140; i++) {
      h = map(ro + rd*t);
      if (h.x < 0.0004*t) { hit = true; break; }
      float r = h.x/(t*pa); if (r < best) { best = r; tb = t; }
      t += h.x*0.85; if (t > 40.0) break;
    }
    float cov = hit ? 1.0 : 1.0 - smoothstep(0.0, 1.0, best);
    if (!hit && cov > 0.02) { t = tb; h = map(ro + rd*t); }
    if (cov > 0.02) {
      vec3 p = ro + rd*t; vec3 n = nrm(p); vec3 v = -rd;
      vec3 L = normalize(vec3(-0.35, 0.65, 0.75)); vec3 L2 = normalize(vec3(0.7, 0.1, 0.6));
      vec3 env = envStudio(reflect(rd, n));
      float fr = pow(1.0 - SAT(dot(n, v)), 5.0);
      float dl = SAT(dot(n, L)), dl2 = SAT(dot(n, L2));
      vec3 c; float id = h.y;
      if (id < 1.5) {                       // enamel: warm white, translucent incisal edge, clear coat
        vec3 pp = p/max(uScale, 1e-3);
        float incisal = smoothstep(-0.25, -0.55, pp.y);
        vec3 base = mix(vec3(0.92, 0.88, 0.80), vec3(0.78, 0.82, 0.86), incisal*0.6);
        float wrap = SAT((dot(n, L) + 0.35)/1.35);
        c = base*(0.22 + 0.95*wrap + 0.35*dl2) + env*(0.04 + 0.35*fr) + vec3(1.3)*ggx(n, v, L, 0.22)*0.55;
      } else if (id < 2.5) {               // gingiva
        vec3 base = vec3(0.80, 0.42, 0.46);
        c = base*(0.25 + 0.9*SAT((dot(n, L) + 0.3)/1.3)) + env*0.05*(0.3 + fr) + vec3(0.8)*ggx(n, v, L, 0.35)*0.3;
      } else if (id < 4.5) {               // stainless steel (brackets + wire)
        vec3 base = vec3(0.80, 0.82, 0.86);
        c = base*env*(0.6 + 0.4*fr) + base*0.15*dl + vec3(1.8)*ggx(n, v, L, 0.12)*0.8;
      } else {                              // elastic ligature in the brand accent
        c = uAccent*(0.25 + 1.1*dl) + vec3(1.0)*ggx(n, v, L, 0.25)*0.4;
      }
      o = vec4(c*cov, cov);
    }
  }
  outColor = o;
}
