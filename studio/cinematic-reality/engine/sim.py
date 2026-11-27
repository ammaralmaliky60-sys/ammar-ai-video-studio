#!/usr/bin/env python3
"""Rigid sphere physics (gravity, floor, back wall, sphere-sphere impulses) -> per-frame positions.
sim(spawns, t0, t1, fps) where spawns = [(t_spawn, x,y,z, r, vx,vy,vz)]
"""
import numpy as np


def simulate(spawns, t_start, t_end, fps=30, wall_z=-12.0, sub=8, seed=0):
    n = len(spawns)
    P = np.array([[s[1], s[2], s[3]] for s in spawns], float)
    V = np.array([[s[5], s[6], s[7]] for s in spawns], float)
    R = np.array([s[4] for s in spawns], float)
    T = np.array([s[0] for s in spawns], float)
    active = np.zeros(n, bool)
    g = np.array([0, -9.81, 0])
    out = []
    dt = 1.0/(fps*sub)
    t = t_start
    nf = int(round((t_end - t_start)*fps)) + 1
    for f in range(nf):
        for s in range(sub):
            active |= (T <= t)
            a = active
            V[a] += g*dt
            P[a] += V[a]*dt
            # floor
            for i in np.where(a)[0]:
                if P[i, 1] < R[i]:
                    P[i, 1] = R[i]
                    if V[i, 1] < 0:
                        V[i, 1] = -V[i, 1]*0.52
                        if abs(V[i, 1]) < 0.35: V[i, 1] = 0.0
                    V[i, [0, 2]] *= 0.985
                if P[i, 2] - R[i] < wall_z:
                    P[i, 2] = wall_z + R[i]
                    if V[i, 2] < 0: V[i, 2] = -V[i, 2]*0.5
            # sphere-sphere
            idx = np.where(a)[0]
            for ii in range(len(idx)):
                i = idx[ii]
                for jj in range(ii+1, len(idx)):
                    j = idx[jj]
                    d = P[j] - P[i]; dist = np.linalg.norm(d); md = R[i] + R[j]
                    if dist < md and dist > 1e-6:
                        nrm = d/dist
                        mi, mj = R[i]**3, R[j]**3
                        pen = md - dist
                        P[i] -= nrm*pen*mj/(mi+mj); P[j] += nrm*pen*mi/(mi+mj)
                        rv = np.dot(V[j] - V[i], nrm)
                        if rv < 0:
                            imp = -(1 + 0.6)*rv/(1/mi + 1/mj)
                            V[i] -= imp/mi*nrm; V[j] += imp/mj*nrm
            t += dt
        frame = []
        for i in range(n):
            if active[i]:
                frame.append([float(P[i, 0]), float(P[i, 1]), float(P[i, 2]), float(R[i])])
            else:
                frame.append([0.0, -50.0, 0.0, 0.0])
        out.append(frame)
    return out
