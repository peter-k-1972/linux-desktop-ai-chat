// ---------- helpers ----------
const $ = (sel, el=document) => el.querySelector(sel);
const $$ = (sel, el=document) => Array.from(el.querySelectorAll(sel));

// ---------- theme ----------
const themeBtn = $("#themeBtn");
const root = document.documentElement;

function setTheme(mode){
  root.dataset.theme = mode;
  localStorage.setItem("theme", mode);
  if(themeBtn){
    const icon = themeBtn.querySelector(".icon");
    if(icon) icon.textContent = mode === "light" ? "☾" : "☼";
  }
}
setTheme(localStorage.getItem("theme") || "dark");
if(themeBtn){
  themeBtn.addEventListener("click", () => {
    setTheme(root.dataset.theme === "light" ? "dark" : "light");
  });
}

// ---------- reveal on scroll ----------
const io = new IntersectionObserver((entries)=>{
  entries.forEach(e => {
    if(e.isIntersecting) e.target.classList.add("in");
  });
},{threshold:0.12});
$$(".reveal").forEach(el=>io.observe(el));

// ---------- tilt effect ----------
function attachTilt(el){
  el.addEventListener("mousemove", (ev)=>{
    const r = el.getBoundingClientRect();
    const x = (ev.clientX - r.left) / r.width;
    const y = (ev.clientY - r.top) / r.height;
    const rx = (0.5 - y) * 10;
    const ry = (x - 0.5) * 12;
    el.style.transform = `rotateX(${rx}deg) rotateY(${ry}deg) translateY(-2px)`;
  });
  el.addEventListener("mouseleave", ()=>{
    el.style.transform = "";
  });
}
$$(".tilt").forEach(attachTilt);

// ---------- quick search / filter ----------
const quickSearch = $("#quickSearch");
const timeline = $("#timeline");
const searchable = [
  ...$$("[data-tags]", timeline || document),
  ...$$(".skills-grid [data-tags]")
];

function tokenSet(str){
  return new Set((str||"").toLowerCase().split(/\s+/).filter(Boolean));
}
const tagMap = new Map();
searchable.forEach(el=>{
  const tags = tokenSet(el.dataset.tags);
  tags.forEach(t => tagMap.set(t, (tagMap.get(t)||0)+1));
});

const quickTags = $("#quickTags");
if(quickTags && tagMap.size > 0){
  [...tagMap.entries()]
    .sort((a,b)=>b[1]-a[1])
    .slice(0, 14)
    .forEach(([t])=>{
      const b = document.createElement("button");
      b.className = "chip";
      b.type = "button";
      b.textContent = t;
      b.addEventListener("click", ()=>{
        if(quickSearch) quickSearch.value = t;
        applyFilter();
        if(quickSearch) quickSearch.focus();
      });
      quickTags.appendChild(b);
    });
}

function applyFilter(){
  if(!quickSearch) return;
  const q = quickSearch.value.trim().toLowerCase();
  if(!q){
    searchable.forEach(el => el.style.display = "");
    return;
  }
  searchable.forEach(el=>{
    const hay = (el.innerText + " " + (el.dataset.tags||"")).toLowerCase();
    el.style.display = hay.includes(q) ? "" : "none";
  });
}
if(quickSearch){
  quickSearch.addEventListener("input", applyFilter);
}

// ---------- particles canvas ----------
const canvas = $("#particles");
if(canvas){
  const ctx = canvas.getContext("2d");
  let W=0,H=0, dots=[];

  function resize(){
    W = canvas.width = window.innerWidth * devicePixelRatio;
    H = canvas.height = window.innerHeight * devicePixelRatio;
    dots = Array.from({length: Math.min(140, Math.floor((window.innerWidth*window.innerHeight)/18000))}, () => ({
      x: Math.random()*W,
      y: Math.random()*H,
      vx: (Math.random()-.5)*0.45*devicePixelRatio,
      vy: (Math.random()-.5)*0.45*devicePixelRatio,
      r: (Math.random()*1.8+0.6)*devicePixelRatio
    }));
  }
  window.addEventListener("resize", resize);
  resize();

  function tick(){
    ctx.clearRect(0,0,W,H);

    // subtle color shift by theme
    const light = root.dataset.theme === "light";

    for(const d of dots){
      d.x += d.vx; d.y += d.vy;
      if(d.x<0||d.x>W) d.vx*=-1;
      if(d.y<0||d.y>H) d.vy*=-1;

      ctx.beginPath();
      ctx.arc(d.x,d.y,d.r,0,Math.PI*2);
      ctx.fillStyle = light ? "rgba(20,24,40,.25)" : "rgba(233,233,255,.20)";
      ctx.fill();
    }

    // links
    for(let i=0;i<dots.length;i++){
      for(let j=i+1;j<dots.length;j++){
        const a=dots[i], b=dots[j];
        const dx=a.x-b.x, dy=a.y-b.y;
        const dist = Math.hypot(dx,dy);
        const max = 130*devicePixelRatio;
        if(dist<max){
          const alpha = (1 - dist/max) * (light ? .12 : .18);
          ctx.strokeStyle = `rgba(124,58,237,${alpha})`;
          ctx.lineWidth = 1*devicePixelRatio;
          ctx.beginPath();
          ctx.moveTo(a.x,a.y); ctx.lineTo(b.x,b.y);
          ctx.stroke();
        }
      }
    }

    requestAnimationFrame(tick);
  }
  tick();
}

// ---------- modal ----------
const modal = $("#modal");
const modalTitle = $("#modalTitle");
const modalBody = $("#modalBody");
const modalClose = $("#modalClose");

if(modalClose){
  modalClose.addEventListener("click", ()=> {
    if(modal) modal.close();
  });
}

function openModal(title, html){
  if(modalTitle) modalTitle.textContent = title;
  if(modalBody) modalBody.innerHTML = html;
  if(modal) modal.showModal();
}
window.openModal = openModal;

function closeModal(){
  if(modal) modal.close();
}
window.closeModal = closeModal;

// ---------- login overlay ----------
function openLoginModal(){
  const tpl = document.querySelector("#loginModalTpl");
  if(!tpl){
    // Fallback: wenn Template fehlt, normale Login-Seite verwenden
    window.location.href = "/members/login/";
    return;
  }
  openModal("Anmelden", tpl.innerHTML);
  // Focus username field (nachdem Modal DOM aktualisiert wurde)
  setTimeout(()=>{
    const u = document.querySelector("#modal_login_username");
    if(u) u.focus();
  }, 0);
}
window.openLoginModal = openLoginModal;

$$("[data-open-login]").forEach(el=>{
  el.addEventListener("click", (ev)=>{
    // JS only enhancement; ohne JS geht's via href zur Login-Seite
    ev.preventDefault();
    openLoginModal();
  });
});

// ---------- year ----------
const yearEl = $("#year");
if(yearEl) yearEl.textContent = new Date().getFullYear();
