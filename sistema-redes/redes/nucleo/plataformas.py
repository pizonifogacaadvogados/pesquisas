"""Especificações por rede e formato (registro R12, síntese de 09/10/2026; valores conservadores).

Cada DESTINO é uma combinação rede+formato que o sistema sabe entregar. Os braços usam isto para
renderizar no tamanho certo, respeitar zonas seguras, cortar duração, e o gestor para validar legenda,
hashtags e arquivo antes de publicar.

Zonas seguras em px no quadro do destino: (topo, baixo, direita, esquerda) — área coberta pela interface.
"""
import json
import subprocess
from pathlib import Path

# zona segura universal 9:16 (vale para IG, FB, TikTok, Shorts, Kwai ao mesmo tempo) — R12 síntese
SEGURA_UNIVERSAL_916 = (380, 670, 150, 65)

V = "video"
I = "imagem"
D = "documento"

DESTINOS = {
    # ------------------------------------------------------------------ vídeo vertical
    "instagram_reels": dict(rede="instagram", tipo=V, w=1080, h=1920, dur=(3, 180, (15, 90)), legenda=2200,
                            visivel=125, hashtags=5, segura=(270, 670, 140, 65), max_mb=4000,
                            obs="alcance para não seguidores só até 3 min; impulsionar exige ≤ 90 s"),
    "instagram_stories": dict(rede="instagram", tipo=V, w=1080, h=1920, dur=(1, 60, (5, 15)), legenda=0, hashtags=0,
                              segura=(270, 380, 65, 65), max_mb=4000),
    "facebook_reels": dict(rede="facebook", tipo=V, w=1080, h=1920, dur=(3, 180, (15, 90)), legenda=2200, visivel=125,
                           hashtags=5, segura=(270, 670, 140, 65), max_mb=1000),
    "tiktok_video": dict(rede="tiktok", tipo=V, w=1080, h=1920, dur=(3, 600, (15, 60)), legenda=2200, visivel=100,
                         hashtags=5, segura=(150, 400, 150, 60), max_mb=287),
    "youtube_shorts": dict(rede="youtube", tipo=V, w=1080, h=1920, dur=(1, 180, (20, 60)), legenda=5000, titulo=100,
                           titulo_ideal=70, bytes=True, hashtags=5, segura=(380, 480, 140, 60), max_mb=4000),
    "kwai_video": dict(rede="kwai", tipo=V, w=1080, h=1920, dur=(3, 60, (15, 36)), legenda=2200, hashtags=5,
                       segura=(150, 400, 150, 60), max_mb=50, obs="sem documentação oficial (conf. D): valores do TikTok"),
    "whatsapp_status": dict(rede="whatsapp", tipo=V, w=1080, h=1920, dur=(1, 60, (15, 30)), legenda=0, hashtags=0,
                            segura=(200, 250, 60, 60), max_mb=16, bitrate=(4, 6)),
    "threads_video": dict(rede="threads", tipo=V, w=1080, h=1920, dur=(1, 300, (15, 60)), legenda=500, hashtags=1,
                          segura=(0, 0, 0, 0), max_mb=500),
    "pinterest_video": dict(rede="pinterest", tipo=V, w=1080, h=1920, dur=(4, 300, (6, 15)), legenda=500, titulo=100,
                            hashtags=0, segura=(270, 400, 120, 60), max_mb=2000),
    # ------------------------------------------------------------------ vídeo em outros quadros
    "linkedin_video": dict(rede="linkedin", tipo=V, w=1080, h=1350, dur=(3, 600, (30, 90)), legenda=3000, visivel=140,
                           hashtags=5, segura=(0, 0, 0, 0), max_mb=5000, obs="4:5 lê melhor no feed; 9:16 também aceito"),
    "facebook_feed_video": dict(rede="facebook", tipo=V, w=1080, h=1350, dur=(1, 180, (30, 180)), legenda=2200,
                                hashtags=5, segura=(0, 0, 0, 0), max_mb=1000),
    "x_video": dict(rede="x", tipo=V, w=1920, h=1080, dur=(1, 140, (30, 90)), legenda=280, hashtags=2,
                    segura=(0, 0, 0, 0), max_mb=512, obs="conta gratuita: 140 s"),
    "youtube_video": dict(rede="youtube", tipo=V, w=1920, h=1080, dur=(1, 43200, (240, 900)), legenda=5000, titulo=100,
                          titulo_ideal=70, bytes=True, hashtags=5, segura=(0, 0, 0, 0), max_mb=256000,
                          obs="capítulos: ≥ 3, o 1º em 00:00, cada um ≥ 10 s"),
    # ------------------------------------------------------------------ imagem
    "instagram_feed": dict(rede="instagram", tipo=I, w=1080, h=1350, itens=(1, 20), legenda=2200, visivel=125,
                           hashtags=5, max_mb=8),
    "instagram_carrossel": dict(rede="instagram", tipo=I, w=1080, h=1350, itens=(2, 20), legenda=2200, visivel=125,
                                hashtags=5, max_mb=8, obs="3:4 (1080x1440) aceito no app; a API pode cortar para 4:5"),
    "instagram_stories_img": dict(rede="instagram", tipo=I, w=1080, h=1920, itens=(1, 1), legenda=0, hashtags=0,
                                  segura=(270, 380, 65, 65), max_mb=8),
    "instagram_capa_reels": dict(rede="instagram", tipo=I, w=1080, h=1920, itens=(1, 1), legenda=0, hashtags=0,
                                 segura=(285, 285, 65, 65), max_mb=8,
                                 obs="a grade 3:4 mostra o centro 1080x1440; texto no bloco y 285-1635"),
    "tiktok_foto": dict(rede="tiktok", tipo=I, w=1080, h=1920, itens=(2, 35), legenda=2200, hashtags=5,
                        segura=(150, 400, 150, 60), max_mb=20),
    "facebook_foto": dict(rede="facebook", tipo=I, w=1080, h=1350, itens=(1, 10), legenda=2200, hashtags=5, max_mb=30),
    "linkedin_imagem": dict(rede="linkedin", tipo=I, w=1080, h=1350, itens=(1, 9), legenda=3000, visivel=140,
                            hashtags=5, max_mb=5),
    "x_imagem": dict(rede="x", tipo=I, w=1200, h=675, itens=(1, 4), legenda=280, hashtags=2, max_mb=5),
    "threads_imagem": dict(rede="threads", tipo=I, w=1080, h=1350, itens=(1, 20), legenda=500, hashtags=1, max_mb=8),
    "pinterest_imagem": dict(rede="pinterest", tipo=I, w=1000, h=1500, itens=(1, 1), legenda=500, titulo=100,
                             hashtags=0, max_mb=20),
    "whatsapp_status_img": dict(rede="whatsapp", tipo=I, w=1080, h=1920, itens=(1, 1), legenda=0, hashtags=0,
                                segura=(200, 250, 60, 60), max_mb=5),
    "youtube_thumbnail": dict(rede="youtube", tipo=I, w=1280, h=720, itens=(1, 1), legenda=0, hashtags=0, max_mb=2),
    # ------------------------------------------------------------------ documento
    "linkedin_documento": dict(rede="linkedin", tipo=D, w=1080, h=1350, itens=(2, 20), legenda=3000, visivel=140,
                               hashtags=5, max_mb=100),
}

