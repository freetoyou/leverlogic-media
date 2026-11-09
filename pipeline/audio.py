import os, sys; VID = os.path.abspath(sys.argv.pop(1)) if len(sys.argv) > 1 and os.path.isdir(sys.argv[1]) else os.getcwd()
# Musik pro Video: Stil aus <video>/music.json {"style": "funky"|"curious"|"lounge"|"diner"|"pulse"|"cosmic"|"stomp"}
# v3.4 (30.10.2026): Musik ca. -19 dBFS RMS, weicheres Ducking im mix.sh
# v3.6 (01.11.2026): neuer Stil "stomp" (Stadion: Stampf-Stampf-Klatsch), neue SFX "rumble" (Beben) und "cheer" (Menge)
import json, wave
import numpy as np
from scipy.signal import butter, lfilter, resample_poly

MUSIC_DB = -19
B = VID + '/build'
SR = 44100
tl = json.load(open(f'{B}/timeline.json'))
events = json.load(open(f'{B}/events.json'))
STYLE = json.load(open(f'{VID}/music.json'))['style']
DUR = tl['duration']
N = int(DUR * SR) + SR
rng = np.random.default_rng(7)

def env(n, a, d):
    t = np.arange(n) / SR
    return np.minimum(t / a, 1) * np.exp(-t / d)
def bp(x, lo, hi):
    b, a = butter(2, [lo / (SR / 2), hi / (SR / 2)], 'band'); return lfilter(b, a, x)
def lp(x, f):
    b, a = butter(2, f / (SR / 2)); return lfilter(b, a, x)
def hp(x, f):
    b, a = butter(2, f / (SR / 2), 'high'); return lfilter(b, a, x)

