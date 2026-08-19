(function(){
  function rand(min, max){ return Math.random()*(max-min)+min; }
  function createCanvas(){
    var c = document.createElement('canvas');
    c.style.position = 'fixed';
    c.style.left = 0; c.style.top = 0; c.style.pointerEvents = 'none';
    c.width = window.innerWidth; c.height = window.innerHeight;
    document.body.appendChild(c);
    window.addEventListener('resize', function(){ c.width = window.innerWidth; c.height = window.innerHeight; });
    return c;
  }
  window.launchConfetti = function(){
    var c = createCanvas();
    var ctx = c.getContext('2d');
    var pieces = [];
    var colors = ['#49a9f2','#7bd3ff','#27c093','#ef6a6a','#f7c948'];
    for (var i=0;i<150;i++){
      pieces.push({
        x: rand(0, c.width), y: rand(-40, -10), r: rand(4, 9),
        vx: rand(-1, 1), vy: rand(2, 4),
        color: colors[(Math.random()*colors.length)|0],
        rot: rand(0, 2*Math.PI), vr: rand(-0.1, 0.1)
      });
    }
    var start = performance.now();
    function frame(now){
      var t = now - start;
      ctx.clearRect(0,0,c.width,c.height);
      pieces.forEach(function(p){
        p.x += p.vx; p.y += p.vy; p.rot += p.vr; p.vy += 0.03;
        ctx.save();
        ctx.translate(p.x, p.y);
        ctx.rotate(p.rot);
        ctx.fillStyle = p.color;
        ctx.fillRect(-p.r, -p.r/2, p.r*2, p.r);
        ctx.restore();
      });
      pieces = pieces.filter(function(p){ return p.y < c.height + 20; });
      if (t < 5000 && pieces.length) requestAnimationFrame(frame); else document.body.removeChild(c);
    }
    requestAnimationFrame(frame);
  }
})();


