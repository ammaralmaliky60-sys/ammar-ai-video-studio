void main(){
  vec3 ro, rd; camRay(gl_FragCoord.xy, ro, rd);
  vec3 col; float depth = 5000.0;
  vec3 p;
  float t = seaTrace(ro, rd, p);
  if (rd.y > 0.0 && seaMap(ro + rd*3000.0, 3) > 0.0) {
    col = skyFull(ro, rd);
  } else {
    float dist = length(p - ro);
    vec3 n = seaNormal(p, dist*dist*0.0001 + 0.004);
    col = shadeSea(p, n, rd, dist);
    depth = dist;
    float fog = 1.0 - exp(-dist*uSky.w);
    vec3 hz = skyBase(normalize(vec3(rd.x, 0.004, rd.z)), uSunDir, ZEN, HOR, uSky.y);
    col = mix(col, hz, fog);
  }
  float tt = txtTrace(ro, rd, depth);
  float tcov = 1.0;
  if (tt < 0.0 && gTxtCov > 0.02) { tt = gTxtT; tcov = gTxtCov; }
  if (tt > 0.0) {
    vec3 colBg = col; float depthBg = depth;
    vec3 q = ro + rd*tt; vec3 n = txtNormal(q);
    vec3 r = reflect(rd, n);
    vec3 env = r.y > 0.0 ? skyFull(q, r) : mix(vec3(0.01,0.04,0.06), skyRefl(r), 0.3);
    vec3 amb = mix(vec3(0.03,0.05,0.07), vec3(0.22,0.30,0.42), n.y*0.5+0.5);
    vec3 c = txtShade(q, n, rd, env, SUNC*0.45, uSunDir, amb);
    float fog = 1.0 - exp(-tt*uSky.w);
    c = mix(c, skyRefl(normalize(vec3(rd.x,0.01,rd.z))), fog*0.5);
    col = mix(colBg, c, tcov); depth = tcov > 0.5 ? tt : depthBg;
  }
  outColor = vec4(col, depth);
}
