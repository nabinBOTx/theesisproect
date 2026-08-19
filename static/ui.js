window.UI = (function(){
  function qs(s,root){ return (root||document).querySelector(s); }
  function ce(tag, cls){ var el = document.createElement(tag); if (cls) el.className = cls; return el; }
  function openModal(contentNode){
    var overlay = ce('div','modal-overlay');
    var modal = ce('div','modal');
    var close = ce('button','modal-close'); close.type = 'button'; close.textContent = '✕';
    close.addEventListener('click', function(){ document.body.removeChild(overlay); });
    overlay.addEventListener('click', function(e){ if (e.target===overlay) document.body.removeChild(overlay); });
    modal.appendChild(close);
    modal.appendChild(contentNode);
    overlay.appendChild(modal);
    document.body.appendChild(overlay);
  }
  function tooltip(el, text){
    el.setAttribute('data-tooltip', text);
    el.addEventListener('mouseenter', function(){ el.classList.add('has-tooltip'); });
    el.addEventListener('mouseleave', function(){ el.classList.remove('has-tooltip'); });
  }
  return { openModal: openModal, tooltip: tooltip, qs: qs };
})();

(function(){
  var modal, modalContent, toastContainer;
  function ensure(){
    if (!modal){
      modal = document.createElement('div');
      modal.className = 'modal-overlay hidden';
      modal.innerHTML = '<div class="modal"><button class="modal-close" aria-label="Close">✕</button><div class="modal-content"></div></div>';
      document.body.appendChild(modal);
      modalContent = modal.querySelector('.modal-content');
      modal.querySelector('.modal-close').addEventListener('click', closeModal);
      modal.addEventListener('click', function(e){ if (e.target === modal) closeModal(); });
    }
    if (!toastContainer){
      toastContainer = document.createElement('div');
      toastContainer.className = 'toast-container';
      document.body.appendChild(toastContainer);
    }
  }
  function openModal(html){ ensure(); modalContent.innerHTML = html; modal.classList.remove('hidden'); }
  function closeModal(){ if (modal){ modal.classList.add('hidden'); modalContent.innerHTML = ''; } }
  function toast(msg){ ensure(); var t = document.createElement('div'); t.className='toast'; t.textContent=msg; toastContainer.appendChild(t); requestAnimationFrame(function(){ t.classList.add('show'); }); setTimeout(function(){ t.classList.remove('show'); setTimeout(function(){ t.remove(); }, 200); }, 2500); }
  window.UI = { openModal: openModal, closeModal: closeModal, toast: toast };
})();


