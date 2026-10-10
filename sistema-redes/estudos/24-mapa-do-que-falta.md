# 24. Mapa do que falta: edição de editor sênior, luz, ambientes, Claude × CapCut e cronograma (Fase 13)

Pedido: registrar tudo o que **não** foi pesquisado/aprimorado e dá para focar (formas de edição, áreas de cinema, iluminação,
escritório × rua × externas, tipos de edição por ambiente), analisar os vídeos do @tiagolemosx e montar um cronograma do que falta
aprender, praticar e fazer. Escrito no fim dos créditos da sessão: **o que está aqui é conhecimento de ofício consolidado + o que foi
medido no sistema; o que não foi verificado na prática está marcado "a testar"**.

## 1. Os vídeos do Tiago Lemos (@tiagolemosx): o que deu e o que falta
- Tentado nesta sessão (R20): canal e vídeo `IobZgb7ngz4` por youtube.com, oEmbed, noembed, miniaturas (i.ytimg), Invidious,
  r.jina.ai e yt-dlp 2026.8.19 → **todos bloqueados pelo proxy (403 / sem conexão)**. A busca na web não indexa o canal.
- **Construído para destravar:** `python3 -m redes referencia ref.mp4 --comparar nosso.mp4` (`redes/video/referencia.py`): mede
  cortes por minuto, plano médio/maior, mudança visual a cada X s, loudness, silêncios, rosto visível e enquadramento
  (close/médio/aberto), brilho/contraste/saturação, e monta a folha com um quadro por plano. Testado na demo v4 × base (49 s).
- **O que fazer na próxima sessão (receita):**
  1. No computador do escritório (rede sem bloqueio), baixe 10-20 vídeos do canal só para estudo:
     `pip install yt-dlp && yt-dlp -f "bv*[height<=1080]+ba/b" -o "ref/%(id)s.%(ext)s" --playlist-end 20 https://www.youtube.com/@tiagolemosx/videos`
     (ou grave a tela do celular). Inclua `https://www.youtube.com/watch?v=IobZgb7ngz4`. Não republicar: é material de terceiro.
  2. Suba a pasta `ref/` para o repositório (ou para a sessão) e rode `python3 -m redes referencia ref/<id>.mp4 --comparar exemplo/v4/demo_efeitos.mp4` em cada um.
  3. Com as folhas de planos, o Claude descreve cada efeito (tipo, duração, entrada/saída, posição, fonte, cor) e cria a "receita" no `efeitos.py` para o que ainda não existe.
  4. Monte uma tabela "assinatura do Tiago": cortes/min, plano médio, % com gráfico, tipos de efeito por minuto, cor média → vira um preset `estilo: tiago` (sem copiar marca nem identidade dele).
  5. Transcreva 3 vídeos (sherpa-onnx ou `--srt`) e estude o roteiro: gancho, promessa, prova, virada, CTA.

