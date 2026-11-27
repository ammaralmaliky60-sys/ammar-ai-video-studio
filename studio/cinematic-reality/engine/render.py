#!/usr/bin/env python3
"""Headless WebGL2 (SwiftShader) renderer for the GLSL scenes.
Usage: render.py JOB.json   (job: scene, W,H,RW,RH, includes, textures, frames[{name,U,P}], out)
"""
import asyncio, base64, json, os, sys, time
from playwright.async_api import async_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
ARGS = ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist',
        '--disable-gpu-watchdog', '--disable-features=GpuWatchdog']


def src(name):
    return open(os.path.join(HERE, name), encoding='utf-8').read()


def data_url(path):
    ext = os.path.splitext(path)[1].lower().strip('.')
    mime = 'image/png' if ext == 'png' else 'image/jpeg'
    return f'data:{mime};base64,' + base64.b64encode(open(path, 'rb').read()).decode()


async def run(job):
    os.makedirs(job['out'], exist_ok=True)
    async with async_playwright() as p:
        b = await p.chromium.launch(args=ARGS, **({'executable_path': os.environ['CR_CHROME']} if os.environ.get('CR_CHROME') else {}))
        pg = await b.new_page()
        pg.set_default_timeout(0)
        await pg.goto('file://' + os.path.join(HERE, 'engine.html'))
        print(await pg.evaluate('([w,h,rw,rh]) => init(w,h,rw,rh)', [job['W'], job['H'], job.get('RW', job['W']), job.get('RH', job['H'])]), flush=True)
        await pg.evaluate('([n,s]) => addProgram(n,s)', ['post', src('post.glsl')])
        inc = job.get('includes', ['common.glsl'])
        scene_src = '\n'.join(src(f) for f in inc) + '\n' + src(job['scene'] + '.glsl')
        try:
            await pg.evaluate('([n,s]) => addProgram(n,s)', [job['scene'], scene_src])
        except Exception as e:
            print(str(e)[:3000]); raise
        async def load_tex(k, v):
            opts = {}
            if isinstance(v, dict):
                opts = v; v = v['path']
            if v.endswith('.npy'):
                import numpy as np
                a = np.load(v).astype(np.float32)
                a = np.ascontiguousarray(a[::-1])  # GL origin bottom-left
                ch = 1 if a.ndim == 2 else a.shape[2]
                print('ftex', k, await pg.evaluate('([n,w,h,b,c]) => loadFloatTex(n,w,h,b,c)',
                                                   [k, a.shape[1], a.shape[0], base64.b64encode(a.tobytes()).decode(), ch]), flush=True)
            else:
                print('tex', k, await pg.evaluate('([n,u,o]) => loadTexture(n,u,o)', [k, data_url(v), opts]), flush=True)
        for k, v in job.get('textures', {}).items():
            await load_tex(k, v)
        t0 = time.time()
        for i, fr in enumerate(job['frames']):
            outp = os.path.join(job['out'], fr['name'])
            for k, v in fr.get('textures', {}).items():
                await load_tex(k, v)
            if job.get('skip_existing') and os.path.exists(outp):
                continue
            url = await pg.evaluate('([s,U,P]) => renderFrame(s,U,P)', [job['scene'], fr['U'], fr.get('P', {})])
            with open(outp, 'wb') as f:
                f.write(base64.b64decode(url.split(',', 1)[1]))
            if i % 5 == 0 or i == len(job['frames']) - 1:
                el = time.time() - t0
                print(f'{job["scene"]}: {i+1}/{len(job["frames"])}  {el/(i+1):.2f}s/frame', flush=True)
        await b.close()


if __name__ == '__main__':
    asyncio.run(run(json.load(open(sys.argv[1]))))
