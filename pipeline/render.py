import os, sys; VID = os.path.abspath(sys.argv.pop(1)) if len(sys.argv) > 1 and os.path.isdir(sys.argv[1]) else os.getcwd()
# Aufruf: render.py <ordner> stills 3.0,10.0 | thumb | video [@handle]
# v5 (01.11.2026): Thumbnail wird als erste 0,1 s (3 Frames) VOR das Video gesetzt (Yuyu: immer so). mix.sh verschiebt den Ton um 0,1 s.
import json, base64, subprocess
from playwright.sync_api import sync_playwright
B = VID + '/build'
tl = json.load(open(f'{B}/timeline.json'))
mode = sys.argv[1] if len(sys.argv) > 1 else 'stills'
handle = sys.argv[2] if mode == 'video' and len(sys.argv) > 2 else '@leverlogic'
FPS = 30
THUMB_FRAMES = 3  # 0,1 s bei 30 fps
with sync_playwright() as p:
    br = p.chromium.launch(args=['--allow-file-access-from-files'])
    pg = br.new_page(viewport={'width': 1080, 'height': 1920})
    pg.on('pageerror', lambda e: print('PAGEERROR', e))
    pg.goto('file://' + VID + '/anim.html')
    events = pg.evaluate('([tl,h]) => init(tl,h)', [tl, handle])
    json.dump(events, open(f'{B}/events.json', 'w'))
    grab = "q => { render(q.t); return document.getElementById('c').toDataURL('image/jpeg', q.q); }"
    thumb_js = "q => { const T=TITLE; thumb(); const d=document.getElementById('c').toDataURL(q.png?'image/png':'image/jpeg', 0.95); TITLE=T; return d; }"
    if mode == 'stills':
        for t in [float(x) for x in sys.argv[2].split(',')]:
            d = pg.evaluate(grab, {'t': t, 'q': 0.7})
            open(f'{B}/still_{t:05.2f}.jpg', 'wb').write(base64.b64decode(d.split(',')[1]))
        print('events', len(events))
    elif mode == 'thumb':
        d = pg.evaluate(thumb_js, {'png': True})
        open(f'{B}/thumbnail.png', 'wb').write(base64.b64decode(d.split(',')[1]))
    else:
        out = f'{B}/video.mp4'
        n = int(tl['duration'] * FPS)
        ff = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', str(FPS), '-c:v', 'mjpeg', '-i', '-',
                               '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '18', '-pix_fmt', 'yuv420p', out], stdin=subprocess.PIPE)
        th = base64.b64decode(pg.evaluate(thumb_js, {'png': False}).split(',')[1])
        for _ in range(THUMB_FRAMES): ff.stdin.write(th)
        for i in range(n):
            d = pg.evaluate(grab, {'t': i / FPS, 'q': 0.95})
            ff.stdin.write(base64.b64decode(d.split(',')[1]))
            if i % 300 == 0: print('frame', i, '/', n, flush=True)
        ff.stdin.close(); ff.wait(); print('done', out)
    br.close()
