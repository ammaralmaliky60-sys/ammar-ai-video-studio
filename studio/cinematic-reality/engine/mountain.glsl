// ---- photoreal mountain landscape with valley fog ----
uniform vec4 uMt;   // x terrain scale, y fog height, z fog density, w snow line
uniform float uAmp; // vertical amplitude
uniform float uReveal; // 0 = black, 1 = full light (sunrise reveal from the black studio)

const mat2 M2 = mat2(0.8,-0.6,0.6,0.8);
const vec3 SUNC = vec3(1.0,0.82,0.62)*3.4;
const vec3 ZEN = vec3(0.03,0.10,0.32);
const vec3 HOR = vec3(0.55,0.60,0.68);

float terrain(vec2 x, int oct){
  vec2 p = x/uMt.x;
  float a = 0.0, b = 1.0; vec2 d = vec2(0.0);
  for (int i = 0; i < 16; i++) {
    if (i >= oct) break;
    vec3 n = noised(p);
    d += n.yz;
    a += b*n.x/(1.0 + dot(d,d));
    b *= 0.5; p = M2*p*2.0;
  }
  // big ridges + valley
  return uAmp*a;
}
float mapT(vec3 p, int oct){ return p.y - terrain(p.xz, oct); }

float traceT(vec3 ro, vec3 rd, float tmax){
  float t = 2.0;
  for (int i = 0; i < 320; i++) {
    vec3 p = ro + rd*t;
    float h = mapT(p, 8);
    if (abs(h) < 0.0015*t || t > tmax) break;
    t += max(0.42*h, 0.0012*t);
  }
  return t;
}
vec3 normalT(vec3 p, float t){
  vec2 e = vec2(0.0018*t + 0.05, 0.0);
  return normalize(vec3(terrain(p.xz - e.xy, 14) - terrain(p.xz + e.xy, 14), 2.0*e.x, terrain(p.xz - e.yx, 14) - terrain(p.xz + e.yx, 14)));
}
float shadowT(vec3 ro, vec3 rd){
  float res = 1.0, t = 4.0;
  for (int i = 0; i < 40; i++) {
    vec3 p = ro + rd*t;
    float h = mapT(p, 7);
    res = min(res, 14.0*h/t);
    t += clamp(h, 6.0, 120.0);
    if (res < 0.001 || p.y > uAmp*1.8) break;
  }
  return SAT(res);
}
vec3 sky(vec3 ro, vec3 rd){
  vec3 col = skyBase(rd, uSunDir, ZEN, HOR, 1.0);
  col += sunDisk(rd, uSunDir, 0.00014);
  if (rd.y > 0.0) {
    float d = (4200.0 - ro.y)/rd.y;
    vec2 p = (ro + rd*d).xz*0.00025 + vec2(uTime*0.004, 0.0);
    float b = fbm2(p, 7); float det = fbm2(p*3.3+5.0, 4);
    float den = SAT((b + 0.3*det - 0.66)*3.0); den = den*den*(3.0-2.0*den);
    float bs = fbm2(p + uSunDir.xz*0.05, 6);
    vec3 c = mix(vec3(0.32,0.34,0.42), vec3(1.25,1.05,0.88), SAT(0.6 + (b-bs)*3.5));
    col = mix(col, c, den*smoothstep(0.01, 0.15, rd.y));
  }
  return col;
}
// height fog integral (exponential) with noise-modulated "volumetric" bank
vec3 applyFog(vec3 col, vec3 ro, vec3 rd, float t){
  float a = uMt.z, b = 1.0/uMt.y*3.0;
  float kk = rd.y*b;
  float fogAmt = a*exp(-ro.y*b)*(abs(kk) < 1e-5 ? t : (1.0 - exp(-t*kk))/kk);
  fogAmt = SAT(1.0 - exp(-fogAmt));
  float mu = dot(rd, uSunDir);
  vec3 fc = mix(vec3(0.50,0.58,0.70), vec3(1.05,0.86,0.66), pow(SAT(mu*0.5+0.5), 6.0));
  // aerial perspective (bluish distance haze)
  float ap = 1.0 - exp(-t*0.00012);
  col = mix(col, HOR*0.95, ap);
  return mix(col, fc, fogAmt);
}
// low cloud bank sitting in the valleys: march a few samples through the layer
vec4 valleyCloud(vec3 ro, vec3 rd, float tmax){
  if (abs(rd.y) < 0.002) return vec4(0.0);
  float y0 = uMt.y*0.55, y1 = uMt.y*1.05;
  float t0 = (y1 - ro.y)/rd.y, t1 = (y0 - ro.y)/rd.y;
  if (rd.y > 0.0) { float tmp = t0; t0 = t1; t1 = tmp; }
  t0 = max(t0, 0.0); t1 = min(t1, tmax);
  if (t1 <= t0) return vec4(0.0);
  vec4 acc = vec4(0.0);
  float dt = (t1 - t0)/12.0;
  float t = t0 + dt*hash12(gl_FragCoord.xy);
  for (int i = 0; i < 12; i++) {
    vec3 p = ro + rd*t;
    float hn = (p.y - y0)/(y1 - y0);
    float n = fbm3(p*0.0024 + vec3(uTime*0.012, 0.0, uTime*0.006), 5);
    float den = SAT((n - 0.42 - hn*0.35)*3.2)*smoothstep(0.0, 0.25, hn)*smoothstep(1.0, 0.6, hn);
    if (den > 0.01) {
      float lit = SAT(0.55 + hn*0.6);
      vec3 c = mix(vec3(0.42,0.47,0.56), vec3(1.15,1.0,0.88), lit);
      float al = den*0.35;
      acc.rgb += (1.0-acc.a)*c*al; acc.a += (1.0-acc.a)*al;
    }
    t += dt;
    if (acc.a > 0.97) break;
  }
  return acc;
}

