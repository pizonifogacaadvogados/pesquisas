"""Cadeia de voz: [deep-filter] -> EQ/deesser/compressor -> loudnorm 2 passadas. uso: cadeia_voz.py entrada saida [deepfilter_bin|-]"""
import json, subprocess, sys, tempfile, time, os, shutil
ent, sai = sys.argv[1], sys.argv[2]; dfbin = sys.argv[3] if len(sys.argv) > 3 else "-"
t0 = time.time(); tmp = tempfile.mkdtemp()
w48 = os.path.join(tmp, "v.wav")
subprocess.run(["ffmpeg","-v","error","-y","-i",ent,"-vn","-ac","1","-ar","48000",w48],check=True)
if dfbin != "-":
    subprocess.run([dfbin,"-D","-a","30","-o",os.path.join(tmp,"df"),w48],check=True,capture_output=True)
    w48 = os.path.join(tmp,"df","v.wav")
t1 = time.time()
CADEIA = ("highpass=f=80:p=2,"
          "equalizer=f=250:t=q:w=1.2:g=-2,"        # tira 'embolado'
          "equalizer=f=3200:t=q:w=1.0:g=2.5,"      # presença/inteligibilidade
          "deesser=i=0.5:m=0.5:f=0.5,"             # i default=0 (não faz nada!)
          "acompressor=threshold=-21dB:ratio=3:attack=8:release=120:makeup=3dB:knee=4")
ALVO = "I=-14:TP=-1.5:LRA=9"
r = subprocess.run(["ffmpeg","-hide_banner","-nostats","-i",w48,"-af",f"{CADEIA},loudnorm={ALVO}:print_format=json","-f","null","-"],capture_output=True,text=True)
m = json.loads(r.stderr[r.stderr.rindex("{"):])
# 2a passada: ganho linear exato até -14 LUFS + limitador com sobreamostragem 4x (pico verdadeiro ~ -1,5 dBTP)
ganho = -14.0 - float(m["input_i"])
seg = (f"{CADEIA},volume={ganho:.2f}dB,aresample=192000,alimiter=limit=-2dB:attack=3:release=60:level=false,aresample=48000")
def medir(arq):
    o = subprocess.run(["ffmpeg","-hide_banner","-nostats","-i",arq,"-af","ebur128","-f","null","-"],capture_output=True,text=True).stderr
    return float(o.rsplit("I:",1)[1].split("LUFS")[0])
for _ in range(3):  # o limitador come ~1 dB: corrige o ganho e refaz (cada volta ~0,5 s/min)
    subprocess.run(["ffmpeg","-v","error","-y","-i",w48,"-af",seg,"-c:a","pcm_s16le",sai],check=True)
    i_out = medir(sai)
    if abs(i_out + 14.0) <= 0.3: break
    ganho += -14.0 - i_out
    seg = (f"{CADEIA},volume={ganho:.2f}dB,aresample=192000,alimiter=limit=-2dB:attack=3:release=60:level=false,aresample=48000")
t2 = time.time(); shutil.rmtree(tmp)
print(json.dumps({"denoise_s":round(t1-t0,2),"cadeia_s":round(t2-t1,2),"passo1":{k:m[k] for k in ("input_i","input_tp","input_lra","normalization_type")}}))
