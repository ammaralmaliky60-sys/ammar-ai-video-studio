// ---- Iraqi flag: wind-driven cloth on a pole against a golden-hour sky ----
uniform sampler2D uFlag;
uniform vec4 uFl;     // xyz top-left (hoist) corner, w width (m)
uniform vec4 uFl2;    // x height, y wind strength, z wave speed, w unused
vec3 skyF(vec3 ro, vec3 rd){ return skyFull(ro, rd); }
// cloth displacement along z (towards camera), u: 0 at hoist -> 1 at fly end, v: 0 top -> 1 bottom
float clothZ(vec2 uv, float t){
  float u = uv.x, v = uv.y;
  float A = pow(u, 1.15)*uFl2.y;
  float w = 0.0;
  w += 0.34*sin(6.2*u - t*uFl2.z*1.0 + 0.9*v + 1.3*sin(t*0.7));
  w += 0.17*sin(11.5*u - t*uFl2.z*1.55 - 1.7*v + 0.5);
  w += 0.08*sin(19.0*u - t*uFl2.z*2.2 + 2.6*v + 2.0);
  w += 0.05*sin(8.0*v + 5.0*u - t*1.7);
  return A*w;
}
float clothSag(vec2 uv, float t){ return uv.x*uv.x*0.18*(0.6+0.4*sin(t*0.9 + uv.x*3.0)); }
// returns hit t, writes uv
float traceFlag(vec3 ro, vec3 rd, out vec2 uv){
  float Wd = uFl.w, Hd = uFl2.x;
  // flag occupies x in [x0, x0+W], y in [y0-H, y0], around plane z = z0
  float tz = (uFl.z - ro.z)/rd.z;
  float amp = uFl2.y*0.7 + 0.05;
  float t0 = (uFl.z + amp - ro.z)/rd.z, t1 = (uFl.z - amp - ro.z)/rd.z;
  if (t0 > t1) { float tmp = t0; t0 = t1; t1 = tmp; }
  t0 = max(t0, 0.0);
  float dt = (t1 - t0)/40.0;
  float prev = 1.0; float tp = t0;
  for (int i = 0; i <= 40; i++) {
    float t = t0 + dt*float(i);
    vec3 p = ro + rd*t;
    vec2 q = vec2((p.x - uFl.x)/Wd, (uFl.y - p.y)/Hd);
    q.y -= clothSag(q, uTime)/Hd;
    float f = (p.z - uFl.z) - clothZ(q, uTime);
    if (i > 0 && f*prev < 0.0) {
      // refine
      float ta = tp, tb = t, fa = prev;
      for (int k = 0; k < 6; k++) {
        float tm = 0.5*(ta+tb); vec3 pm = ro + rd*tm;
        vec2 qm = vec2((pm.x - uFl.x)/Wd, (uFl.y - pm.y)/Hd); qm.y -= clothSag(qm, uTime)/Hd;
        float fm = (pm.z - uFl.z) - clothZ(qm, uTime);
        if (fm*fa < 0.0) tb = tm; else { ta = tm; fa = fm; }
      }
      float th = 0.5*(ta+tb); vec3 ph = ro + rd*th;
      uv = vec2((ph.x - uFl.x)/Wd, (uFl.y - ph.y)/Hd); uv.y -= clothSag(uv, uTime)/Hd;
      if (uv.x >= 0.0 && uv.x <= 1.0 && uv.y >= 0.0 && uv.y <= 1.0) return th;
    }
    prev = f; tp = t;
  }
  return -1.0;
}
vec3 flagNormal(vec2 uv){
  float e = 0.004;
  float dzdu = (clothZ(uv + vec2(e,0.0), uTime) - clothZ(uv - vec2(e,0.0), uTime))/(2.0*e*uFl.w);
  float dzdv = (clothZ(uv + vec2(0.0,e), uTime) - clothZ(uv - vec2(0.0,e), uTime))/(2.0*e*uFl2.x);
  // fine weave
  vec2 wv = uv*vec2(uFl.w, uFl2.x)*420.0;
  float wx = sin(wv.x)*0.012, wy = sin(wv.y)*0.012;
  return normalize(vec3(-dzdu + wx, dzdv + wy, 1.0));
}

