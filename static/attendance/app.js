let selfieBlob = null;
let currentPosition = null;

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
  const form=new FormData();
  form.append("latitude",currentPosition.coords.latitude);
  form.append("longitude",currentPosition.coords.longitude);
  form.append("accuracy",currentPosition.coords.accuracy);
  if(selfieBlob) form.append("selfie",selfieBlob,action+"_selfie.jpg");
  if(status)status.textContent="Menghantar rekod...";
  try{
    const res=await fetch(urls[action],{method:"POST",headers:{"X-CSRFToken":csrfToken},body:form});
    const data=await res.json();
    if(status)status.textContent=data.message;
    if(data.ok)setTimeout(()=>location.reload(),900);
  }catch(e){if(status)status.textContent="Sambungan gagal. Cuba semula.";}
}
