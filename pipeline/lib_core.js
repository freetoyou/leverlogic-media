// ---------- lib_core.js (07.11.2026): Bausteine aus lib_safe/lib_story/lib_batch, die die 2D-Videos brauchen ----------
// thumbSafe (lib_safe 05.11.): Thumbnail-Headline fürs Instagram-Raster, max. 800 px breit, y 470
function thumbSafe(c,l1,l2,y=470){c.save();c.font='128px Anton';const mw=Math.max(c.measureText(l1).width,c.measureText(l2).width);const k=Math.min(1,800/mw);
 c.translate(540,y);c.scale(k,k);c.textAlign='center';c.textBaseline='middle';c.lineJoin='round';c.lineWidth=24;c.strokeStyle='#000';
 [[l1,0,'#fff'],[l2,150,COL.yellow]].forEach(([s,yy,col])=>{c.strokeText(s,0,yy);c.fillStyle=col;c.fillText(s,0,yy);});c.restore();}
// hudBox (lib_story 06.11.): Druckmesser
function hudBox(c,t,txt,lab,o={}){const x=o.x||850,y=o.y||700,s=o.s||1,mode=o.mode||'ok';const pulse=mode==='warn'?1+0.06*Math.sin(t*10):1;
 const bg=mode==='warn'?COL.red:mode==='good'?COL.green:'#fff',fg=mode==='ok'?COL.dark:'#fff';c.save();c.translate(x,y);c.scale(s*pulse,s*pulse);
 lifted(c,()=>{c.fillStyle=bg;rr(c,-150,-80,300,160,36);c.fill();},18,10,0.25);c.strokeStyle=COL.dark;c.lineWidth=7;rr(c,-150,-80,300,160,36);c.stroke();
 c.fillStyle=fg;c.font=`${o.size||96}px Anton`;c.textAlign='center';c.textBaseline='middle';c.fillText(txt,0,-10);c.font='800 26px Inter';c.fillText(lab,0,52);c.restore();}
function choiceCard(c,t,t0,x,y,txt,col){const s=popS(t,t0)*(1+0.04*Math.sin(t*6+x));withScale(c,x,y,s,()=>{lifted(c,()=>{c.fillStyle=col;rr(c,-200,-70,400,140,40);c.fill();},18,10,0.25);c.strokeStyle=COL.dark;c.lineWidth=8;rr(c,-200,-70,400,140,40);c.stroke();
 c.fillStyle='#fff';c.font='78px Anton';c.textAlign='center';c.textBaseline='middle';c.lineJoin='round';c.lineWidth=8;c.strokeStyle=COL.dark;c.strokeText(txt,0,6);c.fillText(txt,0,6);});}
// word (lib_batch 01.11.)
function word(c,txt,x,y,size,col=COL.yellow,rot=0,a=1){c.save();c.globalAlpha=a;c.translate(x,y);c.rotate(rot);c.font=`${size}px Anton`;c.textAlign='center';c.textBaseline='middle';c.lineJoin='round';c.lineWidth=size*0.16;c.strokeStyle=COL.dark;c.strokeText(txt,0,0);c.fillStyle=col;c.fillText(txt,0,0);c.restore();}
// Sprechblase mit Spitze nach unten
function bubble(c,x,y,text,col=COL.dark,size=44,o={}){c.save();c.font=`800 ${size}px Inter`;const tw=c.measureText(text).width;const pw=tw+size*1.2,ph=size*1.9;c.translate(x,y);if(o.s)c.scale(o.s,o.s);
 lifted(c,()=>{c.fillStyle=o.bg||'#fff';rr(c,-pw/2,-ph/2,pw,ph,ph*0.45);c.fill();c.beginPath();c.moveTo(-18,ph/2-2);c.lineTo(o.tail||0,ph/2+34);c.lineTo(22,ph/2-2);c.closePath();c.fill();},16,8,0.22);
 c.strokeStyle=LN;c.lineWidth=5;c.beginPath();c.moveTo(-18,ph/2);c.lineTo(o.tail||0,ph/2+34);c.lineTo(22,ph/2);c.stroke();rr(c,-pw/2,-ph/2,pw,ph,ph*0.45);c.stroke();
 c.fillStyle=o.bg||'#fff';c.fillRect(-16,ph/2-6,36,9);c.fillStyle=col;c.textAlign='center';c.textBaseline='middle';c.fillText(text,0,3);c.restore();}
// @Handle-Karte (Kommentar-Einblendung): Kanal-Kommentar mit Name und Text
function handleCard(c,t,t0,x,y,handle,text,o={}){if(t<t0)return;const s=popS(t,t0,0.35)*(o.s||1);withScale(c,x,y,s,()=>{c.font='800 40px Inter';const w1=c.measureText(handle).width;c.font='700 44px Inter';const w2=c.measureText(text).width;const pw=Math.max(w1+110,w2+70,420),ph=150;
 lifted(c,()=>{c.fillStyle='#fff';rr(c,-pw/2,-ph/2,pw,ph,34);c.fill();},20,10,0.28);c.strokeStyle=LN;c.lineWidth=6;rr(c,-pw/2,-ph/2,pw,ph,34);c.stroke();
 c.fillStyle=o.col||COL.blue;c.beginPath();c.arc(-pw/2+46,-30,22,0,7);c.fill();c.strokeStyle=LN;c.lineWidth=3;c.stroke();
 c.fillStyle=o.col||COL.blue;c.font='800 40px Inter';c.textAlign='left';c.textBaseline='middle';c.fillText(handle,-pw/2+82,-28);
 c.fillStyle=COL.dark;c.font='700 44px Inter';c.textAlign='center';c.fillText(text,0,34);});}
