let selfieBlob = null;
let currentPosition = null;

async function getDeviceIdentity(){
  let seed=localStorage.getItem("kehadiran_device_seed");
  if(!seed){seed=(crypto.randomUUID?crypto.randomUUID():String(Date.now())+Math.random());localStorage.setItem("kehadiran_device_seed",seed);}
  const raw=[seed,navigator.userAgent,navigator.platform,screen.width+"x"+screen.height,Intl.DateTimeFormat().resolvedOptions().timeZone].join("|");
  const bytes=await crypto.subtle.digest("SHA-256",new TextEncoder().encode(raw));
  const id=Array.from(new Uint8Array(bytes)).map(b=>b.toString(16).padStart(2,"0")).join("");
  return {id,name:(navigator.platform||"Peranti")+" · "+screen.width+"x"+screen.height,platform:navigator.platform||"",browser:navigator.userAgent.includes("Edg")?"Edge":navigator.userAgent.includes("Chrome")?"Chrome":navigator.userAgent.includes("Safari")?"Safari":"Pelayar"};
}


function haversineClient(lat1, lon1, lat2, lon2){
  const r=6371000,toRad=v=>v*Math.PI/180;
  const p1=toRad(lat1),p2=toRad(lat2),dp=toRad(lat2-lat1),dl=toRad(lon2-lon1);
  const a=Math.sin(dp/2)**2+Math.cos(p1)*Math.cos(p2)*Math.sin(dl/2)**2;
  return r*(2*Math.atan2(Math.sqrt(a),Math.sqrt(1-a)));
}

async function startCamera(){
  if(!window.isSecureContext){alert("Kamera memerlukan HTTPS.");return;}
  try{
    const stream=await navigator.mediaDevices.getUserMedia({video:{facingMode:"user"},audio:false});
    const video=document.getElementById("camera");
    video.srcObject=stream;
    const placeholder=document.getElementById("camera-placeholder");
    if(placeholder) placeholder.hidden=true;
  }catch(e){alert("Kamera gagal dibuka. Benarkan kebenaran kamera.");}
}

function captureSelfie(){
  const v=document.getElementById("camera"),c=document.getElementById("snapshot");
  if(!v||!v.srcObject){alert("Buka kamera dahulu.");return;}
  c.width=v.videoWidth||640;c.height=v.videoHeight||480;
  c.getContext("2d").drawImage(v,0,0,c.width,c.height);
  c.toBlob(b=>{
    selfieBlob=b;
    const badge=document.getElementById("selfie-badge");
    if(badge) badge.hidden=false;
    alert("Swafoto telah diambil.");
  },"image/jpeg",0.85);
}

function refreshGPS(){
  const status=document.getElementById("gps-status");
  const signal=document.getElementById("gps-signal");
  if(!navigator.geolocation){if(status)status.textContent="Peranti tidak menyokong GPS.";return;}
  if(status)status.textContent="Mendapatkan lokasi GPS berketepatan tinggi...";
  if(signal){signal.textContent="Mencari";signal.className="signal-chip waiting";}
  navigator.geolocation.getCurrentPosition(pos=>{
    currentPosition=pos;
    const {latitude,longitude,accuracy}=pos.coords;
    const school=window.schoolLocation||{};
    const distance=haversineClient(latitude,longitude,school.latitude,school.longitude);
    const inside=distance<=school.radius;
    if(status) status.textContent=inside?"Lokasi disahkan dalam kawasan sekolah.":"Lokasi berada di luar radius sekolah.";
    const accuracyEl=document.getElementById("accuracy-value");if(accuracyEl)accuracyEl.textContent=`±${accuracy.toFixed(0)} m`;
    const distanceEl=document.getElementById("distance-value");if(distanceEl)distanceEl.textContent=`${distance.toFixed(1)} m`;
    const radiusEl=document.getElementById("radius-value");if(radiusEl){radiusEl.textContent=inside?"Dalam radius":"Di luar radius";radiusEl.style.color=inside?"#166534":"#991b1b";}
    const coord=document.getElementById("coordinate-value");if(coord)coord.textContent=`${latitude.toFixed(6)}, ${longitude.toFixed(6)}`;
    if(signal){
      signal.textContent=accuracy<=school.maxAccuracy?"Baik":"Lemah";
      signal.className=`signal-chip ${accuracy<=school.maxAccuracy?'good':'weak'}`;
    }
    const pin=document.getElementById("user-pin");
    if(pin){const ratio=Math.min(distance/(school.radius||50),1.5);const angle=Math.atan2(longitude-school.longitude,latitude-school.latitude);const radius=Math.min(66,ratio*48);pin.style.left=`calc(50% + ${Math.sin(angle)*radius}px)`;pin.style.top=`calc(50% - ${Math.cos(angle)*radius}px)`;pin.hidden=false;}
    const link=document.getElementById("map-link");
    if(link){link.href=`https://www.google.com/maps?q=${latitude},${longitude}`;link.hidden=false;}
  },()=>{
    if(status)status.textContent="GPS gagal. Benarkan akses lokasi dan cuba di kawasan terbuka.";
    if(signal){signal.textContent="Gagal";signal.className="signal-chip bad";}
  },{enableHighAccuracy:true,timeout:20000,maximumAge:0});
}

