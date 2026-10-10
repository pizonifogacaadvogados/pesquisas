import sys, time, json, subprocess, numpy as np, sherpa_onnx
d, nome, wav = sys.argv[1], sys.argv[2], sys.argv[3]
t0=time.time()
rec = sherpa_onnx.OfflineRecognizer.from_whisper(encoder=f"{d}/{nome}-encoder.int8.onnx", decoder=f"{d}/{nome}-decoder.int8.onnx",
        tokens=f"{d}/{nome}-tokens.txt", language="pt", task="transcribe", num_threads=4)
t1=time.time()
raw=subprocess.run(["ffmpeg","-v","error","-i",wav,"-ac","1","-ar","16000","-f","f32le","-"],capture_output=True,check=True).stdout
x=np.frombuffer(raw,np.float32); txt=[]
for i in range(0,len(x),16000*28):   # whisper: janelas de 30 s
    s=rec.create_stream(); s.accept_waveform(16000,x[i:i+16000*28]); rec.decode_stream(s); txt.append(s.result.text)
    ts = s.result.timestamps
t2=time.time()
print(json.dumps({"carregar_s":round(t1-t0,1),"decodificar_s":round(t2-t1,1),"tem_timestamps":len(ts)>0,"texto":" ".join(txt)},ensure_ascii=False))