# exportação de vídeo comum (R12 síntese: áudio e exportação)
EXPORT = dict(fps=30, bitrate=(10, 16), audio_kbps=192, audio_hz=48000, lufs=-14, true_peak=-1)

# qual destino cada "formato do perfil" (perfis.redes.<rede>.semana) alimenta
FORMATO_DO_PERFIL = {
    ("instagram", "reels"): "instagram_reels", ("instagram", "carrossel"): "instagram_carrossel",
    ("instagram", "post"): "instagram_feed", ("instagram", "stories"): "instagram_stories_img",
    ("tiktok", "video"): "tiktok_video", ("tiktok", "foto"): "tiktok_foto",
    ("youtube", "shorts"): "youtube_shorts", ("youtube", "video"): "youtube_video",
    ("linkedin", "documento"): "linkedin_documento", ("linkedin", "video"): "linkedin_video",
    ("linkedin", "imagem"): "linkedin_imagem", ("facebook", "reels"): "facebook_reels",
    ("facebook", "post"): "facebook_foto", ("kwai", "video"): "kwai_video", ("x", "video"): "x_video",
    ("x", "imagem"): "x_imagem", ("threads", "post"): "threads_imagem", ("pinterest", "imagem"): "pinterest_imagem",
    ("whatsapp", "status"): "whatsapp_status",
}


