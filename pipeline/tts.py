import os, sys; VID = os.path.abspath(sys.argv.pop(1)) if len(sys.argv) > 1 and os.path.isdir(sys.argv[1]) else os.getcwd()
import json, re, subprocess, wave
import numpy as np
sys.path.insert(0, VID)
from script import SCENES

SR = 22050
PIPER = '/home/claude/shared/tools/piper/piper'
MODEL = '/home/claude/shared/tools/en-us-ryan-high.onnx'
OUT = VID + '/build'
# v3.5 (30.10.2026): schneller + dynamischer (vorher length 0.9, Pausen 0.18/0.35, Piper-Standardrauschen)
SENT_GAP, SCENE_GAP, LEAD = 0.08, 0.2, 0.2
LENGTH, NOISE, NOISE_W = 0.8, 0.8, 1.0

def tokens(sentence):
    out = []
    for tok in re.findall(r'\*[^*]+\*|\S+', sentence):
        key = tok.startswith('*')
        tok = tok.strip('*')
        for t in tok.split() if not '|' in tok else [tok]:
            if '|' in t:
                disp, spoken = t.split('|', 1)
                out.append((disp, spoken, key))
            else:
                out.append((t, t, key))
    return out

def read(path):
    with wave.open(path) as w:
        return np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768

def trim(a, thr=0.012):
    idx = np.where(np.abs(a) > thr)[0]
    if len(idx) == 0: return a
    s = max(idx[0] - int(0.02 * SR), 0); e = min(idx[-1] + int(0.04 * SR), len(a))
    return a[s:e]

os.makedirs(OUT, exist_ok=True)
audio = [np.zeros(int(LEAD * SR), np.float32)]
t = LEAD
timeline = {'scenes': [], 'words': []}
n = 0
for si, (name, sents) in enumerate(SCENES):
    if si > 0:
        audio.append(np.zeros(int(SCENE_GAP * SR), np.float32)); t += SCENE_GAP
    scene_start = t
    for ki, s in enumerate(sents):
        if ki > 0:
            audio.append(np.zeros(int(SENT_GAP * SR), np.float32)); t += SENT_GAP
        toks = tokens(s)
        spoken = ' '.join(sp for _, sp, _ in toks)
        n += 1
        wav = f'{OUT}/s{n:02d}.wav'
        subprocess.run([PIPER, '-m', MODEL, '-f', wav, '--length_scale', str(LENGTH), '--noise_scale', str(NOISE), '--noise_w', str(NOISE_W)], input=spoken.encode(), check=True, capture_output=True)
        a = trim(read(wav))
        dur = len(a) / SR
        weights = [len(re.sub(r'[^A-Za-z0-9]', '', sp)) + 2.5 + (3 if re.search(r'[.,?!:]$', sp) else 0) for _, sp, _ in toks]
        tot = sum(weights); acc = 0
        for (disp, sp, key), w in zip(toks, weights):
            t0 = t + dur * acc / tot; acc += w
            t1 = t + dur * acc / tot
            d = re.sub(r"[^A-Za-z0-9.'$,%/:€°-]", '', disp).rstrip('.,:').upper()
            timeline['words'].append({'w': d, 'k': key, 't0': round(t0, 3), 't1': round(t1, 3), 'scene': name})
        audio.append(a); t += dur
    timeline['scenes'].append({'name': name, 't0': round(scene_start, 3), 't1': round(t, 3)})
audio.append(np.zeros(int(0.9 * SR), np.float32)); t += 0.9
timeline['duration'] = round(t, 3)
full = np.concatenate(audio)
with wave.open(f'{OUT}/voice.wav', 'w') as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((np.clip(full, -1, 1) * 32767).astype(np.int16).tobytes())
json.dump(timeline, open(f'{OUT}/timeline.json', 'w'), indent=1)
for s in timeline['scenes']: print(s)
print('duration', timeline['duration'])
print(' '.join(w['w'] for w in timeline['words']))
