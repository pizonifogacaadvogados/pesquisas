import sys, numpy as np, subprocess, json
def load(p):
    raw = subprocess.run(["ffmpeg","-v","error","-i",p,"-ac","1","-ar","48000","-f","f32le","-"],capture_output=True,check=True).stdout
    return np.frombuffer(raw,np.float32).astype(np.float64)
ref = load(sys.argv[1]); N=len(ref)
def atraso(x):
    n=1<<int(np.ceil(np.log2(2*N))); seg=slice(0,48000*20)
    c=np.fft.irfft(np.fft.rfft(x[seg],n)*np.conj(np.fft.rfft(ref[seg],n)),n)
    L=4800; cand=np.r_[c[:L],c[-L:]]; i=int(np.argmax(cand)); return i if i<L else i-2*L
w=960; nfr=N//w; R=ref[:nfr*w].reshape(nfr,w); sil=np.sqrt((R**2).mean(1))<1e-4; fala=~sil
rms=lambda M: 20*np.log10(np.sqrt((M**2).mean())+1e-12)
for p in sys.argv[2:]:
    x=load(p); d=atraso(x); x=x[d:] if d>=0 else np.r_[np.zeros(-d),x]
    x=np.pad(x,(0,max(0,N-len(x))))[:N]
    alpha=np.dot(x,ref)/np.dot(ref,ref); e=x-alpha*ref
    s=10*np.log10(np.sum((alpha*ref)**2)/max(np.sum(e**2),1e-20))
    X=x[:nfr*w].reshape(nfr,w)
    print(json.dumps({"arq":p.split('/')[-1],"SI-SDR_dB":round(s,2),"atraso_ms":round(d/48,2),"ruido_pausas_dBFS":round(rms(X[sil]),1),"fala_dBFS":round(rms(X[fala]),1),"SNR_pausa_dB":round(rms(X[fala])-rms(X[sil]),1)}))