## 2. Áreas de cinema ainda não exploradas (por prioridade)
| Área | O que é | Por que importa para advocacia/política | Status |
|---|---|---|---|
| **Iluminação** | chave a 45° e acima do olho, preenchimento 1-2 stops abaixo (razão 2:1 a 4:1), contraluz/recorte, luz prática no fundo | é a maior diferença entre "amador" e "caro" — o código não cria luz que não existe (estudo 20) | só checklist; **a testar** com gravação real |
| **Direção de atuação** | olhar na lente, energia +20 %, frases curtas, pausa antes do ponto principal, mãos no quadro | retenção nasce da fala; o corte só lapida | a fazer: roteiro/teleprompter com marcações |
| **Lentes e enquadramento** | 35-50 mm equivalentes no rosto (sem distorção), olhos no terço superior, headroom pequeno no vertical | celular em ultra-angular deforma o rosto (nariz grande) | a testar |
| **Profundidade** | fundo a ≥ 1,5 m da pessoa, modo retrato com moderação | separa a pessoa sem recorte por IA | checklist |
| **Som de captação** | lapela a 15-20 cm, sala com tecido, sem ar-condicionado | a limpeza (DeepFilterNet) ajuda, não salva | voz.py pronto |
| **Color grading** | correção primária (balanço, exposição) → look (LUT) → pele protegida (vetorscópio, linha de pele) | pele natural transmite confiança | LUTs prontas; **falta** checagem de tom de pele no QC |
| **Montagem (Murch)** | emoção > história > ritmo; corte no movimento; J/L cut; "respirar" após frase forte | ritmo jurídico ≠ político (R18) | parcial (cortes por fala) |
| **Design de som** | room tone, whoosh no corte, riser antes da revelação, silêncio como ênfase | sensação de produção cara | parcial (sfx, ducking) |
| **B-roll** | planos de detalhe (documento, caneta, fachada do fórum, mãos), 3-6 inserções/min | ilustra sem expor cliente | **não feito**: banco próprio de B-roll |
| **Motion design** | tipografia cinética, infográficos de lei, linha do tempo de processo | explicar direito com imagem | efeitos.py (8 efeitos) |
| **Multicâmera** | 2 ângulos (frontal + 3/4) cortando entre si | ritmo sem zoom digital | **não feito** (sincronia por áudio a implementar) |
| **Formatos longos** | YouTube 8-15 min, capítulos, retenção por arco | autoridade e busca | parcial (exportação 16:9) |

## 3. Por ambiente: como gravar e como editar
| Ambiente | Captação | Edição (o que muda) | Riscos |
|---|---|---|---|
| **Escritório (estúdio fixo)** | luz chave + preenchimento fixos (marque o chão), estante/obras ao fundo a 1,5 m, luz prática quente no fundo, câmera na altura do olho, lapela | estilo `estudio`/`juridico`: legenda premium, cartões de lei, punch-in 1,15-1,25 no ponto, cor neutra-quente, sem recorte de fundo (é real) | fundo poluído; janela atrás (contraluz) |
| **Escritório (mesa/reunião)** | plano médio 3/4, segunda câmera no detalhe (documentos sem dados) | cortes entre ângulos, B-roll de detalhe, menos gráfico | dados de cliente visíveis (LGPD) → `foto anonimizar` |
| **Rua / externa (walk-and-talk)** | sol atrás/lateral (nunca de frente no rosto), rebatedor ou sombra aberta, estabilizador, lapela sem fio com espuma (vento) | ritmo mais rápido, legenda sempre (ruído), DeepFilterNet obrigatório, cor: protege céu e pele, pouco gráfico (o ambiente é o "efeito") | vento, pessoas ao fundo (direito de imagem), marcas |
| **Fórum / tribunal (fachada, corredor)** | só áreas permitidas, sem filmar partes/processos | B-roll de contexto + fala curta; títulos de lugar | regras do tribunal; sigilo |
| **Evento / palestra** | câmera fixa no palco + celular de plateia, áudio da mesa de som | cortes de 30-60 s (`cortes`), legenda, nome/cargo, aplausos como respiro | áudio de sala (reverberação) |
| **Política: rua / comício / visita** | equipe de 2 (câmera + áudio), planos de multidão e de detalhe (mãos, rostos da comunidade com autorização) | montagem emocional, trilha (licença política! R19), legenda forte, cortes de discurso | TSE (deepfake, rótulo IA, datas), autorização de imagem |
| **Carro / bastidor** | celular no suporte, luz da janela lateral | autêntico, pouca edição, legenda | segurança; som do carro |

