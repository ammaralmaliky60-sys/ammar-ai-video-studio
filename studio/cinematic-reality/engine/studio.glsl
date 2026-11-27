// ---- bright infinite studio (cyclorama) with physically simulated glossy spheres ----
#define NS 40
uniform vec4 uSph[NS];    // xyz centre, w radius (w<=0: unused)
uniform vec4 uSphC[NS];   // rgb albedo (linear), a roughness
uniform float uWallZ;     // back wall z (negative)
uniform float uLightAmt;

const vec3 KEY = vec3(1.0,0.96,0.90);
vec3 envStudio(vec3 r){
  // white studio with a big softbox overhead-left and a strip light on the right
  float up = SAT(r.y*0.5+0.5);
  vec3 c = mix(vec3(0.55,0.54,0.52), vec3(0.95,0.94,0.92), up);
  vec3 sb = normalize(vec3(-0.45, 0.85, 0.25));
  c += KEY*6.0*smoothstep(0.90, 0.96, dot(r, sb));
  vec3 st = normalize(vec3(0.9, 0.3, 0.1));
  c += KEY*3.0*smoothstep(0.97, 0.985, dot(r, st));
  return c;
}
float sdCyc(vec3 p){
  // floor y=0 blending into a back wall at z=uWallZ with a 3 m cove
  float R = 3.0;
  vec2 q = vec2(p.z - (uWallZ + R), p.y - R);
  float cove = (q.x < 0.0 && q.y < 0.0) ? R - length(q) : 1e5;
  float d = min(p.y, p.z - uWallZ);
  if (p.z < uWallZ + R && p.y < R) d = R - length(vec2(min(q.x,0.0), min(q.y,0.0)));
  return d;
}
float traceCyc(vec3 ro, vec3 rd){
  float t = 0.0;
  for (int i = 0; i < 64; i++) {
    float d = sdCyc(ro + rd*t);
    if (d < 0.001*t + 0.001) return t;
    t += d; if (t > 200.0) break;
  }
  return 1e5;
}
vec3 cycNormal(vec3 p){
  vec2 e = vec2(0.002, 0.0);
  return normalize(vec3(sdCyc(p+e.xyy)-sdCyc(p-e.xyy), sdCyc(p+e.yxy)-sdCyc(p-e.yxy), sdCyc(p+e.yyx)-sdCyc(p-e.yyx)));
}
float sphHit(vec3 ro, vec3 rd, vec4 s){
  vec3 oc = ro - s.xyz; float b = dot(oc, rd); float c = dot(oc,oc) - s.w*s.w; float h = b*b - c;
  if (h < 0.0) return -1.0; return -b - sqrt(h);
}
float sphSoftShadow(vec3 ro, vec3 rd, vec4 s, float k){
  vec3 oc = ro - s.xyz; float b = dot(oc, rd); float c = dot(oc,oc) - s.w*s.w; float h = b*b - c;
  float d = sqrt(max(0.0, s.w*s.w - h)) - s.w; float t = -b - sqrt(max(h, 0.0));
  return (b > 0.0) ? 1.0 : smoothstep(0.0, 1.0, 2.5*k*d/max(t,1e-3));
}
float sphOcc(vec3 p, vec3 n, vec4 s){
  vec3 r = s.xyz - p; float l = length(r);
  return SAT(dot(n, r)*s.w*s.w/(l*l*l));
}
int hitSpheres(vec3 ro, vec3 rd, out float tmin){
  tmin = 1e5; int id = -1;
  for (int i = 0; i < NS; i++) {
    if (uSph[i].w <= 0.0) continue;
    float t = sphHit(ro, rd, uSph[i]);
    if (t > 0.0 && t < tmin) { tmin = t; id = i; }
  }
  return id;
}
vec3 lightAt(vec3 p, vec3 n, int self){
  vec3 L = normalize(vec3(-0.45, 0.85, 0.25));
  float sh = 1.0, occ = 0.0;
  for (int i = 0; i < NS; i++) {
    if (i == self || uSph[i].w <= 0.0) continue;
    sh *= sphSoftShadow(p, L, uSph[i], 2.2);
    occ += sphOcc(p, n, uSph[i]);
  }
  float dif = SAT(dot(n, L));
  float ao = SAT(1.0 - occ*1.1);
  return KEY*dif*sh*2.2*uLightAmt + mix(vec3(0.42,0.42,0.43), vec3(0.75,0.75,0.74), n.y*0.5+0.5)*ao*0.9*uLightAmt;
}
vec3 shadeScene(vec3 ro, vec3 rd, out float depth, bool second){
  float ts; int id = hitSpheres(ro, rd, ts);
  float tc = traceCyc(ro, rd);
  vec3 col;
  if (id >= 0 && ts < tc) {
    vec4 s = uSph[id]; vec3 p = ro + rd*ts; vec3 n = normalize(p - s.xyz);
    vec3 alb = uSphC[id].rgb; float rough = uSphC[id].a;
    vec3 r = reflect(rd, n);
    vec3 env = envStudio(r);
    if (!second) {
      // one-bounce reflection of floor/other spheres
      float tr; int j = hitSpheres(p + n*0.002, r, tr);
      float tcr = traceCyc(p + n*0.002, r);
      if (j >= 0 && tr < tcr) env = uSphC[j].rgb*lightAt(p + r*tr, normalize(p + r*tr - uSph[j].xyz), j);
      else if (tcr < 1e4) { vec3 pf = p + r*tcr; env = vec3(0.82)*lightAt(pf, cycNormal(pf), -1); }
    }
    float fr = fresnelS(dot(n, -rd), 0.04);
    vec3 L = normalize(vec3(-0.45, 0.85, 0.25));
    col = alb*lightAt(p, n, id)*(1.0-fr) + env*mix(fr, fr*0.3, rough) + KEY*ggx(n, -rd, L, max(rough,0.06))*fr*12.0*uLightAmt;
    depth = ts;
  } else if (tc < 1e4) {
    vec3 p = ro + rd*tc; vec3 n = cycNormal(p);
    vec3 alb = vec3(0.80,0.79,0.77);
    col = alb*lightAt(p, n, -1);
    // faint glossy floor reflection of spheres
    if (!second && p.y < 0.01) {
      vec3 r = reflect(rd, n); float tr; int j = hitSpheres(p + n*0.002, r, tr);
      if (j >= 0) col = mix(col, uSphC[j].rgb*0.6, 0.12*exp(-tr*0.6));
    }
    depth = tc;
  } else { col = envStudio(rd); depth = 500.0; }
  return col;
}
void main(){
  vec3 ro, rd; camRay(gl_FragCoord.xy, ro, rd);
  float depth;
  vec3 col = shadeScene(ro, rd, depth, false);
  float tt = txtTrace(ro, rd, depth);
  float tcov = 1.0;
  if (tt < 0.0 && gTxtCov > 0.02) { tt = gTxtT; tcov = gTxtCov; }
  if (tt > 0.0) {
    vec3 colBg = col; float depthBg = depth;
    vec3 q = ro + rd*tt; vec3 n = txtNormal(q);
    vec3 env = envStudio(reflect(rd, n));
    col = mix(colBg, txtShade(q, n, rd, env, KEY*1.4, normalize(vec3(-0.45,0.85,0.25)), vec3(0.45)), tcov); depth = tcov > 0.5 ? tt : depthBg;
  }
  outColor = vec4(col, depth);
}
