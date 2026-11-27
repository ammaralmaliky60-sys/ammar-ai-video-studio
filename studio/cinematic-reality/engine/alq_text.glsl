// ---- extruded 3D word + optional 3D map pin, transparent background (overlaid on the real room) ----
uniform float uSheen;     // light bar sweep across the letters
uniform vec4 uPin;        // xyz position (world), w = scale (0 = hidden)
uniform vec4 uPinCol;     // rgb colour (linear), a = drop shadow strength on letters (unused)

vec3 envRoom(vec3 r){
  float up = r.y*0.5+0.5;
  vec3 c = mix(vec3(0.02,0.012,0.016), vec3(0.17,0.15,0.15), smoothstep(0.30, 0.60, up));
  c = mix(c, vec3(0.32,0.32,0.36), smoothstep(0.80, 1.0, up));
  c += vec3(3.2,3.0,2.7)*smoothstep(0.012, 0.0, abs(r.y - 0.42))*0.9;
  c += vec3(2.6,2.4,2.2)*smoothstep(0.93, 0.975, dot(r, normalize(vec3(-0.55, 0.45, 0.70))));
  c += vec3(1.9,1.2,1.6)*smoothstep(0.95, 0.985, dot(r, normalize(vec3(0.7, 0.2, 0.68))));   // magenta-tinted key
  c += vec3(3.0,2.8,2.5)*smoothstep(0.03, 0.0, abs(r.x*0.7 + r.y*0.3 - mix(-1.2, 1.2, uSheen)));
  return c;
}

// map pin: sphere head + cone tip, white inner disc
float sdCappedCone(vec3 p, float h, float r1, float r2){
  vec2 q = vec2(length(p.xz), p.y); vec2 k1 = vec2(r2, h); vec2 k2 = vec2(r2 - r1, 2.0*h);
  vec2 ca = vec2(q.x - min(q.x, (q.y < 0.0) ? r1 : r2), abs(q.y) - h);
  vec2 cb = q - k1 + k2*clamp(dot(k1 - q, k2)/dot(k2, k2), 0.0, 1.0);
  float s = (cb.x < 0.0 && ca.y < 0.0) ? -1.0 : 1.0; return s*sqrt(min(dot(ca,ca), dot(cb,cb))); }
float smin(float a, float b, float k){ float h = clamp(0.5 + 0.5*(b - a)/k, 0.0, 1.0); return mix(b, a, h) - k*h*(1.0 - h); }
float pinSDF(vec3 p, out float inner){
  vec3 q = (p - uPin.xyz)/max(uPin.w, 1e-4);
  float head = length(q - vec3(0.0, 0.62, 0.0)) - 0.40;
  float cone = sdCappedCone(q - vec3(0.0, 0.28, 0.0), 0.28, 0.015, 0.30);
  float d = smin(head, cone, 0.08);
  d = max(d, -(length(q - vec3(0.0, 0.62, 0.40)) - 0.17));   // inset dimple on the front
  inner = smoothstep(0.03, 0.0, length(q.xy - vec2(0.0, 0.62)) - 0.17)*step(0.15, q.z);
  return d*uPin.w;
}
float pinTrace(vec3 ro, vec3 rd, out float inner){
  inner = 0.0;
  if (uPin.w <= 0.0) return -1.0;
  float t = 0.0;
  for (int i = 0; i < 90; i++) {
    float d = pinSDF(ro + rd*t, inner);
    if (d < 0.0005*t) return t;
    t += d*0.9; if (t > 60.0) break;
  }
  return -1.0;
}
vec3 pinNormal(vec3 p){ float k; vec2 e = vec2(0.002*uPin.w, 0.0);
  return normalize(vec3(pinSDF(p+e.xyy,k)-pinSDF(p-e.xyy,k), pinSDF(p+e.yxy,k)-pinSDF(p-e.yxy,k), pinSDF(p+e.yyx,k)-pinSDF(p-e.yyx,k))); }

void main(){
  vec3 ro, rd; camRay(gl_FragCoord.xy, ro, rd);
  vec4 o = vec4(0.0);
  vec3 L = normalize(vec3(-0.4, 0.6, 0.7));
  float tt = txtTrace(ro, rd, 1e4);
  float cov = 1.0;
  if (tt < 0.0 && gTxtCov > 0.02) { tt = gTxtT; cov = gTxtCov; }
  float inner; float tp = pinTrace(ro, rd, inner);
  if (tp > 0.0 && (tt < 0.0 || tp < tt)) {
    vec3 q = ro + rd*tp; vec3 n = pinNormal(q);
    vec3 env = envRoom(reflect(rd, n));
    vec3 base = mix(uPinCol.rgb, vec3(0.95), inner);
    float fr = pow(1.0 - SAT(dot(n, -rd)), 5.0);
    vec3 c = base*(0.25 + 1.3*SAT(dot(n, L))) + env*(0.06 + 0.5*fr) + vec3(1.6)*ggx(n, -rd, L, 0.18)*0.6;
    o = vec4(c, 1.0);
  } else if (tt > 0.0) {
    vec3 q = ro + rd*tt; vec3 n = txtNormal(q);
    vec3 env = envRoom(reflect(rd, n));
    vec3 c = txtShade(q, n, rd, env, vec3(1.6,1.5,1.4), L, vec3(0.25,0.23,0.21));
    o = vec4(c*cov, cov);
  }
  outColor = o;
}
