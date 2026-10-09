# E15: Áudio e música, o que torna o vídeo "sentido"

> Base: R09.09-14, R03.15, R02.06. Princípio (Murch): som é metade do filme. Em vídeo curto, o som decide se a pessoa sente a emoção, e o silêncio decide onde ela presta atenção.

## 1. As 5 camadas de som

| Camada | Nível de referência | Função |
|---|---|---|
| **Voz** (diálogo) | pico ~−6 dBFS; integrado do vídeo final ≈ **−14 LUFS** | a mensagem: sempre a mais clara |
| **Áudio original de terceiro** (react) | −15 a −20 dB sob o seu comentário; cheio quando só ele fala | o objeto da reação |
| **Música** | **10-15 dB abaixo da voz** (≈ −18 a −24 dB); ducking de 6-12 dB, ataque 30-80 ms, release 250-700 ms | emoção e ritmo |
| **Efeitos (SFX)** | −6 a −12 dB relativos; o pico coincide com o corte ou a animação | marcar eventos visuais |
| **Ambiência / room tone** | quase inaudível | preencher cortes, "colar" o estúdio virtual |

## 2. Escolha da música por tipo de vídeo

| Tipo de vídeo | Clima | Características | Exemplo de busca (biblioteca/IA) |
|---|---|---|---|
| Jurídico educativo ("você sabia") | confiante, leve | piano/pluck, 90-110 BPM, sem vocal | "corporate minimal", "light piano pulse" |
| Jurídico de autoridade (estúdio) | sóbrio, premium | pads e cordas suaves, graves discretos | "cinematic ambient minimal" |
| Alerta / golpe / direito violado | tensão | pulsos graves, ostinato, 100-120 BPM | "tension pulse", "suspense minimal" |
| Documental (lei, decisão, história) | investigativo | pizzicato, relógio, sintetizador analógico | "investigative documentary" |
| Político: denúncia/contradição | tenso, dramático | graves, percussão, risers | "dramatic tension", "dark hybrid" |
| Político: proposta/esperança | ascendente | build-up, cordas, 110-128 BPM | "uplifting cinematic build" |
| Político: resposta-react firme | urgente | batida seca, phonk/trap instrumental (versão licenciada) | "dark trap instrumental" |
| Humor / leve | brincalhão | pizzicato, ukulele, bounce | "quirky playful" |
| React a vídeo viral | depende do original | geralmente **sem música** sob o original; música só no seu comentário | — |

**Regras:**
- **Sem vocal** sob fala (letra cantada compete com a voz).
- **Tempo da música ≈ ritmo do corte** (cortes nas batidas; detecção de batidas do CapCut).
- A música **muda com a história**: tensa no problema, resolve na solução.

## 3. Dinâmica de áudio ao longo do vídeo (automação)

```
tempo →   0s          3s                 clímax        resolução      fim
música:   ▁▃█ (abre)  ▂ (sob a voz) ...   ▁ STOPDOWN ▁   ▅ (volta)      ▆▃▁ (fade 1,5-3s)
voz:      ███         ███████████████    ███ frase ███  █████████
SFX:      HIT         · pop · whoosh ·   riser ↗ IMPACTO              · 
```

| Momento | O que o áudio faz |
|---|---|
| **Primeiro quadro** | impacto suave ou entrada da música já em andamento (sem fade-in lento); a voz começa em até 0,3s |
| **Sob a fala** | música abaixada (ducking) + passa-baixa leve (abre espaço para a voz) |
| **Pausas/respiros** | a música sobe 3-6 dB por 0,5-1s (preenche e mantém energia) |
| **Antes do clímax** | **riser** de 1-2s; ou **stopdown** (a música some 0,3-0,8s antes da frase-chave) |
| **Clímax** | impacto grave (hit/boom) + zoom; música volta mais cheia |
| **React: original falando** | música OFF ou −30 dB; original em volume cheio |
| **React: seu comentário** | original −15/−20 dB (ou pausado/congelado); música baixa |
| **Fim** | música sobe para fechar; fade 1,5-3s (corte seco de música é mais perceptível que corte de imagem) |

## 4. Onde conseguir música e SFX (licença!)

| Fonte | Licença | Uso no escritório |
|---|---|---|
| **Meta Sound Collection** (dentro do Instagram) | liberada para contas comerciais **no Instagram/Facebook** | Reels publicados direto no Instagram |
| **TikTok Commercial Music Library** | liberada **só dentro do TikTok** | vídeo publicado só no TikTok (adicionar no app) |
| Biblioteca do CapCut | muitas faixas "comercial: TikTok e CapCut" | **evitar** para Instagram/escritório |
| **Música por IA do CapCut** | descrita como livre para uso comercial (confirmar termos) | trilha exclusiva |
| Epidemic Sound / Artlist / Uppbeat / Soundstripe (assinatura) | licença multiplataforma para redes (conferir plano "business") | **recomendado** para vídeos em várias redes |
| YouTube Audio Library | grátis; limitada fora do YouTube | só YouTube |
| Pixabay Music | grátis com restrições; sem garantia contra Content ID | uso pontual com cautela |
| **Extrair áudio de outro vídeo** | só se você tem os direitos (seu próprio vídeo, sua live) | ⚠️ música de terceiros extraída = violação |
| Sons em alta (trending) | em geral **vedados a contas comerciais** | só conta pessoal/criador, e com cautela |

**Estratégia recomendada para o escritório:**
1. Publicar **sem música embutida** e adicionar a trilha **no próprio app** (Meta Sound Collection ou CML), ou
2. Usar banco pago com licença multiplataforma, ou música por IA, e embutir no vídeo.

## 5. SFX: paleta profissional

| Evento | Som | Observação |
|---|---|---|
| Abertura | impacto suave / "boom" grave | 1º quadro |
| Snap zoom | whoosh curto | pico no início do zoom |
| Transição de bloco | whoosh suave longo / flash | 0,25s antes do corte |
| Texto/cartão entrando | pop suave / papel (documental) | junto com a animação |
| Lower third | whoosh suave / papel | — |
| Congelar (react) | **tape stop** / record scratch | junto do congelamento |
| Carimbo FALSO | buzzer / impacto | político |
| Carimbo VERDADE | ding | — |
| Antes do clímax | riser 1-2s | termina no impacto |
| Clímax | hit grave (estilo Vine Boom, versão sóbria) | com zoom |
| Datas/documentos | máquina de escrever | documental |

Variar os sons (2-3 versões de cada) para não soar repetitivo.