# ---------------- SFX ----------------
def pop(semi):
    n = int(0.12 * SR); t = np.arange(n) / SR; k = 2 ** (semi / 12)
    f = (900 * np.exp(-t * 30) + 380) * k
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * env(n, 0.002, 0.035) * 0.9
def swipe(semi):
    n = int(0.22 * SR); x = rng.standard_normal(n); k = 2 ** (semi / 12)
    out = np.zeros(n)
    for i, lo in enumerate(np.linspace(800, 3500, 8)):
        seg = slice(i * n // 8, (i + 1) * n // 8)
        out[seg] = bp(x, lo * k, lo * k * 1.6)[seg]
    t = np.arange(n) / n
    return out * np.sin(np.pi * t) ** 1.5 * 1.6
def boom():
    n = int(0.9 * SR); t = np.arange(n) / SR
    f = 40 + 110 * np.exp(-t * 9)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * env(n, 0.003, 0.28)
    hit = lp(rng.standard_normal(n), 2500) * env(n, 0.001, 0.05) * 0.6
    return body + hit
def whoosh():
    n = int(0.45 * SR); x = rng.standard_normal(n); t = np.arange(n) / n
    out = np.zeros(n)
    for i, f in enumerate(np.linspace(300, 2500, 10)):
        seg = slice(i * n // 10, (i + 1) * n // 10)
        out[seg] = bp(x, f, f * 2)[seg]
    return out * np.sin(np.pi * t) ** 2 * 1.2
def roar():
    n = int(1.0 * SR); x = rng.standard_normal(n)
    return lp(x, 900) * env(n, 0.02, 0.35) * 2.2
def tick():
    n = int(0.03 * SR); t = np.arange(n) / SR
    return np.sin(2 * np.pi * 2200 * t) * env(n, 0.001, 0.006)
def ding():
    n = int(0.6 * SR); t = np.arange(n) / SR
    return (np.sin(2 * np.pi * 1320 * t) + 0.5 * np.sin(2 * np.pi * 1980 * t)) * env(n, 0.002, 0.18) * 0.7
def rumble():
    n = int(1.4 * SR); t = np.arange(n) / SR
    x = lp(rng.standard_normal(n), 140) * 6 + np.sin(2 * np.pi * 38 * t) * 0.5
    return x * np.minimum(t / 0.15, 1) * np.exp(-t / 0.7) * (1 + 0.4 * np.sin(2 * np.pi * 7 * t))
def cheer():
    n = int(1.6 * SR); t = np.arange(n) / SR
    x = bp(rng.standard_normal(n), 500, 3500) * (1 + 0.3 * np.sin(2 * np.pi * 5.5 * t))
    return x * np.minimum(t / 0.25, 1) * np.exp(-t / 0.8) * 1.4
# v3.7 (03.11.2026): "hum" (Leuchten/Summen), "ring" (Telefon-Klingeln), "beep" (Tastenton)
def hum():
    n = int(0.8 * SR); t = np.arange(n) / SR
    x = sum(np.sin(2 * np.pi * f * t) for f in (220, 330, 440.8)) / 3 * (1 + 0.3 * np.sin(2 * np.pi * 9 * t))
    return x * np.minimum(t / 0.12, 1) * np.exp(-t / 0.4) * 0.9
def ring():
    n = int(0.9 * SR); t = np.arange(n) / SR
    x = (np.sin(2 * np.pi * 440 * t) + np.sin(2 * np.pi * 480 * t)) / 2 * (np.sin(2 * np.pi * 20 * t) > 0)
    return x * np.minimum(t / 0.01, 1) * np.minimum((0.9 - t) / 0.05, 1) * 0.6
def beep():
    n = int(0.12 * SR); t = np.arange(n) / SR
    return (np.sin(2 * np.pi * 697 * t) + np.sin(2 * np.pi * 1209 * t)) / 2 * env(n, 0.002, 0.08)
# v3.8 (05.11.2026): "splash" (Aufprall Wasser), "bubble" (Blubbern), "alarm" (Wecker-Piepen), "zap" (Funk-Zischen), "crack" (Glas bricht)
def splash():
    n = int(0.9 * SR); t = np.arange(n) / SR
    x = bp(rng.standard_normal(n), 300, 5000) * np.minimum(t / 0.01, 1) * np.exp(-t / 0.25)
    return x * 1.6 + np.sin(2 * np.pi * np.cumsum(70 + 60 * np.exp(-t * 12)) / SR) * env(n, 0.003, 0.2) * 0.6
def bubble():
    n = int(0.6 * SR); out = np.zeros(n)
    for k in range(6):
        i = int(rng.uniform(0, 0.45) * SR); m = int(0.06 * SR); tt = np.arange(m) / SR
        f = rng.uniform(500, 1100) * (1 + tt * 18)
        s = np.sin(2 * np.pi * np.cumsum(f) / SR) * env(m, 0.002, 0.02)
        out[i:i + m] += s[:n - i]
    return out
def alarm():
    n = int(0.9 * SR); t = np.arange(n) / SR
    gate = ((t % 0.15) < 0.08).astype(float)
    return np.sin(2 * np.pi * 2000 * t) * gate * np.minimum((0.9 - t) / 0.05, 1) * 0.55
def zap():
    n = int(0.35 * SR); t = np.arange(n) / SR
    f = 1800 * np.exp(-t * 6) + 300
    return (np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)) * 0.3 + bp(rng.standard_normal(n), 2000, 7000) * 0.4) * env(n, 0.002, 0.09)
def crack():
    n = int(0.5 * SR); t = np.arange(n) / SR
    x = hp(rng.standard_normal(n), 2500) * env(n, 0.0005, 0.03) * 1.5
    for k in range(5):
        i = int(rng.uniform(0.02, 0.3) * SR); m = int(0.04 * SR)
        x[i:i + m] += hp(rng.standard_normal(m), 4000) * env(m, 0.0005, 0.01)
    return x

prio = {'boom': 3, 'roar': 3, 'rumble': 3, 'splash': 3, 'crack': 3, 'cheer': 2, 'ding': 2, 'whoosh': 2, 'ring': 2, 'hum': 2, 'alarm': 2, 'zap': 2, 'swipe': 1, 'pop': 1, 'beep': 1, 'bubble': 1, 'tick': 0}
kept = []
for e in sorted(events, key=lambda e: e['t']):
    if kept and e['t'] - kept[-1]['t'] < (0.1 if e['type'] in ('tick', 'ding', 'beep') else 0.15):
        if prio[e['type']] > prio[kept[-1]['type']]: kept[-1] = e
        continue
    kept.append(e)
sfx = np.zeros(N)
level = {'pop': 0.32, 'swipe': 0.22, 'whoosh': 0.22, 'boom': 0.75, 'roar': 0.35, 'tick': 0.18, 'ding': 0.3, 'rumble': 0.8, 'cheer': 0.3, 'hum': 0.35, 'ring': 0.3, 'beep': 0.3,
         'splash': 0.6, 'bubble': 0.35, 'alarm': 0.3, 'zap': 0.3, 'crack': 0.5}
