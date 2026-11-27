// ---- chrome 3D wall clock, transparent background. Hour hand driven by uHour, accent arc from uArc0 ----
uniform float uHour;      // continuous hour value (0..12)
uniform float uArc0;      // arc start hour (accent sweep from uArc0 to uHour), <0 disables
uniform float uScale;     // pop-in scale (0..1)
uniform float uSheen;
uniform vec3 uAccent;     // accent colour (linear)

#define R0 1.0
vec3 envRoom(vec3 r){
  float up = r.y*0.5+0.5;
  vec3 c = mix(vec3(0.02,0.012,0.016), vec3(0.17,0.15,0.15), smoothstep(0.30, 0.60, up));
  c = mix(c, vec3(0.32,0.32,0.36), smoothstep(0.80, 1.0, up));
  c += vec3(3.2,3.0,2.7)*smoothstep(0.012, 0.0, abs(r.y - 0.42))*0.9;
  c += vec3(2.6,2.4,2.2)*smoothstep(0.93, 0.975, dot(r, normalize(vec3(-0.55, 0.45, 0.70))));
  c += vec3(1.9,1.2,1.6)*smoothstep(0.95, 0.985, dot(r, normalize(vec3(0.7, 0.2, 0.68))));
  c += vec3(3.0,2.8,2.5)*smoothstep(0.03, 0.0, abs(r.x*0.7 + r.y*0.3 - mix(-1.2, 1.2, uSheen)));
  return c;
}
float sdBox(vec3 p, vec3 b){ vec3 q = abs(p) - b; return length(max(q,0.0)) + min(max(q.x,max(q.y,q.z)),0.0); }
float sdRBox(vec3 p, vec3 b, float r){ return sdBox(p, b - r) - r; }
mat2 rot(float a){ float c = cos(a), s = sin(a); return mat2(c, -s, s, c); }

// material id: 1 bezel, 2 face, 3 ticks, 4 hour hand, 5 minute hand, 6 cap
vec2 map(vec3 p){
  p /= max(uScale, 1e-3);
  vec2 res = vec2(1e9, 0.0);
  // bezel torus around z axis
  float bez = length(vec2(length(p.xy) - R0, p.z)) - 0.09;
  res = vec2(bez, 1.0);
  // face disc
  float face = max(length(p.xy) - R0 + 0.02, abs(p.z + 0.03) - 0.03);
  if (face < res.x) res = vec2(face, 2.0);
  // 12 ticks (angular repetition)
  float a = atan(p.x, p.y); float sec = 6.2831853/12.0;
  float k = floor(a/sec + 0.5); float aa = k*sec;
  vec2 q = rot(-aa)*p.xy;   // rotate so the tick sits on +y
  bool major = mod(k + 12.0, 3.0) < 0.5;
  float tick = sdRBox(vec3(q.x, q.y - 0.80, p.z - 0.02), major ? vec3(0.035, 0.11, 0.025) : vec3(0.018, 0.06, 0.018), 0.012);
  if (tick < res.x) res = vec2(tick, 3.0);
  // hour hand
  float ha = uHour/12.0*6.2831853;
  vec2 hq = rot(-ha)*p.xy;
  float hh = sdRBox(vec3(hq.x, hq.y - 0.24, p.z - 0.07), vec3(0.04, 0.32, 0.02), 0.015);
  if (hh < res.x) res = vec2(hh, 4.0);
  // minute hand (time-lapse: one turn per hour)
  float ma = uHour*6.2831853;
  vec2 mq = rot(-ma)*p.xy;
  float mh = sdRBox(vec3(mq.x, mq.y - 0.34, p.z - 0.10), vec3(0.022, 0.46, 0.014), 0.01);
  if (mh < res.x) res = vec2(mh, 5.0);
  float cap = max(length(p.xy) - 0.07, abs(p.z - 0.11) - 0.03);
  if (cap < res.x) res = vec2(cap, 6.0);
  res.x *= max(uScale, 1e-3);
  return res;
}
vec3 nrm(vec3 p){ vec2 e = vec2(0.0015, 0.0);
  return normalize(vec3(map(p+e.xyy).x-map(p-e.xyy).x, map(p+e.yxy).x-map(p-e.yxy).x, map(p+e.yyx).x-map(p-e.yyx).x)); }

void main(){
  vec3 ro, rd; camRay(gl_FragCoord.xy, ro, rd);
  vec4 o = vec4(0.0);
  if (uScale > 0.002) {
    float t = 0.0; vec2 h = vec2(0.0); bool hit = false; float best = 1e9; float tb = 0.0;
    float pa = 2.0*tan(radians(uFov)*0.5)/uRes.y;
    for (int i = 0; i < 120; i++) {
      h = map(ro + rd*t);
      if (h.x < 0.0004*t) { hit = true; break; }
      float r = h.x/(t*pa); if (r < best) { best = r; tb = t; }
      t += h.x*0.9; if (t > 40.0) break;
    }
    float cov = hit ? 1.0 : 1.0 - smoothstep(0.0, 1.0, best);
    if (!hit && cov > 0.02) { t = tb; h = map(ro + rd*t); }
    if (cov > 0.02) {
      vec3 p = ro + rd*t; vec3 n = nrm(p); vec3 v = -rd;
      vec3 L = normalize(vec3(-0.4, 0.6, 0.7));
      vec3 env = envRoom(reflect(rd, n));
      float fr = pow(1.0 - SAT(dot(n, v)), 5.0);
      vec3 c;
      float id = h.y;
      if (id < 1.5 || id > 5.5 || abs(id - 3.0) < 0.5) {            // chrome parts
        vec3 base = id > 2.5 && id < 3.5 ? vec3(0.95) : vec3(0.92, 0.92, 0.95);
        c = base*env*(0.55 + 0.45*fr) + vec3(1.6)*ggx(n, v, L, 0.1)*0.8;
      } else if (id < 2.5) {                                        // dark glossy face + accent arc
        vec3 pp = p/max(uScale, 1e-3);
        float ang = mod(atan(pp.x, pp.y), 6.2831853)/6.2831853*12.0;
        float rr = length(pp.xy);
        float arc = uArc0 >= 0.0 ? step(uArc0, ang)*step(ang, uHour)*smoothstep(0.50, 0.53, rr)*smoothstep(0.70, 0.67, rr) : 0.0;
        c = vec3(0.03, 0.012, 0.025)*(0.4 + SAT(dot(n, L))) + env*0.06*(0.3 + fr) + vec3(1.2)*ggx(n, v, L, 0.2)*0.25;
        c += uAccent*arc*2.2;
      } else {                                                      // hands: accent metal
        vec3 base = uAccent;
        c = base*(0.2 + 1.2*SAT(dot(n, L))) + base*env*0.5 + vec3(1.4)*ggx(n, v, L, 0.15)*0.7;
      }
      o = vec4(c*cov, cov);
    }
  }
  outColor = o;
}
