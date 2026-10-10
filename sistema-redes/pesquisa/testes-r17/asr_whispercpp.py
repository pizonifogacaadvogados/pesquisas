import sys, time, json
from pywhispercpp.model import Model
t0=time.time()
m = Model(sys.argv[1], n_threads=4, language="pt", token_timestamps=True, max_len=1, split_on_word=True, print_progress=False, print_realtime=False)
t1=time.time(); segs = m.transcribe(sys.argv[2]); t2=time.time()
pal=[{"w":s.text.strip(),"ini":s.t0/100,"fim":s.t1/100} for s in segs if s.text.strip()]
print(json.dumps({"carregar_s":round(t1-t0,1),"decodificar_s":round(t2-t1,1),"n":len(pal),"texto":" ".join(p["w"] for p in pal),"palavras":pal},ensure_ascii=False))
