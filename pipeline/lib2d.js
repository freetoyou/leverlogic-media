// ---------- lib2d.js (06.11.2026): Optik-Standard 2D detailliert (claude/optik_standard_2d.md) ----------
// Referenz: produktion/optik_test_2d.html. Perspektivräume, Straße, detaillierte Figur, Licht-Ebenen, Kamera.
const LN='#1c1f2e';
const ez=x=>{x=clamp(x);return x<0.5?2*x*x:1-Math.pow(-2*x+2,2)/2;};
const rh=(i,s)=>{const v=Math.sin(i*12.9898+s*78.233)*43758.5453;return v-Math.floor(v);};
function P(c,pts,fill,stroke=LN,lw=5){c.beginPath();pts.forEach(([x,y],i)=>i?c.lineTo(x,y):c.moveTo(x,y));c.closePath();if(fill){c.fillStyle=fill;c.fill();}if(stroke){c.lineWidth=lw;c.strokeStyle=stroke;c.lineJoin='round';c.stroke();}}
function LG(c,x0,y0,x1,y1,st){const g=c.createLinearGradient(x0,y0,x1,y1);st.forEach(([o,col])=>g.addColorStop(o,col));return g;}
function RG(c,x,y,r0,r1,st){const g=c.createRadialGradient(x,y,r0,x,y,r1);st.forEach(([o,col])=>g.addColorStop(o,col));return g;}
function glow(c,x,y,r,rgb,a){if(a<=0)return;c.fillStyle=RG(c,x,y,2,r,[[0,`rgba(${rgb},${a})`],[1,`rgba(${rgb},0)`]]);c.beginPath();c.arc(x,y,r,0,7);c.fill();}
// Kamera: s = Zoom, (fx,fy) = Bildmitte in Weltkoordinaten; mit leichtem Schwanken
function camApply(c,t,s,fx,fy,sway=1){fx=clamp(fx,540/s+4,W-540/s-4);fy=clamp(fy,960/s+4,H-960/s-4);c.translate(540,960);c.scale(s,s);c.translate(-fx+Math.sin(t*0.9)*3*sway,-fy+Math.sin(t*1.3)*2*sway);}
function camMove(c,t,t0,t1,a,b){const k=ez((t-t0)/(t1-t0));camApply(c,t,lerp(a[0],b[0],k),lerp(a[1],b[1],k),lerp(a[2],b[2],k));}
function vign(c,a=0.42){c.fillStyle=RG(c,540,960,520,1250,[[0,'rgba(0,0,0,0)'],[1,`rgba(0,0,0,${a})`]]);c.fillRect(0,0,W,H);}
function tint(c,rgba){c.fillStyle=rgba;c.fillRect(0,0,W,H);}
// Perspektiv-Raum. o={bw:{x0,x1,y0,y1}, ceil, wallL, wallR, back, floor, stripes, tiles, floorLines, skirting}
function room3(c,t,o={}){const B=o.bw||{x0:150,x1:930,y0:430,y1:1190};
 P(c,[[0,0],[W,0],[B.x1,B.y0],[B.x0,B.y0]],LG(c,0,0,0,B.y0,o.ceil||[[0,'#d9dde6'],[1,'#eef0f4']]),null);
 P(c,[[0,0],[B.x0,B.y0],[B.x0,B.y1],[0,H]],LG(c,0,0,B.x0,0,o.wallL||[[0,'#b9c3d6'],[1,'#d3dbe8']]),null);
 P(c,[[W,0],[B.x1,B.y0],[B.x1,B.y1],[W,H]],LG(c,W,0,B.x1,0,o.wallR||[[0,'#aeb8cc'],[1,'#ccd4e2']]),null);
 c.fillStyle=LG(c,0,B.y0,0,B.y1,o.back||[[0,'#e2e7ef'],[1,'#d6dce8']]);c.fillRect(B.x0,B.y0,B.x1-B.x0,B.y1-B.y0);
 if(o.stripes){c.save();c.globalAlpha=o.stripes;c.fillStyle='#fff';for(let x=B.x0+12;x<B.x1;x+=38)c.fillRect(x,B.y0,8,B.y1-B.y0);c.restore();}
 if(o.tiles){c.save();c.strokeStyle=o.tiles;c.lineWidth=3;for(let x=B.x0;x<=B.x1;x+=65){c.beginPath();c.moveTo(x,B.y0);c.lineTo(x,B.y1);c.stroke();}for(let y=B.y0;y<=B.y1;y+=65){c.beginPath();c.moveTo(B.x0,y);c.lineTo(B.x1,y);c.stroke();}
  for(let i=1;i<9;i++){const y=B.y0+i*(B.y1-B.y0)/9;c.beginPath();c.moveTo(0,y*(1+(i/9)*0.0)-(B.y0-0)*(1-i/9)*0.9);c.lineTo(B.x0,y);c.stroke();c.beginPath();c.moveTo(W,y-(B.y0)*(1-i/9)*0.9);c.lineTo(B.x1,y);c.stroke();}c.restore();}
 P(c,[[B.x0,B.y1],[B.x1,B.y1],[W,H],[0,H]],LG(c,0,B.y1,0,H,o.floor||[[0,'#c9b39a'],[1,'#a58a6c']]),null);
 if(o.floorLines!==false){c.save();c.globalAlpha=0.09;c.strokeStyle='#000';c.lineWidth=3;for(let i=-10;i<=10;i++){c.beginPath();c.moveTo(540+i*40,B.y1);c.lineTo(540+i*170,H);c.stroke();}c.restore();}
 if(o.skirting!==false){c.fillStyle='#f1ece3';c.fillRect(B.x0,B.y1-22,B.x1-B.x0,22);P(c,[[B.x0,B.y1-22],[B.x0,B.y1],[0,H],[0,H-60]],'#ded7ca',null);P(c,[[B.x1,B.y1-22],[B.x1,B.y1],[W,H],[W,H-60]],'#ded7ca',null);}
 c.strokeStyle='rgba(10,12,20,0.3)';c.lineWidth=4;[[0,0,B.x0,B.y0],[W,0,B.x1,B.y0],[B.x0,B.y1,0,H],[B.x1,B.y1,W,H]].forEach(([a,b,d,e])=>{c.beginPath();c.moveTo(a,b);c.lineTo(d,e);c.stroke();});c.strokeRect(B.x0,B.y0,B.x1-B.x0,B.y1-B.y0);return B;}