def destino(nome):
    if nome not in DESTINOS:
        raise KeyError(f"destino desconhecido: {nome} (opções: {', '.join(sorted(DESTINOS))})")
    return DESTINOS[nome]


def de_video(redes=None):
    """Destinos de vídeo (opcionalmente só das redes indicadas)."""
    return [k for k, v in DESTINOS.items() if v["tipo"] == V and (not redes or v["rede"] in redes)]


def destinos_do_perfil(perfil, tipo=None):
    out = []
    for rede, cfg in perfil.get("redes", {}).items():
        for fmt, n in cfg.get("semana", {}).items():
            d = FORMATO_DO_PERFIL.get((rede, fmt))
            if d and n and (tipo is None or DESTINOS[d]["tipo"] == tipo):
                out.append(d)
    return out


def _sonda(arq):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration,size:stream=codec_type,width,height",
                        "-of", "json", str(arq)], capture_output=True, text=True)
    return json.loads(r.stdout or "{}")


def validar_arquivo(arq, nome):
    """Alertas de um arquivo final contra o destino (dimensão, duração, tamanho)."""
    d = destino(nome)
    arq = Path(arq)
    al = []
    if not arq.exists():
        return [f"arquivo não existe: {arq}"]
    mb = arq.stat().st_size / 1e6
    if mb > d.get("max_mb", 1e9):
        al.append(f"{nome}: arquivo de {mb:.0f} MB acima do limite de {d['max_mb']} MB")
    info = _sonda(arq)
    v = next((s for s in info.get("streams", []) if s.get("codec_type") == "video"), None)
    if v and (v.get("width"), v.get("height")) != (d["w"], d["h"]):
        al.append(f"{nome}: {v.get('width')}x{v.get('height')} (esperado {d['w']}x{d['h']})")
    if d["tipo"] == V:
        dur = float(info.get("format", {}).get("duration", 0))
        mn, mx, (i0, i1) = d["dur"]
        if dur > mx:
            al.append(f"{nome}: {dur:.0f} s acima do máximo de {mx} s")
        elif dur < mn:
            al.append(f"{nome}: {dur:.1f} s abaixo do mínimo de {mn} s")
        elif not i0 <= dur <= i1:
            al.append(f"{nome}: {dur:.0f} s fora da faixa recomendada {i0}-{i1} s (aceito)")
    return al


def validar_texto(nome, legenda="", hashtags=(), titulo=""):
    d = destino(nome)
    al = []
    if d.get("legenda") is not None:
        tam = len(legenda.encode("utf-8")) if d.get("bytes") else len(legenda)
        if d["legenda"] and tam > d["legenda"]:
            al.append(f"{nome}: legenda com {tam} {'bytes' if d.get('bytes') else 'caracteres'} (limite {d['legenda']})")
        if d["legenda"] == 0 and legenda:
            al.append(f"{nome}: este formato não tem legenda (texto vai na arte)")
    if len(hashtags) > d.get("hashtags", 99):
        al.append(f"{nome}: {len(hashtags)} hashtags (limite {d['hashtags']})")
    if titulo and d.get("titulo") and len(titulo) > d["titulo"]:
        al.append(f"{nome}: título com {len(titulo)} caracteres (limite {d['titulo']})")
    elif titulo and d.get("titulo_ideal") and len(titulo) > d["titulo_ideal"]:
        al.append(f"{nome}: título com {len(titulo)} caracteres (ideal ≤ {d['titulo_ideal']}, corta no celular)")
    return al
