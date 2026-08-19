// Minimal frontend interactions: simple auth, dashboard rendering, navigation
(function(){
  function $(sel, root=document) { return root.querySelector(sel); }
  function $all(sel, root=document){ return Array.from(root.querySelectorAll(sel)); }

  window.cyber = {
    login(evt){
      evt && evt.preventDefault();
      const u = $('#username')?.value?.trim();
      if(!u) return alert('Enter username');
      const user = (window.MOCK.users.find(x=>x.username===u) || {id:'guest',username:u,displayName:u,badges:[],progress:{}});
      localStorage.setItem('cyber_user', JSON.stringify(user));
      window.location.href = '/cyber_dashboard';
    },
    signup(evt){
      evt && evt.preventDefault();
      const u = $('#username')?.value?.trim();
      if(!u) return alert('Enter username');
      const newUser = {id:'u_'+Date.now(), username:u, displayName:u, badges:['starter'], progress:{}};
      window.MOCK.users.push(newUser);
      localStorage.setItem('cyber_user', JSON.stringify(newUser));
      window.location.href = '/cyber_dashboard';
    },
    getCurrentUser(){
      try{return JSON.parse(localStorage.getItem('cyber_user')||'null');}catch(e){return null}
    },
    renderDashboard(){
      const user = this.getCurrentUser();
      if(!user){document.body.querySelector('.not-auth')?.classList.remove('hidden');}
      const list = document.getElementById('games-list');
      if(!list) return;
      list.innerHTML = '';
      window.MOCK.games.forEach(g=>{
        const progress = (user && user.progress && user.progress[g.id])? user.progress[g.id] : 0;
        const tile = document.createElement('div'); tile.className='game-tile card';
        tile.innerHTML = `<h3>${g.title}</h3><p class="small">${g.desc}</p><div class="progress"><i style="width:${progress}%"></i></div><div style="display:flex;justify-content:space-between;align-items:center;margin-top:12px"><span class="small">Progress: ${progress}%</span><a class="button" href="/cyber_game/${g.id}">Play</a></div>`;
        list.appendChild(tile);
      });
    }
  };

  // Auto-run dashboard render if element exists
  document.addEventListener('DOMContentLoaded', ()=>{
    if(document.getElementById('games-list')) window.cyber.renderDashboard();
    const loginForm = document.getElementById('login-form'); if(loginForm) loginForm.addEventListener('submit', window.cyber.login.bind(window.cyber));
    const signupForm = document.getElementById('signup-form'); if(signupForm) signupForm.addEventListener('submit', window.cyber.signup.bind(window.cyber));
  });
})();