// Detaillierte Figur. o={shirt:[dunkel,hell], hair:'short'|'long'|'bald', hairCol, skin:[hell,dunkel], turn -1..1, wide 0..1, mouth:'o'|'smile'|'flat'|'talk', blink, phone, armUp, bust(true=nur Oberkörper), collar, brows:-1..1}
function guy(c,x,y,s,t,o={}){const sh=o.shirt||['#5a3fc4','#7b5cf0'],sk=o.skin||['#ffd9b5','#e9b48a'];c.save();c.translate(x,y+(o.still?0:Math.sin(t*2.2+(o.ph||0))*3*s));c.scale(s,s);
 const bl=o.blink!=null?o.blink:((t+(o.ph||0))%3.4<0.12?1:0);
 if(!o.bust){c.fillStyle=RG(c,0,330,10,150,[[0,'rgba(0,0,0,0.25)'],[1,'rgba(0,0,0,0)']]);c.beginPath();c.ellipse(0,330,150,26,0,0,7);c.fill();
  c.fillStyle=LG(c,-60,0,60,0,[[0,'#2c3550'],[1,'#3d4870']]);rr(c,-70,200,62,130,20);c.fill();c.strokeStyle=LN;c.lineWidth=5;c.stroke();rr(c,8,200,62,130,20);c.fill();c.stroke();
  c.fillStyle='#2a2a30';rr(c,-78,312,74,24,12);c.fill();c.stroke();rr(c,4,312,74,24,12);c.fill();c.stroke();}
 // Arme hinten
 const arm=(side,up)=>{c.save();c.translate(side*96,52);c.rotate(up?side*-2.3:side*0.12);c.fillStyle=LG(c,-20,0,20,0,[[0,sh[0]],[1,sh[1]]]);rr(c,-22,-6,44,150,22);c.fill();c.strokeStyle=LN;c.lineWidth=5;c.stroke();
  c.fillStyle=sk[1];c.beginPath();c.arc(0,150,22,0,7);c.fill();c.stroke();c.restore();};
 // Körper
 c.fillStyle=LG(c,-110,0,110,0,[[0,sh[0]],[0.5,sh[1]],[1,sh[0]]]);c.beginPath();c.moveTo(-115,220);c.quadraticCurveTo(-128,40,-60,20);c.lineTo(60,20);c.quadraticCurveTo(128,40,115,220);c.closePath();c.fill();c.strokeStyle=LN;c.lineWidth=5;c.stroke();
 c.strokeStyle='rgba(0,0,0,0.22)';c.lineWidth=4;c.beginPath();c.moveTo(-66,90);c.quadraticCurveTo(-58,150,-76,210);c.moveTo(66,90);c.quadraticCurveTo(58,150,76,210);c.stroke();
 if(o.collar!==false){c.fillStyle=o.collarCol||'#eceaf6';c.beginPath();c.moveTo(-34,20);c.lineTo(0,60);c.lineTo(34,20);c.closePath();c.fill();c.strokeStyle=LN;c.lineWidth=5;c.stroke();}
 if(!o.phone)arm(-1,false);arm(1,!!o.armUp);
 // Hals + Kopf
 c.fillStyle=sk[1];rr(c,-22,-20,44,46,12);c.fill();c.strokeStyle=LN;c.stroke();
 const tr=o.turn||0,tx=tr*26,wd=o.wide||0;c.save();c.translate(tx*0.3,-90);
 if(o.hair==='long'){c.fillStyle=LG(c,0,-100,0,90,[[0,'#2e1f16'],[1,o.hairCol||'#4a3324']]);c.beginPath();c.moveTo(-92,70);c.quadraticCurveTo(-110,-110,0,-104);c.quadraticCurveTo(110,-110,92,70);c.closePath();c.fill();c.strokeStyle=LN;c.lineWidth=5;c.stroke();}
 c.fillStyle=RG(c,-20,-20,10,110,[[0,sk[0]],[1,sk[1]]]);c.beginPath();c.ellipse(0,0,78,88,0,0,7);c.fill();c.lineWidth=5;c.strokeStyle=LN;c.stroke();
 const earX=tr>0?-78:78;c.fillStyle=sk[1];c.beginPath();c.ellipse(earX*(1-Math.abs(tr)*0.15),6,14,22,0,0,7);c.fill();c.stroke();
 if(o.hair!=='bald'){const hc=o.hairCol||'#4a3324';c.fillStyle=LG(c,0,-100,0,-10,[[0,'#2e1f16'],[1,hc]]);c.beginPath();c.moveTo(-82,-10);c.quadraticCurveTo(-90,-105,0,-100);c.quadraticCurveTo(90,-105,82,-10);c.quadraticCurveTo(60,-60,20+tx,-55);c.quadraticCurveTo(-30,-58,-82,-10);c.closePath();c.fill();c.stroke();
  c.strokeStyle='rgba(255,255,255,0.25)';c.lineWidth=6;c.beginPath();c.arc(-20,-60,30,3.6,4.6);c.stroke();}
 const br=wd*12+(o.brows||0)*8;c.strokeStyle=LN;c.lineWidth=7;c.lineCap='round';[-1,1].forEach(d=>{c.beginPath();c.moveTo(tx+d*22,-30-br+(o.angry?d*-6:0));c.quadraticCurveTo(tx+d*38,-38-br,tx+d*52,-30-br+(o.angry?d*8:0));c.stroke();});
 const er=10+wd*5;[-1,1].forEach(d=>{const ex=tx+d*34;c.fillStyle='#fff';c.beginPath();c.ellipse(ex,-4,er+3,Math.max(1,(er+5)*(1-bl)),0,0,7);c.fill();c.lineWidth=4;c.stroke();
  if(bl<0.8){c.fillStyle='#2a1d14';c.beginPath();c.arc(ex+tr*6,-2,er*0.6,0,7);c.fill();c.fillStyle='#fff';c.beginPath();c.arc(ex+tr*6-3,-6,3,0,7);c.fill();}});
 c.strokeStyle='rgba(120,60,30,0.6)';c.lineWidth=4;c.beginPath();c.moveTo(tx+4,4);c.quadraticCurveTo(tx+12,26,tx,30);c.stroke();
 const m=o.mouth||'flat';c.fillStyle='#5a2a1e';c.strokeStyle='#5a2a1e';c.lineWidth=6;
 if(m==='o'){c.beginPath();c.ellipse(tx,52,11+wd*2,6+wd*12,0,0,7);c.fill();}
 else if(m==='talk'){const k=Math.abs(Math.sin(t*14));c.beginPath();c.ellipse(tx,52,14,3+k*12,0,0,7);c.fill();}
 else if(m==='smile'){c.beginPath();c.arc(tx,38,22,0.35,Math.PI-0.35);c.stroke();}
 else if(m==='grin'){c.fillStyle='#fff';c.beginPath();c.moveTo(tx-30,40);c.quadraticCurveTo(tx,78,tx+30,40);c.closePath();c.fill();c.strokeStyle=LN;c.lineWidth=4;c.stroke();}
 else{c.beginPath();c.moveTo(tx-16,52);c.lineTo(tx+16,52);c.stroke();}
 c.fillStyle='rgba(255,120,120,0.25)';[-1,1].forEach(d=>{c.beginPath();c.ellipse(tx+d*48,26,16,9,0,0,7);c.fill();});
 c.restore();
 if(o.phone){c.save();c.translate(-70,-40);c.rotate(-0.25);c.fillStyle='#22262e';rr(c,-30,-58,60,116,14);c.fill();c.strokeStyle=LN;c.lineWidth=4;c.stroke();c.restore();
  c.save();c.translate(-96,52);c.rotate(2.6);c.fillStyle=LG(c,-20,0,20,0,[[0,sh[0]],[1,sh[1]]]);rr(c,-22,-6,44,120,22);c.fill();c.strokeStyle=LN;c.lineWidth=5;c.stroke();c.fillStyle=sk[1];c.beginPath();c.arc(0,120,22,0,7);c.fill();c.stroke();c.restore();}
 c.restore();}