for e in kept:
    semi = rng.uniform(-2, 2)
    s = {'pop': lambda: pop(semi), 'swipe': lambda: swipe(semi), 'boom': boom, 'whoosh': whoosh, 'roar': roar, 'tick': tick, 'ding': ding, 'rumble': rumble, 'cheer': cheer, 'hum': hum, 'ring': ring, 'beep': beep,
         'splash': splash, 'bubble': bubble, 'alarm': alarm, 'zap': zap, 'crack': crack}[e['type']]()
    i = int(max(e['t'], 0) * SR)
    s = s[:N - i]; sfx[i:i + len(s)] += s * level[e['type']]
print('sfx events', len(kept), 'of', len(events))

# ---------------- Musik-Bausteine ----------------
music = np.zeros(N)
mid = lambda m: 440 * 2 ** ((m - 69) / 12)
def put(sig, t0, gain=1.0):
    i = int(t0 * SR)
    if i >= N or i < 0: return
    s = sig[:N - i]; music[i:i + len(s)] += s * gain
def osc(f, n, shape='sin'):
    ph = 2 * np.pi * f * np.arange(n) / SR
    if shape == 'sin': return np.sin(ph)
    if shape == 'saw': return 2 * ((f * np.arange(n) / SR) % 1) - 1
    if shape == 'sq': return np.sign(np.sin(ph)) * 0.7
def kick(n=0.3, f0=120, f1=48, d=0.09):
    n = int(n * SR); t = np.arange(n) / SR
    return np.sin(2 * np.pi * np.cumsum(f1 + f0 * np.exp(-t * 28)) / SR) * env(n, 0.002, d)
def snare(d=0.08):
    n = int(0.25 * SR); t = np.arange(n) / SR
    return bp(rng.standard_normal(n), 1200, 6000) * env(n, 0.001, d) * 0.8 + np.sin(2 * np.pi * 190 * t) * env(n, 0.001, 0.04) * 0.6
def hat(d=0.015, lo=7000):
    n = int(0.08 * SR); return bp(rng.standard_normal(n), lo, 14000) * env(n, 0.001, d)
def snap():
    n = int(0.12 * SR); return bp(rng.standard_normal(n), 1800, 5000) * env(n, 0.001, 0.02) * 1.3
def clap():
    n = int(0.2 * SR); x = bp(rng.standard_normal(n), 900, 4500); e = np.zeros(n)
    for k, off in enumerate((0, 0.012, 0.024)):
        i = int(off * SR); e[i:] += env(n - i, 0.001, 0.012 if k < 2 else 0.07)
    return x * e * 1.4
def brush(len_s=0.4):
    n = int(len_s * SR); t = np.arange(n) / n
    return bp(rng.standard_normal(n), 2500, 9000) * np.sin(np.pi * t) ** 2 * 0.35
def ride():
    n = int(0.5 * SR); t = np.arange(n) / SR
    m = sum(np.sin(2 * np.pi * f * t) for f in (3150, 4870, 6230, 7410)) / 4
    return (m * 0.4 + bp(rng.standard_normal(n), 6000, 12000) * 0.5) * env(n, 0.001, 0.18)
def bass(m, dur, bright=900):
    n = int(dur * SR); f = mid(m)
    x = osc(f, n, 'sin') + 0.35 * osc(f, n, 'saw')
    return lp(x, bright) * env(n, 0.005, dur * 0.7) * np.minimum((n - np.arange(n)) / (0.02 * SR), 1)
def pluck(m, dur=0.25, bright=2500):
    n = int(dur * SR); f = mid(m)
    x = osc(f, n, 'saw') * 0.6 + osc(f * 2, n, 'sq') * 0.2
    return lp(x, bright) * env(n, 0.002, dur * 0.35)
def clav(ms, dur=0.12):
    return sum(bp(pluck(m, dur, 4000), 400, 3500) for m in ms) / len(ms)
def marimba(m, dur=0.6):
    n = int(dur * SR); f = mid(m); t = np.arange(n) / SR
    return (np.sin(2 * np.pi * f * t) * env(n, 0.001, 0.22) + 0.35 * np.sin(2 * np.pi * f * 4 * t) * env(n, 0.001, 0.04))
