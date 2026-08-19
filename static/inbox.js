document.addEventListener('DOMContentLoaded', function(){
  const link = document.querySelector('.fake-link');
  const preview = document.querySelector('.link-preview');
  if (link && preview){
    link.addEventListener('mouseenter', function(){ preview.classList.add('show'); });
    link.addEventListener('mouseleave', function(){ preview.classList.remove('show'); });
    link.addEventListener('click', function(e){
      e.preventDefault(); preview.classList.add('show');
      if (window.UI){
        var content = document.createElement('div');
        var url = link.getAttribute('data-url');
        var origin = (function(){ try { var u = new URL(url); return u.origin; } catch(e){ return url; } })();
        content.innerHTML = '<h3 style="margin-top:0">Safe Preview</h3>'+
          '<p>This is the destination the link claims to open:</p>'+
          '<div style="font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; word-break: break-all; background:#0f1430; border:1px solid #2a3154; border-radius:8px; padding:8px;">'+url+'</div>'+
          '<p><strong>Origin:</strong> '+origin+'</p>'+
          '<p>Only proceed if this domain is expected and trusted.</p>';
        UI.openModal(content);
      }
    });
  }
});