// Weicher Rauch: Quelle (x,y), Stärke a, Richtung dx
function smoke2(c,t,x,y,t0,a=1,spread=220,n=70,dx=-160,rise=620){if(t<t0)return;for(let i=0;i<n;i++){const u=t-t0-i*0.06;if(u<0)continue;const life=Math.min(u*0.32,1.4);
 const px=x+(rh(i,1)-0.5)*spread+Math.sin(u*1.4+i)*30+life*dx,py=y-life*rise,r=30+life*150;const al=Math.min(1,u*2)*(0.32-life*0.15)*a;if(al<=0)continue;
 c.fillStyle=RG(c,px,py,2,r,[[0,`rgba(185,188,198,${al})`],[1,'rgba(160,162,175,0)']]);c.beginPath();c.arc(px,py,r,0,7);c.fill();}}
// Fenster mit Stadt bei Nacht/Tag
function cityWindow(c,x,y,w,h,t,o={}){c.save();rr(c,x,y,w,h,10);c.clip();const night=o.night!==false;
 c.fillStyle=night?LG(c,0,y,0,y+h,[[0,'#10162b'],[0.55,'#3a2a52'],[1,o.fire?'#ff7a1a':'#4a3a62']]):LG(c,0,y,0,y+h,[[0,'#8fd0ff'],[1,'#fff1d8']]);c.fillRect(x,y,w,h);
 if(o.fire){c.fillStyle='rgba(255,140,40,0.6)';c.beginPath();c.arc(x+w*0.75,y+h+40,w*0.55+8*Math.sin(t*3),0,7);c.fill();}
 [[0,0.45,0.2],[0.18,0.33,0.24],[0.43,0.55,0.18],[0.63,0.27,0.27],[0.86,0.42,0.17]].forEach(([a,b,ww],i)=>{c.fillStyle=night?'#0b1020':'#9fb3c8';c.fillRect(x+a*w,y+b*h,ww*w,h);c.fillStyle=night?'#ffd27a':'#e6f2ff';for(let k=0;k<14;k++){if(rh(i*20+k,3)<0.45)c.fillRect(x+a*w+8+(k%3)*16,y+b*h+14+Math.floor(k/3)*22,8,10);}});
 c.restore();c.strokeStyle='#efe6d4';c.lineWidth=12;c.strokeRect(x,y,w,h);c.lineWidth=7;c.beginPath();c.moveTo(x+w/2,y);c.lineTo(x+w/2,y+h);c.moveTo(x,y+h/2);c.lineTo(x+w,y+h/2);c.stroke();c.strokeStyle=LN;c.lineWidth=4;c.strokeRect(x-6,y-6,w+12,h+12);
 if(o.curtains!==false)[[x-70,1],[x+w+10,-1]].forEach(([cx,d])=>{c.fillStyle=LG(c,cx,0,cx+60,0,[[0,o.curt?o.curt[0]:'#6e2532'],[0.5,o.curt?o.curt[1]:'#a43a4c'],[1,o.curt?o.curt[0]:'#6e2532']]);c.beginPath();c.moveTo(cx,y-40);c.lineTo(cx+60,y-40);c.quadraticCurveTo(cx+60+d*10,y+h/2,cx+60+d*20,y+h+60);c.lineTo(cx-d*10,y+h+60);c.closePath();c.fill();c.strokeStyle=LN;c.lineWidth=4;c.stroke();
  c.strokeStyle='rgba(0,0,0,0.25)';c.lineWidth=3;for(let k=1;k<4;k++){c.beginPath();c.moveTo(cx+k*15,y-40);c.lineTo(cx+k*15+d*k*4,y+h+60);c.stroke();}});
 if(o.curtains!==false){c.fillStyle='#8a6a4a';c.fillRect(x-90,y-50,w+180,12);}}