float sdCyl(vec3 p, float r){ return length(p.xz) - r; }

void main(){
  vec3 ro, rd; camRay(gl_FragCoord.xy, ro, rd);
  vec3 col = skyF(ro, rd); float depth = 5000.0;
  // pole: vertical cylinder at hoist edge
  vec3 pc = vec3(uFl.x - 0.06, 0.0, uFl.z);
  {
    vec2 oc = ro.xz - pc.xz; vec2 d2 = rd.xz;
    float a = dot(d2,d2), b = dot(oc,d2), c = dot(oc,oc) - 0.07*0.07;
    float h = b*b - a*c;
    if (h > 0.0) {
      float t = (-b - sqrt(h))/a; vec3 p = ro + rd*t;
      if (t > 0.0 && p.y < uFl.y + 0.35) {
        vec3 n = normalize(vec3(p.x - pc.x, 0.0, p.z - pc.z));
        vec3 r = reflect(rd, n);
        vec3 env = skyF(p, vec3(r.x, abs(r.y), r.z));
        vec3 c0 = vec3(0.55,0.56,0.58);
        col = c0*SAT(dot(n,uSunDir))*SUNC*0.35 + env*0.55 + SUNC*ggx(n,-rd,uSunDir,0.25)*0.5;
        depth = t;
      }
    }
    // finial sphere
    vec3 fc = vec3(pc.x, uFl.y + 0.45, pc.z); vec3 w = ro - fc;
    float bb = dot(w, rd), cc = dot(w,w) - 0.13*0.13, hh = bb*bb - cc;
    if (hh > 0.0) { float t = -bb - sqrt(hh); if (t > 0.0 && t < depth) { vec3 p = ro + rd*t; vec3 n = normalize(p - fc);
      vec3 env = skyF(p, reflect(rd,n)*vec3(1.0,sign(reflect(rd,n).y)+0.001,1.0));
      col = vec3(0.9,0.7,0.3)*(SAT(dot(n,uSunDir))*SUNC*0.3) + env*vec3(0.95,0.75,0.4)*0.8 + SUNC*ggx(n,-rd,uSunDir,0.15); depth = t; } }
  }
  vec2 uv;
  float tf = traceFlag(ro, rd, uv);
  if (tf > 0.0 && tf < depth) {
    vec3 n = flagNormal(uv);
    if (dot(n, rd) > 0.0) n = -n;
    vec3 alb = pow(texture(uFlag, vec2(uv.x, 1.0 - uv.y)).rgb, vec3(2.2));
    float z = clothZ(uv, uTime);
    float occ = SAT(0.72 + 1.6*z/(uFl2.y+0.01));            // troughs darker
    float ndl = dot(n, uSunDir);
    float dif = SAT(ndl);
    float trans = SAT(-ndl)*0.9 + 0.25;                              // light through the fabric
    float sheen = pow(1.0 - SAT(dot(n,-rd)), 3.0)*0.35;
    vec3 amb = mix(vec3(0.30,0.34,0.44), vec3(0.60,0.62,0.68), n.y*0.5+0.5)*0.75;
    col = alb*(dif*SUNC*0.55 + trans*SUNC*0.5 + amb)*occ + sheen*vec3(1.0,0.85,0.7)*SUNC*0.12*alb;
    depth = tf;
  }
  float tt = txtTrace(ro, rd, depth);
  float tcov = 1.0;
  if (tt < 0.0 && gTxtCov > 0.02) { tt = gTxtT; tcov = gTxtCov; }
  if (tt > 0.0) {
    vec3 colBg = col; float depthBg = depth;
    vec3 q = ro + rd*tt; vec3 n = txtNormal(q);
    vec3 r = reflect(rd, n);
    vec3 env = skyF(q, vec3(r.x, abs(r.y)*0.6+0.02, r.z));
    vec3 amb = mix(vec3(0.05,0.05,0.06), vec3(0.30,0.30,0.38), n.y*0.5+0.5);
    col = mix(colBg, txtShade(q, n, rd, env, SUNC*0.5, uSunDir, amb), tcov); depth = tcov > 0.5 ? tt : depthBg;
  }
  outColor = vec4(col, depth);
}
