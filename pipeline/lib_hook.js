// ---------- lib_hook.js (11.11.2026, regel_updates Nr. 5/7): kleine Hook-Sprechblase statt großer Titelbox ----------
// Max. ca. 30 % Bildbreite (<= 324 px), weiß mit dünnem Rand, 6–8 Wörter, EIN Wort farbig, erscheint frühestens 0,35 s, ca. 2,5 s sichtbar.
// lines: Array von Zeilen; key: das farbige Wort (Großschreibung wie im Text); tail: 'down'|'left'|'right' + tx/ty = Spitze relativ zur Blase.
let HOOKW=0;
function hookBubble(c,t,x,y,lines,o={}){const t0=o.t0==null?0.35:o.t0,t1=o.t1==null?3.0:o.t1;if(t<t0||t>t1+0.3)return;
 const pin=popS(t,t0,0.3),pout=t>t1?eo((t-t1)/0.3):0;const size=o.size||34,lh=size*1.18,pad=size*0.55;
 c.save();c.font=`800 ${size}px Inter`;const mw=Math.max(...lines.map(l=>c.measureText(l).width));const bw=mw+pad*2,bh=lines.length*lh+pad*1.3;HOOKW=bw;
 c.globalAlpha=1-pout;c.translate(x,y-pout*30);c.scale(pin,pin);
 const tx=o.tx==null?-bw*0.2:o.tx,ty=o.ty==null?bh/2+40:o.ty;
 c.shadowColor='rgba(0,0,0,0.25)';c.shadowBlur=14;c.shadowOffsetY=6;c.fillStyle='#fff';rr(c,-bw/2,-bh/2,bw,bh,size*0.8);c.fill();
 c.beginPath();const bx=clamp(tx*0.5,-bw/2+30,bw/2-30);if(Math.abs(ty)>bh/2){const sy=ty>0?bh/2-2:-bh/2+2;c.moveTo(bx-16,sy);c.lineTo(tx,ty);c.lineTo(bx+16,sy);}else{const sx=tx>0?bw/2-2:-bw/2+2;c.moveTo(sx,-14);c.lineTo(tx,ty);c.lineTo(sx,14);}c.closePath();c.fill();c.shadowColor='transparent';
 c.strokeStyle=LN;c.lineWidth=3;rr(c,-bw/2,-bh/2,bw,bh,size*0.8);c.stroke();
 c.beginPath();if(Math.abs(ty)>bh/2){const sy=ty>0?bh/2:-bh/2;c.moveTo(bx-16,sy);c.lineTo(tx,ty);c.lineTo(bx+16,sy);}else{const sx=tx>0?bw/2:-bw/2;c.moveTo(sx,-14);c.lineTo(tx,ty);c.lineTo(sx,14);}c.stroke();
 c.fillStyle='#fff';if(Math.abs(ty)>bh/2){const sy=ty>0?bh/2-4:-bh/2-1;c.fillRect(bx-14,sy,28,5);}
 c.textBaseline='middle';lines.forEach((l,i)=>{const ly=-bh/2+pad*0.65+lh*(i+0.5);const words=l.split(' ');let cx=-c.measureText(l).width/2;c.textAlign='left';
  words.forEach((w,k)=>{const ww=c.measureText(w+(k<words.length-1?' ':'')).width;const clean=w.replace(/[^A-Z']/gi,'').toUpperCase();c.fillStyle=(o.key&&clean===o.key)?(o.keyCol||COL.red):COL.dark;c.fillText(w,cx,ly);cx+=ww;});});
 c.restore();}