// Tür mit Kassetten. heat 0..1, open 0..1, num
function door2(c,x,y,w,h,t,o={}){c.fillStyle='#efe6d4';c.fillRect(x-22,y-22,w+44,h+22);c.strokeStyle=LN;c.lineWidth=4;c.strokeRect(x-22,y-22,w+44,h+22);
 if(o.open){c.fillStyle=LG(c,x,0,x+w,0,[[0,'#6c6c76'],[1,'#9a9aa6']]);c.fillRect(x,y,w,h);}
 const ww=w*(1-(o.open||0)*0.8);c.fillStyle=LG(c,x,0,x+ww,0,[[0,'#7a4c2e'],[0.5,'#9a6440'],[1,'#7a4c2e']]);c.fillRect(x,y,ww,h);c.strokeRect(x,y,ww,h);
 if(!o.open){c.strokeStyle='rgba(0,0,0,0.35)';c.lineWidth=4;[[x+w*0.12,y+h*0.07,w*0.76,h*0.37],[x+w*0.12,y+h*0.51,w*0.76,h*0.42]].forEach(([a,b,w2,h2])=>{c.strokeRect(a,b,w2,h2);c.strokeStyle='rgba(255,255,255,0.12)';c.strokeRect(a+5,b+5,w2-10,h2-10);c.strokeStyle='rgba(0,0,0,0.35)';});
  if(o.num){c.fillStyle='#f4ecd8';rr(c,x+w/2-45,y+h*0.2,90,40,8);c.fill();c.fillStyle=LN;c.font='bold 30px Arial';c.textAlign='center';c.textBaseline='middle';c.fillText(o.num,x+w/2,y+h*0.2+21);}
  const hx=x+w-40,hy=y+h*0.51;const heat=o.heat||0;if(heat>0)glow(c,hx,hy,70,'255,110,30',0.9*heat);
  c.fillStyle=heat>0.5?mixHex('#c9d3db','#ff6a2a',heat):'#c9d3db';c.strokeStyle=LN;c.lineWidth=4;rr(c,hx-34,hy-9,40,18,9);c.fill();c.stroke();c.beginPath();c.arc(hx,hy,13,0,7);c.fill();c.stroke();}
 if(o.gap){const f=0.75+0.25*Math.sin(t*9);c.fillStyle=`rgba(255,160,60,${f})`;c.fillRect(x,y+h-6,w,6);glow(c,x+w/2,y+h+10,260,'255,120,30',0.55*f);}}
