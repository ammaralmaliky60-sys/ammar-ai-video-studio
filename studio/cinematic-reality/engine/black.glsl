// ---- black studio: glossy black floor, volumetric top spotlight, floating dust ----
uniform vec4 uSpot;    // xyz spot position, w intensity (0..1 ramp)
uniform vec4 uSpot2;   // xyz spot target, w cone half-angle (rad)
uniform float uAmbient; // residual room light (fade from room)

float coneAtt(vec3 p, vec3 sp, vec3 sdir, float ang){
  vec3 L = p - sp; float d = length(L);
  float c = dot(L/d, sdir);
  float x = (1.0 - c)/(1.0 - cos(ang));          // 0 on the axis, 1 at the nominal edge
  float a = exp(-x*x*2.2)*smoothstep(1.35, 0.85, x);
  return a/(1.0 + 0.012*d*d);
}
void main(){
  vec3 ro, rd; camRay(gl_FragCoord.xy, ro, rd);
  vec3 sp = uSpot.xyz; vec3 sdir = normalize(uSpot2.xyz - sp); float ang = uSpot2.w;
  vec3 lightC = vec3(1.0, 0.93, 0.84)*uSpot.w;
  vec3 col = vec3(0.0); float depth = 300.0;
  float tFloor = rd.y < 0.0 ? -ro.y/rd.y : 1e5;
  // floor
  if (tFloor < 1e4) {
    vec3 p = ro + rd*tFloor; depth = tFloor;
    vec3 n = vec3(0.0,1.0,0.0);
    // subtle micro-roughness variation (polished concrete / epoxy)
    float rv = fbm2(p.xz*1.7, 4);
    n = normalize(n + vec3(rv-0.5, 0.0, noise2(p.xz*2.3+7.0)-0.5)*0.018);
    vec3 L = sp - p; float dl = length(L); L /= dl;
    float att = coneAtt(p, sp, sdir, ang);
    float dif = SAT(dot(n, L));
    vec3 base = vec3(0.0035);
    col = base*dif*att*lightC*18.0;
    // specular hotspot + reflection of the light cone/source
    col += lightC*ggx(n, -rd, L, 0.14)*att*9.0;
    vec3 rr = reflect(rd, n);
    // reflected beam glow (cheap): distance of reflected ray to spot axis
    vec3 w = p - sp; float tb = max(dot(-w, rr), 0.0);
    float glow = exp(-length(w + rr*tb)*1.6)*0.05;
    col += lightC*glow*fresnelS(dot(n,-rd), 0.05)*3.0;
    float fade = exp(-tFloor*0.06);
    col *= fade;
    col += vec3(0.006,0.0065,0.007)*uAmbient*fade;
  }
  // volumetric beam (single scattering) with dust
  float tEnd = min(depth, 40.0);
  float dt = tEnd/48.0;
  float t = dt*hash12(gl_FragCoord.xy);
  vec3 scat = vec3(0.0);
  for (int i = 0; i < 48; i++) {
    vec3 p = ro + rd*t;
    float a = coneAtt(p, sp, sdir, ang);
    if (a > 0.0) {
      float hz = 0.55 + 0.9*fbm3(p*0.9 + vec3(0.0, -uTime*0.08, uTime*0.05), 3);
      vec3 L = normalize(sp - p);
      float ph = 0.25 + 0.75*pow(SAT(dot(-rd, -L)*0.5+0.5), 3.0);
      // dust motes: sparse bright specks drifting slowly
      vec3 q = p*vec3(9.0, 9.0, 9.0) + vec3(0.0, uTime*0.35, 0.0);
      vec3 cell = floor(q); vec3 h = hash33(cell);
      vec3 fp = fract(q) - (0.25 + 0.5*h);
      float mote = step(0.86, h.x)*smoothstep(0.055, 0.0, length(fp))*2.2;
      scat += a*(hz*0.05 + mote*0.8)*ph*dt;
    }
    t += dt;
  }
  col += scat*lightC*2.2;
  // source glow
  vec3 w = ro - sp; float tb = max(-dot(w, rd), 0.0);
  float dsrc = length(w + rd*tb);
  col += lightC*exp(-dsrc*7.0)*0.6;
  outColor = vec4(col, depth);
}
