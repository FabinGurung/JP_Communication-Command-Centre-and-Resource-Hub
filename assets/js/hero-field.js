/* JP AEC light construction-field hero: progressive Canvas 2D, no external WebGL dependency. */
(()=>{"use strict";const c=document.getElementById("field-hero-canvas");if(!c)return;const ctx=c.getContext("2d");if(!ctx)return;
let width=0,height=0,dpr=1,pointer=0,active=true,frame=0;const reduce=window.matchMedia("(prefers-reduced-motion: reduce)");const colors={green:"#589878",dark:"#24674d",mint:"#b3d6b7",cloud:"#ffffff",gold:"#ddb95b"};
function resize(){const r=c.getBoundingClientRect();width=Math.max(1,r.width);height=Math.max(1,r.height);dpr=Math.min(window.devicePixelRatio||1,1.6);c.width=Math.round(width*dpr);c.height=Math.round(height*dpr);ctx.setTransform(dpr,0,0,dpr,0,0);draw(0);}
function stroke(x1,y1,x2,y2,color=colors.green,sw=1.5){ctx.strokeStyle=color;ctx.lineWidth=sw;ctx.beginPath();ctx.moveTo(x1,y1);ctx.lineTo(x2,y2);ctx.stroke();}
function cloud(x,y,s=1){ctx.fillStyle="rgba(255,255,255,.83)";ctx.beginPath();ctx.ellipse(x,y,23*s,10*s,0,0,Math.PI*2);ctx.ellipse(x+15*s,y-6*s,17*s,12*s,0,0,Math.PI*2);ctx.ellipse(x+32*s,y,21*s,10*s,0,0,Math.PI*2);ctx.fill();}
function draw(t){if(!width||!height)return;ctx.clearRect(0,0,width,height);const p=reduce.matches?0:Math.sin(t*.00035)+(pointer-.5)*.6,float=reduce.matches?0:Math.sin(t*.0007)*2;const floor=height*.81,span=width*.19,base=width*.48;const sky=ctx.createLinearGradient(0,0,0,height);sky.addColorStop(0,"#e1f1e2");sky.addColorStop(.7,"#f6f6e6");sky.addColorStop(1,"#d7e8d4");ctx.fillStyle=sky;ctx.fillRect(0,0,width,height);
cloud(width*.13+p*19,42,1.05);cloud(width*.63-p*13,height*.18,.9);cloud(width*.81+p*17,height*.39,.65);
ctx.fillStyle="#d0e5cd";ctx.beginPath();ctx.moveTo(0,floor);ctx.bezierCurveTo(width*.22,height*.63,width*.32,height*.9,width*.53,height*.69);ctx.bezierCurveTo(width*.73,height*.52,width*.79,height*.83,width,floor*.91);ctx.lineTo(width,height);ctx.lineTo(0,height);ctx.fill();
ctx.fillStyle="#b2d1b2";ctx.beginPath();ctx.moveTo(0,height*.9);ctx.bezierCurveTo(width*.22,height*.75,width*.47,height*1.01,width*.67,height*.79);ctx.bezierCurveTo(width*.85,height*.73,width*.95,height*.88,width,height*.8);ctx.lineTo(width,height);ctx.lineTo(0,height);ctx.fill();
const sx=base-span/2, ex=base+span/2,top=floor-height*.53;ctx.fillStyle="rgba(255,255,255,.54)";ctx.fillRect(sx,top,span,floor-top);
ctx.strokeStyle=colors.green;ctx.lineWidth=2;ctx.strokeRect(sx,top,span,floor-top);
for(let i=1;i<4;i++){const y=top+(floor-top)*i/4;stroke(sx,y,ex,y,colors.dark,1.7);}for(let j=1;j<3;j++){let x=sx+span*j/3;stroke(x,top,x,floor,colors.dark,1.5);}
const wx=span*.17;for(let y=top+13;y<floor-16;y+=(floor-top)/4)for(let x=sx+14;x<ex-12;x+=span/3){ctx.fillStyle="rgba(108,159,124,.26)";ctx.fillRect(x,y,wx,(floor-top)/7);}
const mastX=sx-span*.42,mastTop=top-height*.08;stroke(mastX,mastTop,mastX,floor,colors.dark,3);stroke(mastX,mastTop,ex+span*.72,mastTop,colors.gold,3);stroke(mastX-span*.08,mastTop+height*.06,ex+span*.60,mastTop+height*.06,"#e3c77b",1);
for(let i=0;i<9;i++){let x=mastX+i*((ex+span*.72-mastX)/9);stroke(x,mastTop,x+(ex+span*.72-mastX)/18,mastTop+height*.06,"#b08d4b",1);}
let hookX=ex+span*.32+p*span*.06;stroke(hookX,mastTop,hookX,top+height*.22+float,colors.dark,1.3);ctx.fillStyle=colors.gold;ctx.fillRect(hookX-10,top+height*.21+float,20,7);
stroke(0,floor+6,width,floor+6,colors.dark,1.2);ctx.fillStyle=colors.dark;ctx.font="700 11px system-ui";ctx.fillText("SITE • PLAN • BUILD • VERIFY",16,height-17);
}
function tick(t){if(!active)return;frame=requestAnimationFrame(tick);if(!reduce.matches)draw(t);}
c.addEventListener("pointermove",e=>{pointer=e.offsetX/Math.max(width,1);if(reduce.matches)draw(0);},{passive:true});document.addEventListener("visibilitychange",()=>{active=!document.hidden;if(active){resize();if(!reduce.matches)tick(performance.now());}else cancelAnimationFrame(frame);});
window.addEventListener("resize",resize,{passive:true});reduce.addEventListener?.("change",()=>{cancelAnimationFrame(frame);resize();if(!reduce.matches&&active)tick(performance.now());});resize();if(!reduce.matches)tick(0);
})();