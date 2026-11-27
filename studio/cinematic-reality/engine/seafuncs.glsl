// ---- photoreal open sea ----
uniform vec4 uSea;   // x height, y choppy, z freq, w speed
uniform vec4 uSky;   // x cloud cover, y turbidity, z unused, w haze density

const mat2 OCT = mat2(1.6,1.2,-1.2,1.6);
const vec3 ZEN = vec3(0.022,0.085,0.30);
const vec3 HOR = vec3(0.46,0.52,0.60);
float seaOct(vec2 uv, float ch){
  uv += noise2(uv);
  vec2 wv = 1.0-abs(sin(uv)); vec2 swv = abs(cos(uv));
  wv = mix(wv, swv, wv);
  return pow(1.0-pow(wv.x*wv.y, 0.65), ch);
}
float seaH(vec2 xz, int it){
  float freq = uSea.z, amp = uSea.x, ch = uSea.y, h = 0.0;
  float T = uTime*uSea.w;
  vec2 uv = xz; uv.x *= 0.75;
  for (int i = 0; i < 6; i++) {
    if (i >= it) break;
    float d = seaOct((uv+T)*freq, ch) + seaOct((uv-T)*freq, ch);
    h += d*amp;
    uv = OCT*uv; freq *= 1.9; amp *= 0.22; ch = mix(ch, 1.0, 0.2);
  }
  return h;
}
float seaMap(vec3 p, int it){ return p.y - seaH(p.xz, it); }
vec3 seaNormal(vec3 p, float eps){
  vec3 n; n.y = seaMap(p, 6);
  n.x = seaMap(vec3(p.x+eps,p.y,p.z), 6) - n.y;
  n.z = seaMap(vec3(p.x,p.y,p.z+eps), 6) - n.y;
  n.y = eps; return normalize(n);
}
float seaTrace(vec3 ori, vec3 dir, out vec3 p){
  float tm = 0.0; float tx = 3000.0;
  float hx = seaMap(ori + dir*tx, 3);
  if (hx > 0.0) { p = ori + dir*tx; return tx; }
  float hm = seaMap(ori + dir*tm, 3); float tmid = 0.0;
  for (int i = 0; i < 10; i++) {
    tmid = mix(tm, tx, hm/(hm-hx));
    p = ori + dir*tmid;
    float hmid = seaMap(p, 3);
    if (hmid < 0.0) { tx = tmid; hx = hmid; } else { tm = tmid; hm = hmid; }
  }
  return tmid;
}

const vec3 SUNC = vec3(1.0,0.80,0.58)*3.0;
vec4 cloudLayer(vec3 ro, vec3 rd){
  if (rd.y < 0.004) return vec4(0.0);
  float d = (1400.0 - ro.y)/rd.y;
  vec2 p = (ro + rd*d).xz*0.00042 + vec2(uTime*0.0035, uTime*0.001);
  float b = fbm2(p, 7);
  float det = fbm2(p*3.7 + 3.0, 5);
  float den = SAT((b + 0.32*det - (1.08 - uSky.x))*3.2);
  den = den*den*(3.0-2.0*den);
  float bs = fbm2(p + uSunDir.xz*0.045, 6);
  float lit = SAT(0.62 + (b - bs)*3.5);
  float mu = dot(rd, uSunDir);
  vec3 dark = vec3(0.30,0.33,0.40); vec3 lite = vec3(1.25,1.08,0.92);
  vec3 c = mix(dark, lite, lit);
  c += SUNC*0.55*pow(SAT(mu),10.0)*(1.0-den)*1.4;      // silver lining
  float fade = smoothstep(0.004, 0.10, rd.y);
  c = mix(HOR*1.05, c, smoothstep(0.004, 0.06, rd.y));
  return vec4(c, den*fade);
}
vec3 skyFull(vec3 ro, vec3 rd){
  vec3 col = skyBase(rd, uSunDir, ZEN, HOR, uSky.y);
  col += sunDisk(rd, uSunDir, 0.00012);
  vec4 cl = cloudLayer(ro, rd);
  col = mix(col, cl.rgb, cl.a);
  return col;
}
vec3 skyRefl(vec3 rd){
  vec3 r = rd; r.y = abs(r.y);
  return skyBase(r, uSunDir, ZEN, HOR, uSky.y);
}

vec3 shadeSea(vec3 p, vec3 n, vec3 rd, float t){
  vec3 l = uSunDir;
  float fres = min(fresnelS(dot(n, -rd), 0.02), 0.6);
  vec3 refl = skyRefl(reflect(rd, n));
  vec3 deep = vec3(0.003, 0.028, 0.055);
  vec3 water = vec3(0.04, 0.17, 0.17);
  float dif = pow(SAT(dot(n,l))*0.4+0.6, 80.0);
  vec3 refr = deep + dif*water*0.10;
  float hgt = SAT((p.y - uSea.x*0.8)/(uSea.x*1.6));
  float sss = pow(SAT(dot(-rd, l)*0.5+0.5), 4.0)*hgt*(1.0 - SAT(n.y*1.1-0.1));
  refr += water*sss*1.3;
  vec3 col = mix(refr, refl, fres);
  float atten = max(1.0 - t*t*0.0006, 0.0);
  col += water*(p.y - uSea.x)*0.14*atten;
  float fn = fbm2(p.xz*1.3 + uTime*0.25, 4);
  float foam = smoothstep(uSea.x*1.75, uSea.x*2.35, p.y + (fn-0.5)*0.5)*atten;
  col = mix(col, vec3(0.80,0.84,0.88)*(0.5+0.5*SAT(dot(n,l))), foam*0.55);
  col += SUNC*ggx(n, -rd, l, 0.10)*0.7;
  return col;
}

