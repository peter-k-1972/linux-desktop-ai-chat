// Variant-only goodies (Konami, fun modal, business CTA tracking demo)
const root = document.documentElement;

function setVariant(v){
  root.dataset.variant = v;
  localStorage.setItem("variant", v);
}

(function initVariant(){
  const v = root.dataset.variant || localStorage.getItem("variant");
  if(v) root.dataset.variant = v;
})();

// Konami Easter Egg (Fun variant only)
const KONAMI = ["ArrowUp","ArrowUp","ArrowDown","ArrowDown","ArrowLeft","ArrowRight","ArrowLeft","ArrowRight","b","a"];
let kbuf = [];
window.addEventListener("keydown",(e)=>{
  if(root.dataset.variant !== "fun") return;
  kbuf.push(e.key);
  kbuf = kbuf.slice(-KONAMI.length);
  const ok = KONAMI.every((k,i)=>k.toLowerCase() === (kbuf[i]||"").toLowerCase());
  if(ok){
    const modal = document.querySelector("#modal");
    const modalTitle = document.querySelector("#modalTitle");
    const modalBody = document.querySelector("#modalBody");
    if(modal && modalTitle && modalBody){
      modalTitle.textContent = "Easter Egg unlocked 🕹️";
      modalBody.innerHTML = `
        Du hast den Konami-Code gefunden.<br><br>
        <code>Hint:</code> Wenn du willst, baue ich dir hier ein Mini-Game oder Musik-Visualizer rein.
      `;
      modal.showModal();
    }
    kbuf = [];
  }
});

// Business: demo click telemetry (local only)
window.addEventListener("click",(e)=>{
  if(root.dataset.variant !== "business") return;
  const el = e.target.closest("[data-track]");
  if(!el) return;
  const log = JSON.parse(localStorage.getItem("biz_clicks") || "[]");
  log.unshift({ at:new Date().toISOString(), track: el.dataset.track });
  localStorage.setItem("biz_clicks", JSON.stringify(log));
});

