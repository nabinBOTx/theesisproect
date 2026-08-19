(function(){
  function rand(a,b){return Math.random()*(b-a)+a}
  function create(){
    var c = document.createElement('canvas');
    c.className = 'bg-canvas';
    c.style.position = 'fixed';
    c.style.left = 0; c.style.top = 0; c.style.width = '100%'; c.style.height = '100%';
    c.style.zIndex = '-1'; c.style.pointerEvents = 'none';
    document.body.appendChild(c);
    function resize(){ c.width = innerWidth; c.height = innerHeight; }
    resize(); addEventListener('resize', resize);
    return c;
  }
  function init(){
    var c = create(); var ctx = c.getContext('2d');
    var dots = []; var N = Math.min(120, Math.floor((innerWidth*innerHeight)/15000));
    for (var i=0;i<N;i++) dots.push({x: rand(0,c.width), y: rand(0,c.height), vx: rand(-0.2,0.2), vy: rand(-0.2,0.2), r: rand(0.6,1.8)});
    function frame(){
      ctx.clearRect(0,0,c.width,c.height);
      for (var i=0;i<dots.length;i++){
        var d = dots[i];
        d.x += d.vx; d.y += d.vy;
        if (d.x<0||d.x>c.width) d.vx*=-1;
        if (d.y<0||d.y>c.height) d.vy*=-1;
      }
      // draw links
      for (var i=0;i<dots.length;i++){
        for (var j=i+1;j<dots.length;j++){
          var a=dots[i], b=dots[j];
          var dx=a.x-b.x, dy=a.y-b.y; var dist=dx*dx+dy*dy; // squared
          if (dist < 120*120){
            var op = Math.max(0, 0.12 - dist/(120*120)*0.12);
            ctx.strokeStyle = 'rgba(124, 169, 255,'+op+')';
            ctx.lineWidth = 1; ctx.beginPath(); ctx.moveTo(a.x,a.y); ctx.lineTo(b.x,b.y); ctx.stroke();
          }
        }
      }
      // draw dots
      for (var k=0;k<dots.length;k++){
        var p = dots[k]; ctx.fillStyle = 'rgba(124, 200, 255, 0.7)';
        ctx.beginPath(); ctx.arc(p.x,p.y,p.r,0,Math.PI*2); ctx.fill();
      }
      requestAnimationFrame(frame);
    }
    requestAnimationFrame(frame);
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
})();