void main(){
  vec3 ro, rd; camRay(gl_FragCoord.xy, ro, rd);
  float tmax = 16000.0;
  float t = traceT(ro, rd, tmax);
  vec3 col; float depth = tmax;
  if (t < tmax) {
    vec3 p = ro + rd*t;
    vec3 n = normalT(p, t);
    // materials: rock, grass, snow
    float slope = n.y;
    vec3 rock = mix(vec3(0.10,0.085,0.07), vec3(0.20,0.17,0.135), noise2(p.xz*0.05));
    rock *= 0.7 + 0.6*noise2(p.xz*0.6);
    vec3 grass = mix(vec3(0.035,0.075,0.02), vec3(0.10,0.12,0.035), noise2(p.xz*0.02));
    vec3 alb = mix(rock, grass, smoothstep(0.62, 0.85, slope)*smoothstep(uMt.w*0.8, uMt.w*0.3, p.y));
    float snowAmt = smoothstep(uMt.w - 60.0, uMt.w + 60.0, p.y + 140.0*fbm2(p.xz*0.004, 4))*smoothstep(0.55, 0.8, slope);
    alb = mix(alb, vec3(0.86,0.88,0.92), snowAmt);
    float sh = shadowT(p + n*2.0, uSunDir);
    float dif = SAT(dot(n, uSunDir));
    float amb = SAT(0.5 + 0.5*n.y);
    float bac = SAT(0.2 + 0.8*dot(normalize(vec3(-uSunDir.x, 0.0, -uSunDir.z)), n));
    vec3 lin = dif*sh*SUNC + amb*vec3(0.30,0.40,0.62)*0.9 + bac*vec3(0.30,0.24,0.18)*0.35;
    col = alb*lin;
    col += snowAmt*SUNC*ggx(n, -rd, uSunDir, 0.35)*sh*0.25;
    col = applyFog(col, ro, rd, t);
    depth = t;
  } else {
    col = sky(ro, rd);
  }
  vec4 vc = valleyCloud(ro, rd, min(t, tmax));
  col = col*(1.0 - vc.a) + vc.rgb;
  col *= uReveal;
  outColor = vec4(col, depth);
}
