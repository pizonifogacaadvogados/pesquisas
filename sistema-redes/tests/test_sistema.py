"""Suíte do sistema (unittest; também roda com pytest). Isolada: perfis, dados e memória em pasta temporária.

  python3 -m unittest discover -s tests -v            # tudo (≈ 5-8 min: inclui vídeo)
  REDES_RAPIDO=1 python3 -m unittest discover -s tests # pula produção de vídeo e react
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

TMP = Path(tempfile.mkdtemp(prefix="redes_teste_"))
os.environ.update(REDES_PERFIS=str(TMP / "perfis"), REDES_DADOS=str(TMP / "dados"), REDES_MEMORIA=str(TMP / "mem"),
                  REDES_SEM_MOTION="1")
RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from PIL import Image  # noqa: E402

from redes.foto import capas, carrossel, post, tratamento  # noqa: E402
from redes.gestao import calendario, fluxo, pautas, publicacao  # noqa: E402
from redes.nucleo import conformidade, perfis, plataformas, rosto  # noqa: E402
from redes.video import exportar  # noqa: E402

RAPIDO = os.environ.get("REDES_RAPIDO") == "1"


def ff(*args):
    subprocess.run(["ffmpeg", "-y", "-v", "error", *map(str, args)], check=True)


def dur(f):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(f)],
                                capture_output=True, text=True).stdout)


def dims(f):
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height",
                          "-of", "csv=p=0", str(f)], capture_output=True, text=True).stdout.strip()
    return tuple(map(int, out.split(",")))


def tam(f):
    with Image.open(f) as im:
        return im.size


def setUpModule():
    perfis.criar("teste-adv", "advocacia")
    perfis.criar("teste-pol", "politico")
    # vídeo vertical sintético (12 s) com tom e "rosto" desenhado; e um de 65 s para o WhatsApp
    ff("-f", "lavfi", "-i", "testsrc2=s=540x960:r=30:d=12", "-f", "lavfi", "-i", "sine=f=330:d=12",
       "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", "-shortest", TMP / "v12.mp4")
    ff("-f", "lavfi", "-i", "color=c=0x334455:s=360x640:r=30:d=65", "-f", "lavfi", "-i", "sine=f=220:d=65",
       "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", "-shortest", TMP / "v65.mp4")
    im = Image.new("RGB", (1600, 1200), (190, 170, 150))
    im.save(TMP / "foto.jpg")


def tearDownModule():
    if os.environ.get("REDES_MANTER") != "1":
        shutil.rmtree(TMP, ignore_errors=True)


# ====================================================================== núcleo
class Nucleo(unittest.TestCase):
    def test_conformidade_oab(self):
        adv = perfis.carregar("teste-adv")
        self.assertEqual(conformidade.checar("Garantimos 100% de êxito, consulta grátis!", adv)["sinal"], "vermelho")
        self.assertEqual(conformidade.checar("É um direito garantido por lei: 7 dias (art. 49 do CDC).", adv)["sinal"], "verde")
        self.assertEqual(conformidade.checar("Sou o melhor advogado da cidade.", adv)["sinal"], "amarelo")
        r = conformidade.checar("CPF 123.456.789-09", adv)
        self.assertTrue(any("CPF" in i["regra"] for i in r["itens"]))

    def test_conformidade_tse(self):
        pol = perfis.carregar("teste-pol")
        self.assertEqual(conformidade.checar("Vote em mim!", pol, {"data": "2026-07-01"})["sinal"], "vermelho")
        self.assertEqual(conformidade.checar("Nossa proposta.", pol, {"data": "2026-10-25"})["sinal"], "vermelho")
        self.assertEqual(conformidade.checar("Nossa proposta.", pol, {"data": "2026-10-23", "impulsionar": True})["sinal"],
                         "vermelho")
        r = conformidade.checar("Nossa proposta. Propaganda Eleitoral.", pol, {"data": "2026-10-10", "impulsionar": True})
        self.assertEqual(r["sinal"], "verde")
        self.assertEqual(conformidade.checar("Texto.", pol, {"data": "2026-10-10", "usa_ia": True})["sinal"], "vermelho")
        self.assertEqual(conformidade.checar("x", pol, {"ia_rosto_voz_real": True})["sinal"], "vermelho")

    def test_conformidade_cta_dm(self):
        adv = perfis.carregar("teste-adv")
        self.assertEqual(conformidade.checar("Comenta PRAZO que eu te mando no direct", adv)["sinal"], "amarelo")
        self.assertEqual(conformidade.checar("Comente sua dúvida que respondo em vídeo", adv)["sinal"], "verde")

    def test_plataformas(self):
        self.assertTrue(plataformas.validar_texto("instagram_reels", "a", ["#a"] * 6))
        self.assertTrue(plataformas.validar_texto("x_video", "a" * 300))
        self.assertTrue(plataformas.validar_texto("youtube_shorts", "ç" * 2600))   # 5.000 BYTES (UTF-8)
        self.assertFalse(plataformas.validar_texto("instagram_reels", "ok", ["#a"]))
        adv = perfis.carregar("teste-adv")
        self.assertIn("instagram_reels", plataformas.destinos_do_perfil(adv, plataformas.V))

    def test_perfis(self):
        self.assertEqual(set(perfis.listar()), {"teste-adv", "teste-pol"})
        with self.assertRaises(FileExistsError):
            perfis.criar("teste-adv")
        with self.assertRaises(ValueError):
            perfis.criar("Nome Inválido")
        self.assertTrue(any("CNPJ" in a for a in perfis.validar(perfis.carregar("teste-pol"))))

    def test_rosto_detector(self):
        import numpy as np
        det = rosto.Detector()
        self.assertIn(det.motor, ("yunet", "haar"))
        self.assertEqual(det(np.zeros((360, 640, 3), np.uint8)), [])


# ====================================================================== braço de foto
class Foto(unittest.TestCase):
    def test_posts_todos_os_tipos(self):
        specs = [{"tipo": "frase", "texto": "Arrependimento é direito."},
                 {"tipo": "dado", "numero": "7", "legenda": "dias", "fonte": "CDC"},
                 {"tipo": "manchete", "titulo": "Decisão", "fonte": "STJ"},
                 {"tipo": "comunicado", "titulo": "Expediente", "texto": "Fechado no feriado."},
                 {"tipo": "evento", "dia": 15, "mes": "OUT", "titulo": "Live", "local": "IG", "hora": "19h"},
                 {"tipo": "foto", "foto": str(TMP / "foto.jpg"), "titulo": "Bastidores"},
                 {"tipo": "pergunta", "titulo": "Qual sua dúvida?"}]
        for s in specs:
            r = post.gerar(s, TMP / "posts" / s["tipo"], ("4x5", "9x16"), perfil="teste-adv")
            for arq, esperado in zip(r["arquivos"], [(1080, 1350), (1080, 1920)]):
                self.assertEqual(tam(TMP / "posts" / s["tipo"] / arq), esperado, s["tipo"])
        self.assertTrue(post.gerar({"tipo": "dado", "numero": "7", "legenda": "x"}, TMP / "p2", ("1x1",))["alertas"])

    def test_carrossel(self):
        spec = {"identidade": "manifesto", "autor": {"nome": "A", "handle": "@a"}, "slides": [
            {"tipo": "capa", "titulo": "Título curto"}, {"tipo": "item", "numero": 1, "titulo": "Um", "texto": "x"},
            {"tipo": "lista", "titulo": "Resumo", "itens": ["a", "b"]}, {"tipo": "cta", "titulo": "Salve"}]}
        r = carrossel.gerar(spec, TMP / "car", "4x5")
        self.assertEqual(len(r["png"]), 4)
        self.assertTrue((TMP / "car" / r["pdf"]).exists())
        self.assertTrue(any("slides" in a for a in r["alertas"]))     # 4 slides < 5 recomendado

    def test_carrossel_editorial(self):
        spec = {"identidade": "editorial_juridico", "autor": {"nome": "A"}, "slides": [
            {"tipo": "capa", "kicker": "Tema", "titulo": "Título com __destaque__"},
            {"tipo": "fluxo", "titulo": "Fluxo", "de": {"rotulo": "A"}, "meio": {"titulo": "7 dias"}, "para": {"rotulo": "B"},
             "cards": [{"icone": "1", "titulo": "Um", "texto": "x"}, {"icone": "2", "titulo": "Dois", "texto": "y"}]},
            {"tipo": "terminal", "titulo": "Modelo", "codigo": "Assunto: teste"},
            {"tipo": "grade", "titulo": "Grade", "cards": [{"titulo": "A"}, {"titulo": "B"}]},
            {"tipo": "cta_palavra", "palavra": "PRAZO", "texto": "comente"}]}
        r = carrossel.gerar(spec, TMP / "car_ed", "4x5")
        self.assertEqual(len(r["png"]), 5)
        self.assertFalse(any("CTA" in a for a in r["alertas"]))
        html_capa = (TMP / "car_ed" / "slide_01_4x5.html").read_text(encoding="utf-8")
        self.assertIn('<em class="ac">destaque</em>', html_capa)
        self.assertIn("01</b> / 05", html_capa)

    def test_tratamento(self):
        r = tratamento.tratar(TMP / "foto.jpg", TMP / "trat", ("4x5", "9x16"), "teste-adv")
        self.assertEqual(tam(r["arquivos"]["9x16"]), (1080, 1920))
        a = tratamento.anonimizar(TMP / "foto.jpg", [(0.1, 0.1, 0.2, 0.2)], TMP / "trat" / "anon.jpg", "tarja")
        self.assertEqual(Image.open(a).getpixel((300, 300)), (0, 0, 0))
        self.assertTrue(tratamento.moldura_print(TMP / "foto.jpg", TMP / "trat" / "p.jpg", "teste-adv", "G1").exists())

    def test_capas(self):
        r = capas.capa_reels(TMP / "v12.mp4", "Título ==teste==", TMP / "capa", "teste-adv")
        self.assertEqual(tam(TMP / "capa" / r["capa"]), (1080, 1920))
        self.assertEqual(tam(TMP / "capa" / r["grade"]), (1080, 1440))
        t = capas.thumbnail(TMP / "v12.mp4", "Seis palavras aqui para dar alerta", TMP / "thumb", "teste-adv")
        self.assertEqual(tam(TMP / "thumb" / t["thumbnail"]), (1280, 720))
        self.assertTrue(t["alertas"])


# ====================================================================== exportação
class Exportacao(unittest.TestCase):
    def test_multirrede(self):
        ds = ["instagram_reels", "tiktok_video", "linkedin_video", "x_video", "kwai_video"]
        r = exportar.exportar(TMP / "v12.mp4", TMP / "exp", ds)
        for d in ds:
            arq = TMP / "exp" / r["destinos"][d]["arquivos"][0]
            pd = plataformas.destino(d)
            self.assertEqual(dims(arq), (pd["w"], pd["h"]), d)
        self.assertAlmostEqual(dur(TMP / "exp" / "instagram_reels.mp4"), 12, delta=0.2)

    def test_whatsapp_divide(self):
        r = exportar.exportar(TMP / "v65.mp4", TMP / "exp_wa", ["whatsapp_status"])
        arqs = r["destinos"]["whatsapp_status"]["arquivos"]
        self.assertEqual(len(arqs), 2)
        for a in arqs:
            self.assertLessEqual((TMP / "exp_wa" / a).stat().st_size, 16e6)

    def test_qc(self):
        from redes.video import qc
        r = qc.revisar(TMP / "v12.mp4", TMP / "qc")
        self.assertIn(r["sinal"], ("verde", "amarelo", "vermelho"))
        self.assertIsNotNone(r["medidas"]["lufs"])
        self.assertTrue((TMP / "qc" / "folha_quadros.png").exists())
        self.assertTrue((TMP / "qc" / "QC.md").read_text(encoding="utf-8").startswith("# QC"))

    def test_entrega_versionada(self):
        from redes.gestao import entrega
        pal = [{"w": w, "ini": i * 0.4, "fim": i * 0.4 + 0.35} for i, w in enumerate(
            "Você sabia que pode cancelar uma compra feita pela internet? Sim, em sete dias.".split())]
        r1 = entrega.preparar(TMP / "ent", TMP / "v12.mp4", pal)
        r2 = entrega.preparar(TMP / "ent", TMP / "v12.mp4")
        self.assertEqual((r1["versao"], r2["versao"]), ("v01", "v02"))
        srt = (TMP / "ent" / "entrega" / "v01" / "legendas.srt").read_text(encoding="utf-8")
        self.assertTrue(all(len(l) <= 32 for l in srt.splitlines()))
        self.assertIn("internet?", srt)
        self.assertTrue((TMP / "ent" / "entrega" / "v02" / "previa_720p.mp4").exists())


class Reutilizar(unittest.TestCase):
    def test_cortes_e_variacoes(self):
        from redes.video import cortes
        frases = ["Você sabia que pode cancelar uma compra online?", "O artigo 49 do CDC garante isso.",
                  "O prazo é de sete dias.", "E a loja não pode cobrar multa.", "Muita gente acha que precisa de motivo.",
                  "Isso é mito.", "Salve este vídeo e compartilhe."] * 4
        pal, t = [], 0.5
        for f in frases:
            for w in f.split():
                pal.append({"w": w, "ini": round(t, 2), "fim": round(t + .32, 2), "energia": .6})
                t += .36
            t += .9
        an = {"palavras": pal, "duracao": t, "fonte": "x"}
        cl = cortes.escolher_clipes(an, 3, 12, 25)
        self.assertGreaterEqual(len(cl), 2)
        usados = [set(c["idx"]) for c in cl]
        self.assertFalse(usados[0] & usados[1])                     # sem sobreposição
        v = cortes.variacoes(an, TMP / "var", 3, "juridico", 12, 25, renderizar=False)
        self.assertGreaterEqual(len(v), 2)
        self.assertEqual(len({x["gancho"] for x in v}), len(v))       # ganchos diferentes


# ====================================================================== gestão
class Gestao(unittest.TestCase):
    def test_pautas_calendario(self):
        p = pautas.criar("teste-adv", "Tema A", "reels", gancho="Você sabia?")
        pautas.criar("teste-adv", "Tema B", "carrossel")
        pautas.atualizar(p["id"], status="roteiro")
        self.assertEqual(pautas.obter(p["id"])["status"], "roteiro")
        with self.assertRaises(ValueError):
            pautas.atualizar(p["id"], status="inexistente")
        self.assertTrue(pautas.sugerir("teste-adv"))
        cal = calendario.gerar("teste-adv", "2026-10-12", 1, TMP / "cal")
        self.assertTrue((TMP / "cal" / "calendario.ics").read_text().startswith("BEGIN:VCALENDAR"))
        self.assertTrue(any(i["pauta"] == p["id"] for i in cal["itens"]))
        pol = calendario.gerar("teste-pol", "2026-10-19", 1)
        self.assertFalse(any(i["data"] == "2026-10-25" for i in pol["itens"]))     # dia de eleição

    def test_legendas(self):
        x = publicacao.legenda("teste-adv", "x_video", "Gancho curto", "corpo longo " * 50, ["#a", "#b", "#c"])
        self.assertLessEqual(len(x["texto"]), 280)
        ig = publicacao.legenda("teste-adv", "instagram_reels", "Gancho", "Corpo", [f"#t{i}" for i in range(9)])
        self.assertLessEqual(len(ig["hashtags"]), 5)
        self.assertIn("OAB", ig["texto"])
        yt = publicacao.legenda("teste-adv", "youtube_shorts", "Título do vídeo", "Corpo")
        self.assertEqual(yt["titulo"], "Título do vídeo")
        pol = publicacao.legenda("teste-pol", "instagram_reels", "G", peca={"impulsionar": True, "usa_ia": True})
        self.assertIn("Propaganda Eleitoral", pol["texto"])
        self.assertIn("IA", pol["texto"])

    def test_fluxo_foto(self):
        spec = {"slides": [{"tipo": "capa", "titulo": "Capa"}, {"tipo": "promessa", "texto": "Promessa"},
                           {"tipo": "item", "numero": 1, "titulo": "Um"}, {"tipo": "item", "numero": 2, "titulo": "Dois"},
                           {"tipo": "cta", "titulo": "Salve"}]}
        p = pautas.criar("teste-adv", "Carrossel teste", "carrossel", gancho="Gancho", spec=spec)
        r = fluxo.executar(p["id"], TMP / "fx_car")
        self.assertEqual(r["conformidade"], "verde")
        self.assertTrue((TMP / "fx_car" / "pacote" / "PUBLICAR.md").exists())
        self.assertTrue(list((TMP / "fx_car" / "pacote" / "instagram_carrossel").glob("*.jpg")))
        self.assertTrue(list((TMP / "fx_car" / "pacote" / "linkedin_documento").glob("*.pdf")))
        self.assertEqual(pautas.obter(p["id"])["status"], "produzido")
        p2 = pautas.criar("teste-adv", "Post vermelho", "post", gancho="Consulta grátis! Ligue já",
                          spec={"tipo": "frase", "texto": "Garantimos resultado"})
        self.assertEqual(fluxo.executar(p2["id"], TMP / "fx_post")["conformidade"], "vermelho")

    def test_cli(self):
        env = dict(os.environ)
        r = subprocess.run([sys.executable, "-m", "redes", "checar", "Consulta grátis", "--perfil", "teste-adv"],
                           cwd=RAIZ, capture_output=True, text=True, env=env)
        self.assertEqual(r.returncode, 2, r.stderr)
        r = subprocess.run([sys.executable, "-m", "redes", "perfil", "listar"], cwd=RAIZ, capture_output=True, text=True,
                           env=env)
        self.assertIn("teste-adv", r.stdout)
        r = subprocess.run([sys.executable, "-m", "redes", "destinos"], cwd=RAIZ, capture_output=True, text=True, env=env)
        self.assertIn("youtube_thumbnail", r.stdout)


# ====================================================================== vídeo (produção completa e react)
@unittest.skipIf(RAPIDO, "REDES_RAPIDO=1")
class Video(unittest.TestCase):
    def test_pipeline_v1(self):
        r = subprocess.run([sys.executable, str(RAIZ / "tests" / "teste_pipeline.py"), str(TMP / "v1")],
                           capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stdout[-2000:] + r.stderr[-2000:])

    def test_fluxo_video_autentico(self):
        # usa o bruto sintético do pipeline v1 (fala = tons nos tempos do SRT)
        if not (TMP / "v1" / "bruto.mp4").exists():
            subprocess.run([sys.executable, str(RAIZ / "tests" / "teste_pipeline.py"), str(TMP / "v1")], check=True,
                           capture_output=True)
        p = pautas.criar("teste-adv", "Vídeo teste", "reels", gancho="Você sabia que pode cancelar?",
                         material=str(TMP / "v1" / "bruto.mp4"), srt=str(TMP / "v1" / "bruto.srt"), estilo="autentico",
                         destinos=["instagram_reels", "tiktok_video"])
        r = fluxo.executar(p["id"], TMP / "fx_video")
        self.assertIn(r["conformidade"], ("verde", "amarelo"))
        self.assertEqual(dims(TMP / "fx_video" / "pacote" / "instagram_reels" / "instagram_reels.mp4"), (1080, 1920))
        self.assertTrue((TMP / "fx_video" / "pacote" / "instagram_reels" / "capa_reels.png").exists())
        self.assertTrue((TMP / "fx_video" / "video" / "roteiro_capcut_pro.md").exists())

    def test_efeitos_overlay(self):
        from redes.video import efeitos
        r = efeitos.aplicar(TMP / "v12.mp4", [
            {"tipo": "pergunta", "ini": .5, "fim": 3.5, "texto": "Posso desistir da compra?"},
            {"tipo": "titulo", "ini": 4, "fim": 7, "kicker": "ATENÇÃO", "texto": "Seu direito"},
            {"tipo": "pb", "ini": 8, "fim": 10}], TMP / "ef.mp4", tema="dourado")
        self.assertEqual([x["efeito"] for x in r["efeitos"]], ["pb", "pergunta", "titulo"])
        self.assertEqual(dims(TMP / "ef.mp4"), (540, 960))
        self.assertAlmostEqual(dur(TMP / "ef.mp4"), 12, delta=0.2)

    def test_react(self):
        from redes.video import react
        rot = {"layout": "dividida", "credito": "@teste · 09/10/2026",
               "passos": [{"tipo": "original", "ini": 1, "fim": 3}, {"tipo": "comentario", "ini": 0, "fim": 5}]}
        v, rel = react.renderizar(TMP / "v12.mp4", TMP / "v12.mp4", rot, TMP / "react")
        self.assertTrue(Path(v).exists())
        self.assertGreaterEqual(rel["proporcao_comentario"], 0.5)


if __name__ == "__main__":
    unittest.main(verbosity=2)
