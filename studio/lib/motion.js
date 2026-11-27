// Frame-based motion primitives (Remotion-style API, zero dependencies).
// Every visual is a pure function of the frame number, so renders are deterministic.

export const clamp = (v, a = 0, b = 1) => Math.min(b, Math.max(a, v));

export const Easing = {
  linear: (t) => t,
  inOut: (t) => (t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2),
  out: (t) => 1 - Math.pow(1 - t, 3),
  outQuint: (t) => 1 - Math.pow(1 - t, 5),
  in: (t) => t * t * t,
};

/** Map frame from input range to output range (multi-stop, clamped). */
export function interpolate(frame, input, output, easing = Easing.linear) {
  if (frame <= input[0]) return output[0];
  if (frame >= input[input.length - 1]) return output[output.length - 1];
  let i = 0;
  while (frame > input[i + 1]) i++;
  const t = easing((frame - input[i]) / (input[i + 1] - input[i]));
  return output[i] + (output[i + 1] - output[i]) * t;
}

/** Damped spring 0 -> 1 starting at `from` frame. */
export function spring(frame, from, { fps = 30, stiffness = 170, damping = 18, mass = 1 } = {}) {
  const t = (frame - from) / fps;
  if (t <= 0) return 0;
  const w0 = Math.sqrt(stiffness / mass);
  const zeta = damping / (2 * Math.sqrt(stiffness * mass));
  if (zeta < 1) {
    const wd = w0 * Math.sqrt(1 - zeta * zeta);
    return 1 - Math.exp(-zeta * w0 * t) * (Math.cos(wd * t) + ((zeta * w0) / wd) * Math.sin(wd * t));
  }
  return 1 - Math.exp(-w0 * t) * (1 + w0 * t);
}

/** Enter/exit envelope: 0 before `in`, eases to 1, holds, eases to 0 at `out`. */
export function presence(frame, inF, outF, fadeIn = 10, fadeOut = 8) {
  if (frame < inF || frame > outF) return 0;
  return Math.min(
    Easing.out(clamp((frame - inF) / fadeIn)),
    Easing.inOut(clamp((outF - frame) / fadeOut)),
  );
}

export const sec = (s, fps = 30) => Math.round(s * fps);