def glock(m, dur=0.8):
    n = int(dur * SR); f = mid(m); t = np.arange(n) / SR
    return (np.sin(2 * np.pi * f * t) + 0.3 * np.sin(2 * np.pi * f * 2.76 * t)) * env(n, 0.001, 0.3)
def epiano(ms, dur):
    n = int(dur * SR); t = np.arange(n) / SR; out = np.zeros(n)
    for m in ms:
        f = mid(m)
        out += np.sin(2 * np.pi * f * t + 0.8 * np.sin(2 * np.pi * f * t) * np.exp(-t * 6)) * env(n, 0.004, 1.4)
    out *= 1 + 0.25 * np.sin(2 * np.pi * 4.5 * t)
    return out / len(ms) * np.minimum((n - np.arange(n)) / (0.08 * SR), 1)
def pad(ms, dur):
    n = int(dur * SR); t = np.arange(n) / SR
    x = sum(np.sin(2 * np.pi * mid(m) * t * d) for m in ms for d in (0.997, 1.003)) / (2 * len(ms))
    return x * np.minimum(t / 0.5, 1) * np.minimum((dur - t) / 0.5, 1)
def honky(ms, dur=0.18):
    n = int(dur * SR); t = np.arange(n) / SR; out = np.zeros(n)
    for m in ms:
        f = mid(m)
        for d in (1.0, 1.006):
            out += (np.sin(2 * np.pi * f * d * t) + 0.4 * np.sin(4 * np.pi * f * d * t) + 0.15 * np.sin(6 * np.pi * f * d * t))
    return out / (2 * len(ms)) * env(n, 0.002, dur * 0.5)
def synth(m, dur, cut=1800):
    n = int(dur * SR); f = mid(m)
    x = osc(f, n, 'saw') * 0.5 + osc(f * 1.005, n, 'saw') * 0.5
    return lp(x, cut) * env(n, 0.004, dur * 0.4)

# ---------------- Stile ----------------
if STYLE == 'funky':
    bpm = 108; b = 60 / bpm; s16 = b / 4; bar = 4 * b
    prog = [(40, [52, 55, 59, 62]), (40, [52, 55, 59, 62]), (45, [57, 61, 64, 67]), (45, [55, 57, 61, 64])]
    riff = [(0, 0), (3, 0), (6, 12), (8, 0), (10, 3), (11, 5), (14, 7)]
    for bi in range(int(DUR / bar) + 2):
        root, ch = prog[bi % 4]; t0 = bi * bar
        for st, off in riff: put(bass(root + off, s16 * 1.6, 1100), t0 + st * s16, 0.8)
        for st in (2, 5, 9, 13): put(clav(ch), t0 + st * s16, 0.45)
        for q in range(4):
            if q in (0, 2): put(kick(), t0 + q * b, 0.9)
            if q in (1, 3): put(snare(), t0 + q * b, 0.5)
        put(kick(), t0 + 10 * s16, 0.6)
        for st in range(16): put(hat(0.012 if st % 2 else 0.02), t0 + st * s16, 0.18 if st % 2 else 0.28)
        if bi % 2 == 1: put(glock(ch[-1] + 12, 0.5), t0 + 15 * s16, 0.12)
    cutoff = 7000
elif STYLE == 'curious':
    bpm = 92; b = 60 / bpm; e8 = b / 2; bar = 4 * b
    prog = [(48, [60, 64, 67, 72]), (45, [57, 60, 64, 69]), (41, [57, 60, 65, 69]), (43, [59, 62, 67, 71])]
    pat = [0, 1, 2, 3, 2, 1, 2, 3]
    for bi in range(int(DUR / bar) + 2):
        root, ch = prog[bi % 4]; t0 = bi * bar
        put(bass(root, bar * 0.9, 500), t0, 0.55)
        for k, p in enumerate(pat): put(marimba(ch[p], 0.5), t0 + k * e8, 0.55 if k % 2 == 0 else 0.4)
        if bi % 4 == 3: put(glock(ch[1] + 12), t0 + 3.5 * b, 0.25); put(glock(ch[3] + 12), t0 + 3.75 * b, 0.25)
        for q in range(4):
            if q in (1, 3): put(snap(), t0 + q * b, 0.35)
            if q == 0: put(kick(0.25, 90, 50, 0.07), t0, 0.5)
        put(pad(ch[:3], bar), t0, 0.12)
    cutoff = 6000
