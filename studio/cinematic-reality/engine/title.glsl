// ---- chrome 3D title, transparent background (overlaid on the real room) ----
uniform float uSheen;  // 0..1 sweep position of a light bar across the letters
vec3 envRoom(vec3 r){
  float up = r.y*0.5+0.5;
  vec3 c = mix(vec3(0.015,0.012,0.010), vec3(0.16,0.15,0.14), smoothstep(0.30, 0.60, up));
  c = mix(c, vec3(0.30,0.32,0.36), smoothstep(0.80, 1.0, up));
  // strip lights (top and side) reflected in the chrome
  c += vec3(3.2,3.0,2.7)*smoothstep(0.012, 0.0, abs(r.y - 0.42))*0.9;
  c += vec3(2.6,2.4,2.2)*smoothstep(0.93, 0.975, dot(r, normalize(vec3(-0.55, 0.45, 0.70))));
  c += vec3(1.6,1.7,2.0)*smoothstep(0.95, 0.985, dot(r, normalize(vec3(0.7, 0.2, 0.68))));
  c += vec3(3.0,2.8,2.5)*smoothstep(0.03, 0.0, abs(r.x*0.7 + r.y*0.3 - mix(-1.2, 1.2, uSheen)));
  return c;
}
void main(){
  vec3 ro, rd; camRay(gl_FragCoord.xy, ro, rd);
  vec4 o = vec4(0.0);
  float tt = txtTrace(ro, rd, 1e4);
  float cov = 1.0;
  if (tt < 0.0 && gTxtCov > 0.02) { tt = gTxtT; cov = gTxtCov; }
  if (tt > 0.0) {
    vec3 q = ro + rd*tt; vec3 n = txtNormal(q);
    vec3 env = envRoom(reflect(rd, n));
    vec3 L = normalize(vec3(-0.4, 0.6, 0.7));
    vec3 c = txtShade(q, n, rd, env, vec3(1.6,1.5,1.4), L, vec3(0.25,0.23,0.21));
    o = vec4(c*cov, cov);
  }
  outColor = o;
}