async function rekod(action){
  const status=document.getElementById("gps-status");
  if(!currentPosition){refreshGPS();if(status)status.textContent="Sila tunggu lokasi GPS diperoleh, kemudian tekan semula.";return;}
  if(!selfieBlob){alert("Swafoto baharu wajib diambil sebelum merekod kehadiran.");return;}
  const liveCheck=document.getElementById("liveness-confirmed");
  if(liveCheck && !liveCheck.checked){alert("Sila lakukan dan sahkan cabaran hidup terlebih dahulu.");return;}
  const form=new FormData();
  form.append("latitude",currentPosition.coords.latitude);
  form.append("longitude",currentPosition.coords.longitude);
  form.append("accuracy",currentPosition.coords.accuracy);
  form.append("location_timestamp",currentPosition.timestamp||Date.now());
  const device=await getDeviceIdentity();
  form.append("device_id",device.id);
  form.append("device_name",device.name);
  form.append("device_platform",device.platform);
  form.append("device_browser",device.browser);
  form.append("selfie",selfieBlob,action+"_selfie.jpg");
  const challenge=document.getElementById("liveness-challenge");
  if(challenge) form.append("liveness_challenge",challenge.textContent.trim());
  if(liveCheck && liveCheck.checked) form.append("liveness_confirmed","1");
  if(status)status.textContent="Menghantar rekod...";
  try{
    const res=await fetch(urls[action],{method:"POST",headers:{"X-CSRFToken":csrfToken},body:form});
    const data=await res.json();
    if(status)status.textContent=data.message;
    if(data.ok)setTimeout(()=>location.reload(),900);
  }catch(e){if(status)status.textContent="Sambungan gagal. Cuba semula.";}
}


// V10.0.1: sidebar responsif dan keadaan collapse disimpan.
(()=>{const shell=document.querySelector('.app-shell'),sidebar=document.getElementById('roleSidebar'),toggle=document.getElementById('sidebarToggle');if(!shell||!sidebar||!toggle)return;const desktop=()=>window.matchMedia('(min-width:901px)').matches;const sync=()=>toggle.setAttribute('aria-expanded',desktop()?String(!shell.classList.contains('sidebar-collapsed')):String(sidebar.classList.contains('open')));if(desktop()&&localStorage.getItem('attendance_sidebar_collapsed')==='1')shell.classList.add('sidebar-collapsed');toggle.addEventListener('click',()=>{if(desktop()){shell.classList.toggle('sidebar-collapsed');localStorage.setItem('attendance_sidebar_collapsed',shell.classList.contains('sidebar-collapsed')?'1':'0')}else sidebar.classList.toggle('open');sync()});document.addEventListener('click',e=>{if(!desktop()&&sidebar.classList.contains('open')&&!sidebar.contains(e.target)&&!toggle.contains(e.target)){sidebar.classList.remove('open');sync()}});window.addEventListener('resize',()=>{if(desktop())sidebar.classList.remove('open');sync()});sync()})();


