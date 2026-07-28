let selfieBlob = null;
let currentPosition = null;

async function startCamera(){
  if(!window.isSecureContext){alert("Kamera memerlukan HTTPS.");return;}
  try{
    const stream=await navigator.mediaDevices.getUserMedia({video:{facingMode:"user"},audio:false});
    document.getElementById("camera").srcObject=stream;
  }catch(e){alert("Kamera gagal dibuka. Benarkan kebenaran kamera.");}
}

function captureSelfie(){
  const v=document.getElementById("camera"),c=document.getElementById("snapshot");
  if(!v.srcObject){alert("Buka kamera dahulu.");return;}
  c.width=v.videoWidth||640;c.height=v.videoHeight||480;
  c.getContext("2d").drawImage(v,0,0,c.width,c.height);
  c.toBlob(b=>{selfieBlob=b;alert("Swafoto telah diambil.");},"image/jpeg",0.85);
}

function refreshGPS(){
  const status=document.getElementById("gps-status");
  if(!navigator.geolocation){status.textContent="Peranti tidak menyokong GPS.";return;}
  status.textContent="Mendapatkan lokasi GPS berketepatan tinggi...";
  navigator.geolocation.getCurrentPosition(pos=>{
    currentPosition=pos;
    const {latitude,longitude,accuracy}=pos.coords;
    status.textContent=`Lokasi: ${latitude.toFixed(6)}, ${longitude.toFixed(6)} · Ketepatan ±${accuracy.toFixed(0)} m`;
    const link=document.getElementById("map-link");
    if(link){link.href=`https://www.google.com/maps?q=${latitude},${longitude}`;link.hidden=false;}
  },()=>{status.textContent="GPS gagal. Benarkan akses lokasi dan cuba di kawasan terbuka.";},{enableHighAccuracy:true,timeout:20000,maximumAge:0});
}

async function rekod(action){
  const status=document.getElementById("gps-status");
  if(!currentPosition){refreshGPS();status.textContent="Sila tunggu lokasi GPS diperoleh, kemudian tekan semula.";return;}
  const form=new FormData();
  form.append("latitude",currentPosition.coords.latitude);
  form.append("longitude",currentPosition.coords.longitude);
  form.append("accuracy",currentPosition.coords.accuracy);
  if(selfieBlob) form.append("selfie",selfieBlob,action+"_selfie.jpg");
  status.textContent="Menghantar rekod...";
  try{
    const res=await fetch(urls[action],{method:"POST",headers:{"X-CSRFToken":csrfToken},body:form});
    const data=await res.json();
    status.textContent=data.message;
    if(data.ok)setTimeout(()=>location.reload(),900);
  }catch(e){status.textContent="Sambungan gagal. Cuba semula.";}
}