elif STYLE == 'lounge':
    bpm = 78; b = 60 / bpm; bar = 4 * b; sw = b * 2 / 3
    prog = [(38, [53, 57, 60, 64]), (43, [53, 59, 64, 69]), (36, [52, 55, 59, 62]), (45, [55, 58, 61, 64])]
    walks = [[38, 41, 45, 48], [43, 47, 50, 49], [36, 40, 43, 44], [45, 44, 43, 37]]
    for bi in range(int(DUR / bar) + 2):
        root, ch = prog[bi % 4]; t0 = bi * bar
        put(epiano(ch, bar * 0.95), t0, 0.6)
        put(epiano(ch[1:], b * 0.6), t0 + 2.5 * b + (sw - b / 2), 0.25)
        for q, m in enumerate(walks[bi % 4]): put(bass(m, b * 0.9, 700), t0 + q * b, 0.6)
        for q in range(4):
            put(ride(), t0 + q * b, 0.16)
            if q in (1, 3): put(ride(), t0 + q * b + sw, 0.1); put(brush(0.35), t0 + q * b, 0.5)
            if q == 0: put(kick(0.3, 70, 45, 0.1), t0, 0.35)
    cutoff = 5500
elif STYLE == 'diner':
    bpm = 126; b = 60 / bpm; bar = 4 * b; sw = b * 2 / 3
    prog = [(36, [60, 64, 67, 70]), (41, [60, 65, 69, 70]), (36, [60, 64, 67, 70]), (43, [62, 65, 67, 71])]
    boog = [0, 4, 7, 9, 10, 9, 7, 4]
    for bi in range(int(DUR / bar) + 2):
        root, ch = prog[bi % 4]; t0 = bi * bar
        for k, off in enumerate(boog): put(bass(root + off, b * 0.45, 1000), t0 + (k // 2) * b + (k % 2) * sw, 0.7)
        for q in range(4): put(honky(ch, 0.16), t0 + q * b + sw, 0.42)
        for q in range(4):
            if q in (0, 2): put(kick(0.25, 100, 50, 0.08), t0 + q * b, 0.75)
            if q in (1, 3): put(snare(0.06), t0 + q * b, 0.45)
            put(hat(0.02), t0 + q * b, 0.22); put(hat(0.012), t0 + q * b + sw, 0.14)
        if bi % 2 == 1:
            for k, m in enumerate([ch[3] + 12, ch[2] + 12, ch[1] + 12]): put(honky([m], 0.2), t0 + 3 * b + k * sw / 1.5, 0.3)
    cutoff = 6500
elif STYLE == 'pulse':
    bpm = 100; b = 60 / bpm; s16 = b / 4; bar = 4 * b
    prog = [(45, [57, 60, 64, 69]), (41, [57, 60, 65, 69]), (43, [55, 59, 62, 67]), (40, [56, 59, 64, 68])]
    pat = [0, 2, 1, 3, 2, 1, 3, 2]
    for bi in range(int(DUR / bar) + 2):
        root, ch = prog[bi % 4]; t0 = bi * bar
        for st in range(16): put(synth(ch[pat[st % 8]] + 12, s16 * 0.9, 2200 + 600 * np.sin(bi + st / 3)), t0 + st * s16, 0.28 if st % 4 else 0.38)
        for q in range(4): put(bass(root, b * 0.7, 600), t0 + q * b + s16 * 2, 0.6)
        for q in range(4):
            put(kick(0.28, 110, 45, 0.1), t0 + q * b, 0.8)
            if q in (1, 3): put(snap(), t0 + q * b, 0.3)
            put(hat(0.01, 9000), t0 + q * b + s16 * 2, 0.2)
        put(pad(ch[:3], bar), t0, 0.1)
    cutoff = 7000
elif STYLE == 'stomp':
    # Stadion-Groove: Stampf-Stampf-Klatsch, Pop-Akkorde, treibender Achtel-Bass (Taylor Swift, 01.11.2026)
    bpm = 116; b = 60 / bpm; e8 = b / 2; bar = 4 * b
    prog = [(36, [60, 64, 67]), (43, [59, 62, 67]), (45, [57, 60, 64]), (41, [57, 60, 65])]
    for bi in range(int(DUR / bar) + 2):
        root, ch = prog[bi % 4]; t0 = bi * bar
        for half in (0, 2):
            put(kick(0.35, 90, 42, 0.14), t0 + half * b, 1.0)
            put(kick(0.35, 90, 42, 0.14), t0 + half * b + e8, 0.85)
            put(clap(), t0 + (half + 1) * b, 0.75)
        for k in range(8): put(bass(root + (12 if k % 4 == 3 else 0), e8 * 0.9, 700), t0 + k * e8, 0.55)
        for k in range(8): put(synth(ch[k % 3] + 12, e8 * 0.8, 2600), t0 + k * e8, 0.22 if k % 2 else 0.3)
        put(pad([m + 12 for m in ch], bar), t0, 0.14)
        for k in range(8): put(hat(0.012, 8000), t0 + k * e8 + e8 / 2, 0.16)
    cutoff = 7500
elif STYLE == 'sneaky':
    # v3.7 (03.11.2026): Schleich-Groove (Pizzicato-Bass, gezupfte Moll-Töne, Fingerschnipsen) – für Lügen/Ertappt-Themen
    bpm = 96; b = 60 / bpm; e8 = b / 2; bar = 4 * b
    prog = [(45, [57, 60, 64]), (45, [57, 60, 64]), (41, [57, 60, 65]), (40, [56, 59, 64])]
    walk = [0, 0, 7, 0, 3, 0, 7, 5]
    for bi in range(int(DUR / bar) + 2):
        root, ch = prog[bi % 4]; t0 = bi * bar
        for k, off in enumerate(walk): put(bass(root + off, e8 * 0.55, 800), t0 + k * e8, 0.75 if k % 2 == 0 else 0.5)
        for k in (1, 3, 6): put(pluck(ch[k % 3] + 12, 0.18, 3000), t0 + k * e8, 0.35)
        for q in (1, 3): put(snap(), t0 + q * b, 0.45)
        put(kick(0.25, 80, 48, 0.08), t0, 0.55); put(kick(0.25, 80, 48, 0.08), t0 + 2.5 * b, 0.4)
        for k in range(8): put(hat(0.01, 9000), t0 + k * e8, 0.12)
        if bi % 2 == 1: put(glock(ch[2] + 24, 0.5), t0 + 3.5 * b, 0.12)
    cutoff = 6500
elif STYLE == 'tense':
    # v3.7 (03.11.2026): Spannung (Notruf): Herzschlag-Kick, tiefer Puls-Bass, hohe Streicher-Fläche
    bpm = 84; b = 60 / bpm; e8 = b / 2; bar = 4 * b
    prog = [(38, [62, 65, 69]), (38, [62, 65, 70]), (36, [60, 64, 67]), (37, [61, 64, 68])]
    for bi in range(int(DUR / bar) + 2):
        root, ch = prog[bi % 4]; t0 = bi * bar
        for q in range(4):
            put(kick(0.3, 70, 42, 0.11), t0 + q * b, 0.85); put(kick(0.3, 70, 42, 0.08), t0 + q * b + b * 0.28, 0.5)
        for k in range(8): put(bass(root, e8 * 0.7, 420), t0 + k * e8, 0.45)
        put(pad([m + 12 for m in ch], bar), t0, 0.32)
        for k in range(8): put(hat(0.008, 9500), t0 + k * e8 + e8 / 2, 0.1)
        if bi % 2 == 1: put(glock(ch[0] + 24, 1.0), t0 + 3 * b, 0.1)
    cutoff = 6000
elif STYLE == 'urgent':
    # v3.8 (05.11.2026): Countdown-Druck (Auto im Wasser): treibende 16tel-Synth-Ostinato in Moll, Tom-Schläge, steigende Spannung
    bpm = 122; b = 60 / bpm; s16 = b / 4; bar = 4 * b
    prog = [(38, [62, 65, 69]), (38, [62, 65, 69]), (34, [58, 62, 65]), (36, [60, 64, 67])]
    for bi in range(int(DUR / bar) + 2):
        root, ch = prog[bi % 4]; t0 = bi * bar
        for st in range(16): put(synth(ch[st % 3] + (12 if st % 8 == 7 else 0), s16 * 0.8, 1600 + 400 * (bi % 4)), t0 + st * s16, 0.24 if st % 2 else 0.32)
        for k in range(8): put(bass(root, b / 2 * 0.8, 500), t0 + k * b / 2, 0.55)
        for q in range(4):
            put(kick(0.3, 100, 44, 0.1), t0 + q * b, 0.85)
            if q in (1, 3): put(snare(0.05), t0 + q * b, 0.35)
        put(kick(0.4, 60, 70, 0.18), t0 + 3.5 * b, 0.45)
        put(pad([m + 12 for m in ch], bar), t0, 0.16)
    cutoff = 6500
elif STYLE == 'bounce':
    # v3.9 (07.11.2026): verspielter Pop-Groove (Earworm): Ohrwurm-Hook auf Glockenspiel/Marimba, Off-Beat-Bass, Klatschen
    bpm = 112; b = 60 / bpm; e8 = b / 2; bar = 4 * b
    prog = [(41, [65, 69, 72]), (43, [67, 71, 74]), (40, [64, 67, 71]), (45, [64, 69, 72])]
    hook = [72, 74, 76, 74, 72, 69, 72, 0]
    for bi in range(int(DUR / bar) + 2):
        root, ch = prog[bi % 4]; t0 = bi * bar
        for k in range(8): put(bass(root + (7 if k % 4 == 2 else 0), e8 * 0.7, 800), t0 + k * e8 + (e8 / 2 if k % 2 else 0), 0.55)
        for q in range(4):
            put(kick(0.28, 100, 48, 0.09), t0 + q * b, 0.75 if q % 2 == 0 else 0.45)
            if q in (1, 3): put(clap(), t0 + q * b, 0.5)
        for k, m in enumerate(hook):
            if m and bi % 2 == 0: put(marimba(m, 0.45), t0 + k * e8, 0.45)
        if bi % 2 == 1: put(glock(ch[2] + 12, 0.7), t0 + 2 * b, 0.18)
        for k in range(8): put(hat(0.01, 8500), t0 + k * e8 + e8 / 2, 0.14)
        put(pad(ch, bar), t0, 0.1)
    cutoff = 7000
else:
    bpm = 70; b = 60 / bpm; bar = 4 * b
    prog = [(38, [50, 57, 62, 65]), (34, [50, 58, 62, 65]), (36, [48, 55, 60, 64]), (33, [49, 57, 61, 64])]
    for bi in range(int(DUR / bar) + 2):
        root, ch = prog[bi % 4]; t0 = bi * bar
        put(pad(ch, bar * 1.05), t0, 0.5)
        put(bass(root, bar * 0.95, 300), t0, 0.5)
        for k, m in enumerate([ch[3] + 12, ch[2] + 12, ch[1] + 24, ch[2] + 12]): put(glock(m, 1.2), t0 + k * b + (0.5 * b if k % 2 else 0), 0.18)
        put(kick(0.4, 60, 38, 0.18), t0, 0.5); put(kick(0.4, 60, 38, 0.18), t0 + 2 * b, 0.35)
        put(brush(1.0), t0 + 1.5 * b, 0.3)
    cutoff = 5000

t = np.arange(N) / SR
music = lp(hp(music, 40), cutoff)
fade = np.minimum(np.minimum(t / 0.8, 1), np.clip((DUR + 0.6 - t) / 1.2, 0, 1)); music *= fade
music *= 10 ** (MUSIC_DB / 20) / (np.sqrt(np.mean(music[: int(DUR * SR)] ** 2)) + 1e-9)

with wave.open(f'{B}/voice.wav') as w:
    v = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float64) / 32768
v = resample_poly(v, 2, 1)[:N]; voice = np.zeros(N); voice[:len(v)] = v
voice *= 10 ** (-16 / 20) / (np.sqrt(np.mean(voice[voice != 0] ** 2)) + 1e-9)
sfx *= 10 ** (-24 / 20) / (np.sqrt(np.mean(sfx[np.abs(sfx) > 1e-4] ** 2)) + 1e-9)

def save(name, x):
    with wave.open(f'{B}/{name}.wav', 'w') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((np.clip(x, -1, 1) * 32767).astype(np.int16).tobytes())
save('voice44', voice); save('sfx', sfx); save('music', music)
print('ok', STYLE)
