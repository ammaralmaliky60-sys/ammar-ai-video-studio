// ---- indoor standing flag (Iran) waving gently in the room, transparent background ----
uniform sampler2D uFlag;
uniform vec4 uFl;     // xyz top-left (hoist) corner, w width (m)
uniform vec4 uFl2;    // x height, y wave amplitude, z wave speed, w reveal (0..1 unfurl from the pole)

float clothZ(vec2 uv, float t){
  float u = uv.x, v = uv.y;
  float A = pow(u, 1.1)*uFl2.y;
  float w = 0.0;
  w += 0.36*sin(5.6*u - t*uFl2.z + 0.8*v + 1.1*sin(t*0.6));
  w += 0.16*sin(10.5*u - t*uFl2.z*1.5 - 1.5*v + 0.5);
  w += 0.07*sin(17.0*u - t*uFl2.z*2.1 + 2.4*v + 2.0);
  // unfurling: the not-yet-open part bunches towards the pole
  w += (1.0 - uFl2.w)*0.4*sin(30.0*u - t*4.0);
  return A*w;
}
float clothSag(vec2 uv){ return uv.x*uv.x*0.05; }
float traceFlag(vec3 ro, vec3 rd, out vec2 uv){
  float Wd = uFl.w, Hd = uFl2.x;
  float amp = uFl2.y*0.75 + 0.05;
  float t0 = (uFl.z + amp - ro.z)/rd.z, t1 = (uFl.z - amp - ro.z)/rd.z;
  if (t0 > t1) { float tmp = t0; t0 = t1; t1 = tmp; }
  t0 = max(t0, 0.0);
  float dt = (t1 - t0)/40.0; float prev = 1.0; float tp = t0;
  for (int i = 0; i <= 40; i++) {
    float t = t0 + dt*float(i);
    vec3 p = ro + rd*t;
    vec2 q = vec2((p.x - uFl.x)/Wd, (uFl.y - p.y)/Hd); q.y -= clothSag(q);
    float f = (p.z - uFl.z) - clothZ(q, uTime);
    if (i > 0 && f*prev < 0.0) {
      float ta = tp, tb = t, fa = prev;
      for (int k = 0; k < 6; k++) {
        float tm = 0.5*(ta+tb); vec3 pm = ro + rd*tm;
        vec2 qm = vec2((pm.x - uFl.x)/Wd, (uFl.y - pm.y)/Hd); qm.y -= clothSag(qm);
        float fm = (pm.z - uFl.z) - clothZ(qm, uTime);
        if (fm*fa < 0.0) tb = tm; else { ta = tm; fa = fm; }
      }
      float th = 0.5*(ta+tb); vec3 ph = ro + rd*th;
      uv = vec2((ph.x - uFl.x)/Wd, (uFl.y - ph.y)/Hd); uv.y -= clothSag(uv);
      if (uv.x >= 0.0 && uv.x <= uFl2.w && uv.y >= 0.0 && uv.y <= 1.0) return th;
    }
    prev = f; tp = t;
  }
  return -1.0;
}
vec3 flagNormal(vec2 uv){
  float e = 0.004;
  float dzdu = (clothZ(uv + vec2(e,0.0), uTime) - clothZ(uv - vec2(e,0.0), uTime))/(2.0*e*uFl.w);
  float dzdv = (clothZ(uv + vec2(0.0,e), uTime) - clothZ(uv - vec2(0.0,e), uTime))/(2.0*e*uFl2.x);
  vec2 wv = uv*vec2(uFl.w, uFl2.x)*900.0;
  return normalize(vec3(-dzdu + sin(wv.x)*0.01, dzdv + sin(wv.y)*0.01, 1.0));
}
vec3 envRoomF(vec3 r){
  float up = r.y*0.5+0.5;
  vec3 c = mix(vec3(0.05,0.04,0.035), vec3(0.95,0.90,0.82), smoothstep(0.3, 0.7, up));
  c += vec3(2.5,2.3,2.0)*smoothstep(0.93, 0.975, dot(r, normalize(vec3(-0.45, 0.55, 0.70))));
  return c;
}
void main(){
  vec3 ro, rd; camRay(gl_FragCoord.xy, ro, rd);
  vec4 o = vec4(0.0); float depth = 1e5;
  vec3 KEY = vec3(1.0, 0.95, 0.88)*1.25;
  vec3 L = normalize(vec3(-0.40, 0.50, 0.75));
  // pole (thin brushed metal), from the floor up to just above the flag
  float pr = 0.022;
  vec3 pc = vec3(uFl.x - 0.028, 0.0, uFl.z);
  {
    vec2 oc = ro.xz - pc.xz; vec2 d2 = rd.xz;
    float a = dot(d2,d2), b = dot(oc,d2), c = dot(oc,oc) - pr*pr;
    float h = b*b - a*c;
    if (h > 0.0) {
      float t = (-b - sqrt(h))/a; vec3 p = ro + rd*t;
      if (t > 0.0 && p.y < uFl.y + 0.10) {
        vec3 n = normalize(vec3(p.x - pc.x, 0.0, p.z - pc.z));
        vec3 env = envRoomF(reflect(rd, n));
        vec3 c0 = vec3(0.72,0.62,0.40);
        vec3 col = c0*SAT(dot(n,L))*KEY*0.5 + env*c0*0.7 + KEY*ggx(n,-rd,L,0.22)*0.8;
        o = vec4(col, 1.0); depth = t;
      }
    }
    // finial
    vec3 fc = vec3(pc.x, uFl.y + 0.15, pc.z); vec3 w = ro - fc;
    float bb = dot(w, rd), cc = dot(w,w) - 0.045*0.045, hh = bb*bb - cc;
    if (hh > 0.0) { float t = -bb - sqrt(hh); if (t > 0.0 && t < depth) { vec3 p = ro + rd*t; vec3 n = normalize(p - fc);
      vec3 env = envRoomF(reflect(rd,n));
      o = vec4(vec3(0.95,0.75,0.35)*(SAT(dot(n,L))*KEY*0.45 + env*0.8) + KEY*ggx(n,-rd,L,0.15), 1.0); depth = t; } }
  }
  vec2 uv;
  float tf = traceFlag(ro, rd, uv);
  if (tf > 0.0 && tf < depth) {
    vec3 n = flagNormal(uv);
    if (dot(n, rd) > 0.0) n = -n;
    vec3 alb = pow(texture(uFlag, vec2(uv.x, 1.0 - uv.y)).rgb, vec3(2.2));
    float z = clothZ(uv, uTime);
    float occ = clamp(0.80 + 0.9*z/(uFl2.y + 0.01), 0.55, 1.0);
    float dif = SAT(dot(n, L));
    float sheen = pow(1.0 - SAT(dot(n,-rd)), 3.0)*0.25;
    vec3 amb = vec3(0.42,0.40,0.38);
    vec3 col = alb*(dif*KEY*0.75 + amb)*occ + sheen*KEY*0.15*alb;
    // soft edge at the unfurl front
    float edge = smoothstep(uFl2.w, uFl2.w - 0.02, uv.x);
    o = vec4(col*edge, edge);
  }
  outColor = o;
}
