# Diário de aprendizados (como cada coisa foi descoberta)

Registro cronológico do que o Claude aprendeu construindo o sistema: o problema, **como foi descoberto**, a causa
e o que mudou no código. Complementa `pesquisa/registro/R08-testes-tecnicos.md` (testes) e `memoria/LICOES.md`
(aprendizado automático por métricas). Toda fase nova acrescenta entradas aqui.

## Fases 1-9 (resumo; detalhes em R01-R11 e estudos 01-21)
- **"Fora de uma edição cinematográfica" (v1).** Descoberto pela avaliação do usuário. Causa: cortes e legendas por regras de viral, sem cor/som/movimento. Mudança: estilos com LUT, câmera com easing, desenho de som (v2).
- **"Recorte visonho, fundo ruim" (v2).** Descoberto pela avaliação do usuário e confirmado extraindo quadros (franja branca no cabelo). Causa: modelo de recorte de *foto* (rembg) aplicado quadro a quadro, sem coerência temporal, e cor da pessoa diferente do fundo. Mudança: RVM (modelo de vídeo), cor casada, light wrap (v3); tremor da borda caiu 37% (R08.33).
- **O limite real é a captação.** Descoberto comparando quadros nossos com os de referência (estudo 21): eles gravam com luz a 45°, fundo com profundidade e 4K. Mudança: `visao` passou a dar recomendações de captação e o estudo 20 virou checklist.

## Fase 10 (sistema de ponta a ponta)
- **OpenCV 5 sem `CascadeClassifier`.** Descoberto na auditoria ao rodar `visao` (AttributeError). Mudança: detector YuNet (`nucleo/rosto.py`).
- **WhatsApp Status acima de 16 MB / Kwai acima de 50 MB.** Descoberto medindo os arquivos exportados no teste multirrede. Mudança: 720p no Status e bitrate calculado pelo limite de cada rede.
- **13 codificações para 13 redes.** Descoberto pelo tempo de exportação. Mudança: assinatura da especificação → redes iguais compartilham arquivo (13 → 5).
- **Capa com legenda queimada.** Descoberto olhando a capa gerada. Mudança: capa sai do `base.mp4`.

## Fase 11 (o Claude como editor)
- **O "editor IA" dos criadores é código, não um app.** Descoberto lendo as capturas quadro a quadro (estudo 22): o que aparece (camadas 3D, HUD, transcrição com forma de onda) é motion graphics em HTML/CSS 3D renderizado por quadro — exatamente o que o HyperFrames faz. Mudança: `video/efeitos.py`.
- **HUD quebrava no quadro 540×960.** Descoberto no primeiro render (erro do YuNet: tamanho de entrada fixo 320×320). Mudança: `Detector.marcos()` ajusta `setInputSize` a cada quadro.
- **Camadas 3D cortavam o título; card cobria o rosto.** Descoberto pela folha de quadros da demo (revisão visual). Mudança: deslocamento x 90 na abertura; card de 340 px no topo 430.
- **Pergunta e HUD por cima do cartão "Art. 49 · CDC" da produção.** Descoberto na mesma revisão visual. Causa: efeitos e cartões vêm de etapas diferentes. Mudança: `efeitos.conflitos()` cruza os tempos e avisa no `executar`.
- **Render de 8 efeitos levava 7-10 min a cada ajuste.** Descoberto medindo (`time`). Mudança: cache por `index.html` — só o efeito alterado é refeito. Atenção: mudar a ordem/tempo dos efeitos muda o nome da pasta e invalida o cache (re-render de 5m40s na demo final).

## Fase 12 (pesquisa além dos exemplos)
- **Faltava o Claude revisar o próprio corte com números.** Descoberto ao comparar o fluxo com o de agências (QC antes da entrega, R18). Mudança: `video/qc.py` (loudness, pico, silêncios, quadros pretos/congelados, rosto visível, rosto sob a interface, ritmo de mudanças de plano, folha de quadros), rodando sozinho no `executar`.
- **Calibração do QC.** Descoberto rodando o QC na demo: a janela do apresentador da `lista` contava como "rosto principal". Mudança: só rostos com mais de 15% da largura do quadro. O vídeo sintético do teste deu 0% de rosto — correto (não há rosto real).
