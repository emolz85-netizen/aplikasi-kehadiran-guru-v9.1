(()=>{
  const offline=document.getElementById("mobileOfflineIndicator");
  const updateNetwork=()=>{if(!offline)return;offline.hidden=navigator.onLine;if(navigator.onLine){offline.textContent="✅ Sambungan dipulihkan";offline.classList.add("online");setTimeout(()=>{offline.hidden=true;offline.classList.remove("online");offline.textContent="📡 Anda sedang luar talian"},1800)}else{offline.textContent="📡 Anda sedang luar talian";offline.hidden=false}};
  addEventListener("online",updateNetwork);addEventListener("offline",updateNetwork);if(!navigator.onLine)updateNetwork();
  document.querySelectorAll(".mobile-bottom-nav a").forEach(a=>{try{const u=new URL(a.href,location.href);if(u.pathname===location.pathname)a.classList.add("active")}catch(e){}});
  if("setAppBadge" in navigator){const n=parseInt(document.querySelector(".header-notification span")?.textContent||"0",10);if(n>0)navigator.setAppBadge(n).catch(()=>{});else navigator.clearAppBadge?.().catch(()=>{});}
  let startY=0,pulling=false;const tip=document.createElement("div");tip.className="pull-refresh-tip";tip.textContent="Tarik ke bawah untuk muat semula";document.body.appendChild(tip);
  addEventListener("touchstart",e=>{if(scrollY===0){startY=e.touches[0].clientY;pulling=true}},{passive:true});
  addEventListener("touchmove",e=>{if(!pulling)return;const d=e.touches[0].clientY-startY;if(d>35){tip.classList.add("show");tip.textContent=d>85?"Lepaskan untuk muat semula":"Tarik ke bawah untuk muat semula"}},{passive:true});
  addEventListener("touchend",e=>{if(!pulling)return;pulling=false;const visible=tip.classList.contains("show");if(visible&&tip.textContent.startsWith("Lepaskan")){tip.textContent="Memuat semula…";location.reload()}else tip.classList.remove("show")},{passive:true});
})();