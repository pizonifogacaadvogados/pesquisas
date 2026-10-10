import json, re, sys, unicodedata
REF = ("Você sabia que pode cancelar uma compra feita pela internet? O artigo 49 do Código de Defesa do Consumidor garante o direito de arrependimento. "
 "O prazo é de sete dias, contados do recebimento do produto. E atenção, a loja não pode cobrar multa por isso. Muita gente acha que precisa explicar o motivo, mas isso é mito. "
 "Você não precisa justificar nada. E o pior: tem loja que se recusa a devolver o dinheiro. Isso é ilegal, e você pode reclamar no Procon. Salve esse vídeo e compartilhe com quem precisa saber disso.")
FILL = {"bom","é","éé","hã","ah","eh","hum","uh","tipo","né"}
def norm(t):
    t = t.lower().replace(" 7 "," sete ").replace("quarenta e nove","49")
    t = re.sub(r"[^\w\s]"," ",t); return [w for w in t.split()]
def wer(r,h):
    d=list(range(len(h)+1))
    for i,rw in enumerate(r,1):
        nd=[i]
        for j,hw in enumerate(h,1): nd.append(min(d[j]+1,nd[j-1]+1,d[j-1]+(rw!=hw)))
        d=nd
    return d[-1]/len(r)
r=norm(REF)
onsets=[float(x) for x in open(sys.argv[1]).read().split()]
for f in sys.argv[2:]:
    j=json.loads(open(f).read()); h=norm(j["texto"])
    # remove o preâmbulo "bom é hoje eu vou falar sobre um assunto" (não está no REF) e fillers
    hh=[w for w in h if w not in FILL]
    k=next((i for i in range(len(hh)) if hh[i]=="você"),0); hh=hh[k:]
    out={"arq":f,"WER_%":round(100*wer(r,hh),1),"decod_s":j["decodificar_s"],"fillers":[w for w in h if w in FILL]}
    if "palavras" in j:
        st=[p["ini"] for p in j["palavras"]]
        errs=[min(abs(o-s) for s in st) for o in onsets if o>0.1]
        out["erro_inicio_frase_ms_medio"]=round(1000*sum(errs)/len(errs)); out["erro_max_ms"]=round(1000*max(errs))
    print(json.dumps(out,ensure_ascii=False))
