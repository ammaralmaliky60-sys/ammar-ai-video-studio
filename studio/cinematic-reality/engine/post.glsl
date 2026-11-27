#version 300 es
precision highp float;
uniform sampler2D uScene;
uniform vec2 uRes, uSrcRes;
uniform float uMode;      // 0 opaque (a = depth m), 1 overlay (a = alpha)
uniform float uFocus;     // focus distance (m); <=0 disables DOF
uniform float uMaxCoc;    // max blur radius in output px
uniform float uExposure;
uniform float uSat;
uniform vec3 uTint;
uniform float uContrast;
uniform float uVignette;
in vec2 vUv; out vec4 outColor;

vec3 aces(vec3 x){ const float a=2.51,b=0.03,c=2.43,d=0.59,e=0.14; return clamp((x*(a*x+b))/(x*(c*x+d)+e),0.0,1.0); }
float coc(float d){ if (uFocus <= 0.0) return 0.0; return uMaxCoc*clamp(1.0 - uFocus/max(d,0.01), 0.0, 1.0); }

void main(){
  vec4 c0 = texture(uScene, vUv);
  vec3 col = c0.rgb; float a = 1.0;
  if (uMode < 0.5 && uFocus > 0.0) {
    float r0 = coc(c0.a);
    vec3 acc = col; float wsum = 1.0;
    const float GA = 2.39996323;
    for (int i = 1; i < 40; i++) {
      float fi = float(i);
      float rr = sqrt(fi/40.0)*uMaxCoc;
      vec2 off = vec2(cos(fi*GA), sin(fi*GA))*rr/uRes;
      vec4 s = texture(uScene, vUv + off);
      float rs = coc(s.a);
      float w = smoothstep(rr-1.5, rr+0.5, min(rs, r0 + 2.0));
      acc += s.rgb*w; wsum += w;
    }
    col = acc/wsum;
  }
  if (uMode > 0.5) { a = c0.a; col = a > 0.0 ? col/a : col; }
  col *= uExposure;
  col = aces(col);
  float l = dot(col, vec3(0.2126,0.7152,0.0722));
  col = mix(vec3(l), col, uSat);
  col = (col - 0.5)*uContrast + 0.5;
  col *= uTint;
  vec2 q = vUv - 0.5; col *= 1.0 - uVignette*dot(q,q)*1.6;
  col = pow(clamp(col,0.0,1.0), vec3(1.0/2.2));
  outColor = vec4(col, a);
}
