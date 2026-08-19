(function(){
  var key = 'csq-theme';
  function apply(theme){
    document.documentElement.setAttribute('data-theme', theme);
    try { localStorage.setItem(key, theme); } catch(e){}
  }
  function current(){ return document.documentElement.getAttribute('data-theme') || 'dark'; }
  function toggle(){ apply(current()==='dark' ? 'light' : 'dark'); }
  // init from storage or prefers
  try {
    var saved = localStorage.getItem(key);
    if (saved) { apply(saved); }
    else if (window.matchMedia && window.matchMedia('(prefers-color-scheme: light)').matches) {
      apply('light');
    } else { apply('dark'); }
  } catch(e){ apply('dark'); }
  window.__csqToggleTheme = toggle;
})();