// V10.2 Enterprise UI sebenar
(()=>{
  const html=document.documentElement,body=document.body;
  const themeBtn=document.getElementById('themeToggle'),themeIcon=document.getElementById('themeIcon');
  const profileTheme=document.getElementById('profileThemeToggle');
  const densityBtn=document.getElementById('densityToggle'),profileDensity=document.getElementById('profileDensityToggle');
  const profileButton=document.getElementById('profileMenuButton'),profileMenu=document.getElementById('profileMenu');
  const systemDark=()=>window.matchMedia&&window.matchMedia('(prefers-color-scheme: dark)').matches;
  const savedTheme=localStorage.getItem('attendance_theme')||'system';
  function resolvedTheme(value){return value==='system'?(systemDark()?'dark':'light'):value}
  function applyTheme(value){const resolved=resolvedTheme(value);html.dataset.theme=resolved;localStorage.setItem('attendance_theme',value);if(themeIcon)themeIcon.textContent=resolved==='dark'?'☀️':'🌙';if(themeBtn)themeBtn.title=resolved==='dark'?'Tukar ke mod cerah':'Tukar ke mod gelap';if(profileTheme)profileTheme.innerHTML=resolved==='dark'?'☀️ Mod Cerah':'🌙 Mod Gelap';const meta=document.querySelector('meta[name="theme-color"]');if(meta)meta.content=resolved==='dark'?'#0b1220':(body.classList.contains('role-admin')?'#0f2747':'#166534')}
  applyTheme(savedTheme);
  const toggleTheme=()=>applyTheme(html.dataset.theme==='dark'?'light':'dark');
  themeBtn?.addEventListener('click',toggleTheme);profileTheme?.addEventListener('click',()=>{toggleTheme();closeProfile()});
  window.matchMedia?.('(prefers-color-scheme: dark)').addEventListener?.('change',()=>{if(localStorage.getItem('attendance_theme')==='system')applyTheme('system')});
  function applyDensity(compact){body.classList.toggle('ui-compact',compact);localStorage.setItem('attendance_density',compact?'compact':'comfortable');if(profileDensity)profileDensity.innerHTML=compact?'↕️ Paparan Selesa':'↕️ Paparan Padat'}
  applyDensity(localStorage.getItem('attendance_density')==='compact');
  const toggleDensity=()=>applyDensity(!body.classList.contains('ui-compact'));
  densityBtn?.addEventListener('click',toggleDensity);profileDensity?.addEventListener('click',()=>{toggleDensity();closeProfile()});
  function closeProfile(){if(profileMenu)profileMenu.hidden=true;if(profileButton)profileButton.setAttribute('aria-expanded','false')}
  profileButton?.addEventListener('click',e=>{e.stopPropagation();const open=profileMenu.hidden;profileMenu.hidden=!open;profileButton.setAttribute('aria-expanded',String(open))});
  document.addEventListener('click',e=>{if(profileMenu&&!profileMenu.hidden&&!profileMenu.contains(e.target)&&!profileButton.contains(e.target))closeProfile()});
  document.addEventListener('keydown',e=>{if(e.key==='Escape')closeProfile()});

  // Jadual enterprise: carian segera + pagination 10 rekod.
  document.querySelectorAll('table').forEach((table,index)=>{
    if(table.dataset.enterpriseReady==='1'||table.closest('.no-enterprise-table'))return;
    const tbody=table.tBodies[0];if(!tbody||tbody.rows.length<6)return;
    table.dataset.enterpriseReady='1';
    const parent=table.parentElement;
    const scroll=document.createElement('div');scroll.className='table-scroll';parent.insertBefore(scroll,table);scroll.appendChild(table);
    const toolbar=document.createElement('div');toolbar.className='enterprise-toolbar';
    const wrap=document.createElement('div');wrap.className='enterprise-search-wrap';
    const search=document.createElement('input');search.type='search';search.className='enterprise-search';search.placeholder='Cari dalam jadual…';search.setAttribute('aria-label','Cari dalam jadual');wrap.appendChild(search);toolbar.appendChild(wrap);parent.insertBefore(toolbar,scroll);
    const pager=document.createElement('div');pager.className='enterprise-pagination';const prev=document.createElement('button'),next=document.createElement('button'),info=document.createElement('span');prev.textContent='‹ Sebelum';next.textContent='Seterusnya ›';info.className='enterprise-page-info';pager.append(prev,info,next);parent.insertBefore(pager,scroll.nextSibling);
    const rows=[...tbody.rows];let page=1;const perPage=10;
    function render(){const q=search.value.trim().toLocaleLowerCase('ms');const filtered=rows.filter(r=>r.innerText.toLocaleLowerCase('ms').includes(q));const pages=Math.max(1,Math.ceil(filtered.length/perPage));page=Math.min(page,pages);rows.forEach(r=>r.hidden=true);filtered.slice((page-1)*perPage,page*perPage).forEach(r=>r.hidden=false);info.textContent=`Halaman ${page} / ${pages} · ${filtered.length} rekod`;prev.disabled=page<=1;next.disabled=page>=pages;pager.hidden=filtered.length<=perPage}
    search.addEventListener('input',()=>{page=1;render()});prev.addEventListener('click',()=>{page--;render()});next.addEventListener('click',()=>{page++;render()});render();
  });
  const top=document.createElement('button');top.id='backToTop';top.type='button';top.textContent='↑';top.title='Kembali ke atas';top.setAttribute('aria-label','Kembali ke atas');document.body.appendChild(top);addEventListener('scroll',()=>top.classList.toggle('show',scrollY>450),{passive:true});top.addEventListener('click',()=>scrollTo({top:0,behavior:'smooth'}));
})();
