#version 300 es
precision highp float;
precision highp sampler2D;
uniform vec2 uRes;
uniform float uTime;
uniform vec3 uCamPos;
uniform vec3 uCamTgt;
uniform float uRoll;
uniform float uFov;      // vertical fov in degrees
uniform vec2 uShift;     // lens shift (ndc units) for framing
uniform sampler2D uNoise;
uniform vec3 uSunDir;
out vec4 outColor;

#define PI 3.14159265
#define SAT(x) clamp(x, 0.0, 1.0)

float hash11(float p){ p = fract(p*0.1031); p *= p+33.33; p *= p+p; return fract(p); }
float hash12(vec2 p){ vec3 p3 = fract(vec3(p.xyx)*0.1031); p3 += dot(p3, p3.yzx+33.33); return fract((p3.x+p3.y)*p3.z); }
vec3 hash33(vec3 p3){ p3 = fract(p3*vec3(.1031,.1030,.0973)); p3 += dot(p3, p3.yxz+33.33); return fract((p3.xxy+p3.yxx)*p3.zyx); }

// texture-based value noise (fast on CPU rasterisers)
float noise3(vec3 x){
  vec3 p = floor(x); vec3 f = fract(x); f = f*f*(3.0-2.0*f);
  vec2 uv = (p.xy + vec2(37.0,239.0)*p.z) + f.xy;
  vec2 rg = textureLod(uNoise, (uv+0.5)/256.0, 0.0).xy;
  return mix(rg.x, rg.y, f.z);
}
float noise2(vec2 x){
  vec2 p = floor(x); vec2 f = fract(x); f = f*f*(3.0-2.0*f);
  return textureLod(uNoise, (p+f+0.5)/256.0, 0.0).x;
}
// value noise with analytic derivatives (for terrain)
vec3 noised(vec2 x){
  vec2 p = floor(x); vec2 f = fract(x);
  vec2 u = f*f*(3.0-2.0*f); vec2 du = 6.0*f*(1.0-f);
  float a = textureLod(uNoise, (p+vec2(0.5,0.5))/256.0, 0.0).z;
  float b = textureLod(uNoise, (p+vec2(1.5,0.5))/256.0, 0.0).z;
  float c = textureLod(uNoise, (p+vec2(0.5,1.5))/256.0, 0.0).z;
  float d = textureLod(uNoise, (p+vec2(1.5,1.5))/256.0, 0.0).z;
  return vec3(a+(b-a)*u.x+(c-a)*u.y+(a-b-c+d)*u.x*u.y, du*(vec2(b-a,c-a)+(a-b-c+d)*u.yx));
}
float fbm3(vec3 p, int oct){ float a = 0.5, s = 0.0; for(int i=0;i<8;i++){ if(i>=oct) break; s += a*noise3(p); p = p*2.02 + vec3(1.7,9.2,3.1); a *= 0.5; } return s; }
float fbm2(vec2 p, int oct){ float a = 0.5, s = 0.0; mat2 m = mat2(1.6,1.2,-1.2,1.6); for(int i=0;i<9;i++){ if(i>=oct) break; s += a*noise2(p); p = m*p; a *= 0.5; } return s; }

// camera ray
void camRay(vec2 fragCoord, out vec3 ro, out vec3 rd){
  vec2 q = (2.0*fragCoord - uRes)/uRes.y + uShift;
  vec3 ww = normalize(uCamTgt - uCamPos);
  vec3 up = vec3(sin(uRoll), cos(uRoll), 0.0);
  vec3 uu = normalize(cross(ww, up)); vec3 vv = cross(uu, ww);
  float fl = 1.0/tan(radians(uFov)*0.5);
  ro = uCamPos; rd = normalize(q.x*uu + q.y*vv + fl*ww);
}

// physically-inspired sky (single scattering approximation)
vec3 skyBase(vec3 rd, vec3 sd, vec3 zen, vec3 hor, float turb){
  float y = max(rd.y, 0.0);
  float mu = dot(rd, sd);
  vec3 col = mix(hor, zen, pow(y, 0.42));
  // mie forward glow and horizon brightening toward sun
  float g = 0.76; float mie = (1.0-g*g)/pow(1.0+g*g-2.0*g*mu, 1.5)/(4.0*PI);
  col += vec3(1.0,0.72,0.45)*mie*0.32*turb;
  col += vec3(1.0,0.8,0.6)*pow(SAT(mu),6.0)*0.22*turb*(1.0-y);
  // below horizon: dark haze
  col = mix(col, hor*0.55, smoothstep(0.0, -0.08, rd.y));
  return col;
}
vec3 sunDisk(vec3 rd, vec3 sd, float size){
  float mu = dot(rd, sd);
  return vec3(1.0,0.92,0.78)*smoothstep(1.0-size, 1.0-size*0.5, mu)*40.0;
}
// cloud layer on a plane at altitude h
vec4 clouds(vec3 ro, vec3 rd, vec3 sd, float h, float cover, float t, vec3 lightCol){
  if (rd.y < 0.01) return vec4(0.0);
  float d = (h - ro.y)/rd.y;
  vec2 p = (ro + rd*d).xz*0.00055 + vec2(t*0.004, t*0.0015);
  float n = fbm2(p*1.0, 7);
  float n2 = fbm2(p*3.1 + 7.0, 5);
  float den = SAT((n*0.75 + n2*0.35 - (1.0-cover)) * 2.2);
  // light: sample toward sun
  float ns = fbm2(p + sd.xz*0.03, 5);
  float shade = SAT(0.55 + (n - ns)*2.6);
  vec3 c = mix(vec3(0.38,0.42,0.52), lightCol, shade);
  float fade = smoothstep(0.01, 0.12, rd.y);
  float mu = dot(rd, sd);
  c += lightCol*pow(SAT(mu),12.0)*0.8*(1.0-den);    // silver lining
  return vec4(c, den*fade);
}

vec3 aces(vec3 x){ const float a=2.51,b=0.03,c=2.43,d=0.59,e=0.14; return SAT((x*(a*x+b))/(x*(c*x+d)+e)); }

// GGX specular
float ggx(vec3 n, vec3 v, vec3 l, float r){
  vec3 h = normalize(v+l); float nh = SAT(dot(n,h)), nl = SAT(dot(n,l)), nv = SAT(dot(n,v))+1e-4;
  float a = r*r; float a2 = a*a; float d = nh*nh*(a2-1.0)+1.0; d = a2/(PI*d*d);
  float k = (r+1.0)*(r+1.0)/8.0; float g = (nv/(nv*(1.0-k)+k))*(nl/(nl*(1.0-k)+k));
  return d*g/(4.0*nv*max(nl,1e-4)+1e-4)*nl;
}
float fresnelS(float c, float f0){ return f0 + (1.0-f0)*pow(1.0-SAT(c), 5.0); }