// Straße in Perspektive (Lever City). o={night, vp:[x,y]}
function street3(c,t,o={}){const vx=o.vp?o.vp[0]:540,vy=o.vp?o.vp[1]:820,night=o.night;
 c.fillStyle=night?LG(c,0,0,0,vy,[[0,'#1b2440'],[1,'#4a4a6e']]):LG(c,0,0,0,vy,[[0,'#7fc6ff'],[1,'#fff0d6']]);c.fillRect(0,0,W,vy+10);
 if(!night){c.fillStyle='rgba(255,255,255,0.85)';[[180,260,1],[820,180,0.8],[560,380,0.6]].forEach(([x,y,s],i)=>{const xx=((x-t*20*(i+1))%(W+300)+W+300)%(W+300)-150;c.beginPath();c.ellipse(xx,y,110*s,40*s,0,0,7);c.ellipse(xx+70*s,y-20*s,80*s,45*s,0,0,7);c.ellipse(xx-60*s,y+5*s,70*s,32*s,0,0,7);c.fill();});}
 // Rathausturm (Lever City Wahrzeichen) am Fluchtpunkt
 c.save();c.translate(vx,vy);c.fillStyle=night?'#3a4058':'#f4e3c1';c.strokeStyle=LN;c.lineWidth=3;c.fillRect(-24,-150,48,150);c.strokeRect(-24,-150,48,150);c.fillStyle=COL.red;c.beginPath();c.moveTo(-32,-150);c.lineTo(0,-200);c.lineTo(32,-150);c.closePath();c.fill();c.stroke();c.fillStyle=night?'#ffe08a':'#fff';c.beginPath();c.arc(0,-112,14,0,7);c.fill();c.stroke();c.restore();
 // Fassaden links/rechts
 const fac=(side)=>{const cols=night?['#4a3f52','#3e4a62','#523e3e']:['#e8b48a','#c9d6e8','#f2d0b8'];for(let i=0;i<5;i++){const z0=i/5,z1=(i+1)/5;
  const xa=side<0?lerp(0,vx-120,z0*0.92):lerp(W,vx+120,z0*0.92),xb=side<0?lerp(0,vx-120,z1*0.92):lerp(W,vx+120,z1*0.92);
  const top0=lerp(-200,vy-260,z0),top1=lerp(-200,vy-260,z1),bot0=lerp(H*0.86,vy+40,z0),bot1=lerp(H*0.86,vy+40,z1);
  P(c,[[xa,top0+i*30*(1-z0)],[xb,top1],[xb,bot1],[xa,bot0]],LG(c,xa,0,xb,0,[[0,cols[i%3]],[1,mixHex(cols[i%3],'#000000',0.18)]]),LN,3);
  for(let f=0;f<6;f++){const fy0=lerp(top0+80,bot0-220,f/6),fy1=lerp(top1+40,bot1-60,f/6);const wa=lerp(xa,xb,0.25),wb=lerp(xa,xb,0.7);const lit=night&&rh(i*10+f,side+5)<0.4;
   P(c,[[wa,fy0],[wb,lerp(fy0,fy1,0.45)],[wb,lerp(fy0,fy1,0.45)+(bot1-bot0)*0+40*(1-z0)+12],[wa,fy0+60*(1-z0)+16]],lit?'#ffd98a':(night?'#232a40':'#9fd0f0'),LN,2);}
  if(i===0){P(c,[[xa,bot0-200],[xb,bot1-90*(1-z1)],[xb,bot1],[xa,bot0]],night?'#2a2230':'#7a4c2e',LN,3);}}};
 fac(-1);fac(1);
 // Gehweg + Straße
 P(c,[[0,H*0.86],[vx-120,vy+40],[vx+120,vy+40],[W,H*0.86],[W,H],[0,H]],night?'#3c4256':'#c9ccd4',null);
 P(c,[[200,H],[vx-40,vy+40],[vx+40,vy+40],[880,H]],night?'#2a2e3e':'#6f7484',null);
 c.strokeStyle=night?'#cfc28a':'#f4e3a1';c.lineWidth=6;c.setLineDash([40,40]);c.lineDashOffset=-t*0;c.beginPath();c.moveTo(540,H);c.lineTo(vx,vy+40);c.stroke();c.setLineDash([]);
 if(night){for(let i=0;i<4;i++){const z=i/4;const lx=lerp(120,vx-90,z),ly=lerp(H*0.86,vy+40,z);c.strokeStyle=LN;c.lineWidth=lerp(10,3,z);c.beginPath();c.moveTo(lx,ly);c.lineTo(lx,ly-lerp(700,140,z));c.stroke();glow(c,lx,ly-lerp(700,140,z),lerp(160,40,z),'255,214,140',0.7);}}}
// Halbe Figuren-Menge (Hinterköpfe/Silhouetten) für Hintergrund
function crowd2(c,t,n,y,cols,s=0.55){for(let i=0;i<n;i++){const x=80+i*(920/(n-1));guy(c,x,y+(i%2)*30,s,t,{shirt:cols[i%cols.length],ph:i,hair:i%3===1?'long':'short',hairCol:['#2e1f16','#8a5a2a','#1a1a1a'][i%3],mouth:'flat',turn:(rh(i,2)-0.5)*0.6});}}