## 4. Técnicas de editor sênior ainda por implementar no sistema
1. **Corte no movimento e no olhar** (match cut): detectar piscadas/movimentos de cabeça e preferir cortar nelas (YuNet já dá os marcos dos olhos).
2. **J/L cuts automáticos** com B-roll: o áudio da próxima frase entra 6-10 quadros antes.
3. **Room tone** em cortes secos para não "furar" o som (gravar 5 s de silêncio na captação).
4. ✅ **Checagem de tom de pele** no QC (vetorscópio: pele na linha de ~123°) — feito (R08.53). Falta: balanço de branco geral.
5. **Sincronia multicâmera por áudio** (correlação cruzada) e corte entre ângulos pela fala.
6. **Banco de B-roll** do escritório (pasta + etiquetas) e inserção por palavra-chave da fala.
7. **Retenção prevista**: marcar no plano os pontos de risco (> 8 s sem mudança, frase longa) antes do render.
8. **Revisor crítico separado** (subagente) com a folha de quadros + QC + transcrição, que reprova antes da entrega.
9. **Estilo "tiago"** a partir da dissecação das referências (seção 1).
10. Nitidez leve (`unsharp=5:5:0.5`) só quando o material foi ampliado (R19).

## 5. Claude × CapCut: qual a melhor forma de editar?
| Critério | Claude (código, este sistema) | CapCut (manual) |
|---|---|---|
| Velocidade em escala (10+ vídeos/semana, cortes de live) | **melhor**: tudo automático e repetível | lento |
| Consistência de marca, conformidade OAB/TSE, entrega por rede | **melhor**: regras no código | depende de quem edita |
| Sigilo de cliente | **local** | nuvem com licença perpétua (ToS 12/06/2025) |
| Ajuste fino "no olho" (timing de um efeito, escolha estética) | bom, via folha de quadros e iteração | **melhor**: interativo |
| Efeitos prontos de tendência (templates, transições da moda) | precisa programar cada um | **melhor**: biblioteca pronta |
| Custo de render | CPU lenta aqui (camadas 3D ≈ 10 min/4 s) | rápido |
**Recomendação:** o Claude é o editor principal (corte, legenda, cor, som, gráficos, QC, entrega); o CapCut fica para o retoque final
opcional, sem material sigiloso, em um computador do escritório. **O Claude dá conta** do nível das referências em edição; o que
ainda separa é a **captação** (luz, lente, fundo) e o **acervo** (B-roll, trilhas licenciadas, referências dissecadas).

## 6. Cronograma do que falta (aprender → praticar → fazer → medir)
| Semana | Foco | Entregável | Como medir |
|---|---|---|---|
| 1 | Referências: baixar 20 vídeos do @tiagolemosx e de 5 perfis jurídicos/políticos; rodar `referencia` | tabela "assinatura" + receitas de efeitos faltantes | cortes/min, plano médio, efeitos/min comparados aos nossos |
| 1 | Gravação teste no escritório com o checklist (estudo 20) | 3 vídeos de 45-60 s | QC verde; comparação lado a lado com referência |
| 2 | Luz: kit chave+preenchimento+contraluz; testar 3 esquemas (Rembrandt, borboleta, lateral) | fotos/quadros comparativos | contraste do rosto, separação do fundo |
| 2 | Externas: 1 walk-and-talk e 1 evento | 2 vídeos + cortes | ruído (voz.py), estabilidade |
| 3 | Implementar itens 1-4 da seção 4 (corte no olhar, J/L, room tone, pele no QC) | código + testes | QC e revisão humana |
| 3 | Transcrição local (sherpa-onnx) integrada | `analise` sem `--srt` | WER < 10 % |
| 4 | Multicâmera + banco de B-roll | 2 vídeos multicâmera | mudança visual a cada 2-4 s sem zoom digital |
| 4 | Revisor crítico + estilo "tiago" | preset + skill | aprovação na 1ª rodada |
| contínuo | Publicar, medir (taxa de pulo, retenção), `feedback` | LICOES.md alimentado | taxa de pulo < 35 % |

## 7. O que depende do usuário
Vídeos de referência baixados (seção 1); gravações reais no escritório e na rua; kit de luz e lapela; trilhas licenciadas
(inclusive com cláusula política); perfil real (`perfil criar escritorio-pizoni`); métricas após publicar.
