import sys, time, json, subprocess, numpy as np, sherpa_onnx
d, wav = sys.argv[1], sys.argv[2]
t0=time.time()
rec = sherpa_onnx.OfflineRecognizer.from_transducer(encoder=f"{d}/encoder.int8.onnx", decoder=f"{d}/decoder.int8.onnx",
        joiner=f"{d}/joiner.int8.onnx", tokens=f"{d}/tokens.txt", model_type="nemo_transducer", num_threads=4)
t1=time.time()
raw=subprocess.run(["ffmpeg","-v","error","-i",wav,"-ac","1","-ar","16000","-f","f32le","-"],capture_output=True,check=True).stdout
x=np.frombuffer(raw,np.float32)
# blocos de ~25 s cortados em silêncio seria o ideal; aqui: arquivo inteiro
s=rec.create_stream(); s.accept_waveform(16000,x); rec.decode_stream(s); r=s.result
t2=time.time()
# tokens BPE com '▁' -> palavras
pal=[]; 
for tok,ts in zip(r.tokens, r.timestamps):
    if tok.startswith("▁") or tok.startswith(" ") or not pal: pal.append({"w":tok.lstrip("▁ "),"ini":round(ts,2)})
    else: pal[-1]["w"]+=tok
for i,p in enumerate(pal): p["fim"]= pal[i+1]["ini"] if i+1<len(pal) else round(len(x)/16000,2)
print(json.dumps({"carregar_s":round(t1-t0,1),"decodificar_s":round(t2-t1,1),"audio_s":round(len(x)/16000,1),"texto":r.text,"palavras":pal},ensure_ascii=False))
