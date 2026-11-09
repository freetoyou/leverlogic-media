import sys, os
# build.py <ordner> [lib1.js lib2.js ...] – libs aus /home/claude/shared/ werden vor scenes.js eingefügt
d = os.path.abspath(sys.argv[1])
head = open('/home/claude/shared/head.html').read(); tail = open('/home/claude/shared/tail.html').read()
libs = ''.join(open(f'/home/claude/shared/{l}').read() + '\n' for l in sys.argv[2:])
sc = open(f'{d}/scenes.js').read()
open(f'{d}/anim.html', 'w').write(head + libs + sc + '\n' + tail)
