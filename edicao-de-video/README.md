# Edição de vídeo com o Claude: ferramentas disponíveis (out/2026)

## Resumo

O Claude não "assiste" vídeo. Ele edita **lendo** o vídeo por três vias: metadados, transcrição com tempos e frames extraídos como imagem. A partir disso, ele decide os cortes e executa por uma de quatro rotas:

| Rota | Como funciona | Bom para | Precisa de |
|---|---|---|---|
| **1. ffmpeg direto (Claude Code)** | Claude escreve e roda comandos ffmpeg | cortes, legendas, vertical, silêncios, compressão | ffmpeg (grátis) |
| **2. Vídeo como código (Remotion / Manim)** | Claude escreve código React/Python que vira MP4 | vídeos com animação, textos, gráficos, marca | Node.js ou Python |
| **3. MCP controlando editor desktop** | Claude opera DaVinci / Premiere / CapCut | timeline real, revisão humana no editor | o editor instalado |
| **4. Conectores no app do Claude** | Claude edita na nuvem do fornecedor, direto no chat (web, desktop, celular) | quem não quer instalar nada | conta no serviço (Descript, Adobe, HeyGen) |

**Recomendação:**
- **Sem programar, direto no app do Claude:** conector **Descript** (rota 4). É o mais próximo de "editar vídeo direto do Claude".
- **Com Claude Code:** a skill `editor-de-video` deste repositório (rota 1), que é grátis e já foi testada aqui. Para gravações longas com muito "é…" e "hã…", vale o **video-use**.

## 0. Direto no app do Claude (conectores oficiais)

Ative em claude.ai → Configurações → Conectores (ou no diretório de conectores). Funciona no navegador, no desktop e no celular, sem instalar nada.

| Conector | O que faz com vídeo | Observações |
|---|---|---|
| **[Descript](https://claude.com/connectors/descript)** | importa mídia, transcreve, remove vícios de linguagem ("é…", "hã…"), reduz ruído, legenda, tira cortes de entrevista, traduz | exige conta Descript paga; consome créditos de IA do plano; em acesso antecipado |
| **[Adobe for creativity](https://claude.com/marketplace/connectors/adobe-creativity)** | cria e redimensiona vídeos e fluxos como o Quick Cut, sem abrir o Premiere | lançado em 28/04/2026; não traz todos os recursos de cada app Adobe |
| **[HyperFrames (HeyGen)](https://claude.com/connectors/hyperframes-heygen)** | cria vídeos animados (slides, explicativos, motion graphics) a partir de HTML e renderiza o MP4 | gera vídeo novo, não edita gravação |
| Canva | design; edição de vídeo limitada | mais útil para capa/thumbnail |

**Fluxo típico com o Descript:** no chat, envie ou importe o vídeo e peça algo como: *"Tire os vícios de linguagem e as pausas longas, coloque legenda e faça 3 cortes verticais de até 60s com os melhores trechos."* O Claude dispara o agente do Descript, acompanha o job e devolve o projeto editado.

## 1. ffmpeg direto + skills

- **Skill própria `editor-de-video`** (neste repo): fluxo inspecionar → transcrever → propor cortes → renderizar → conferir, com receitas prontas e scripts de remoção de silêncio e transcrição.
- **Youtube Clipper Skill** (op7418): baixa vídeo, gera capítulos, corta, traduz e queima legendas. `npx skills add https://github.com/op7418/Youtube-clipper-skill`. [GitHub](https://github.com/op7418/Youtube-clipper-skill)
- **ffmpeg-mcp-lite**: servidor MCP local que corta, junta e queima legendas. [GitHub](https://github.com/kevinwatt/ffmpeg-mcp-lite)
- **[video-use](https://github.com/browser-use/video-use)** (browser-use, licença MIT, mais de 10 mil estrelas): o projeto que viralizou. Você coloca a gravação numa pasta, conversa com o Claude Code e recebe `final.mp4`. Corta "é…" e "hã…" palavra a palavra, aplica correção de cor, insere fades de áudio em cada corte e queima legendas. Também revisa os próprios cortes antes de entregar. Exige ffmpeg e uma **chave paga da ElevenLabs** para a transcrição.
- **Edição guiada por transcrição**: transcreve → o modelo propõe um EDL (lista de cortes) → ffmpeg renderiza. Funciona melhor com vídeos de pessoa falando para a câmera e podcasts.

## 2. Vídeo como código

- **Remotion Agent Skills (oficial do Remotion)**: `npx skills add remotion` e você descreve o vídeo; o Claude escreve os componentes React e renderiza o MP4. [Docs](https://www.remotion.dev/docs/ai/claude-code). Atenção: o Remotion exige licença paga para empresas acima de um certo porte; confira antes de usar comercialmente.
- **Claude Code Video Toolkit** (digitalsamba): modelo de projeto com temas, transições e perfis de marca. [GitHub](https://github.com/digitalsamba/claude-code-video-toolkit)
- **HyperFrames** (HeyGen): vídeo a partir de HTML. `npx skills add heygen-com/hyperframes` e depois `/hyperframes`; também existe como conector no app (ver seção 0).
- **Manim** (animações estilo 3Blue1Brown): [manim-skill](https://github.com/Yusuke710/manim-skill).

## 3. MCP controlando editores (comunitários, não oficiais)

| Editor | Projeto | Observações |
|---|---|---|
| DaVinci Resolve | [samuelgursky/davinci-resolve-mcp](https://github.com/samuelgursky/davinci-resolve-mcp) | o mais popular; versão grátis do Resolve só via script ponte |
| DaVinci Resolve (grátis) | [hiteshK03/davinci-resolve-mcp](https://github.com/hiteshK03/davinci-resolve-mcp) | ponte para a versão gratuita, transcrição local |
| Premiere Pro | [hetpatel-11/Adobe_Premiere_Pro_MCP](https://github.com/hetpatel-11/Adobe_Premiere_Pro_MCP) | painel CEP aberto no Premiere; telemetria ligada por padrão |
| After Effects | [Dakkshin/after-effects-mcp](https://github.com/Dakkshin/after-effects-mcp) | só camadas/composições |
| CapCut / Jianying | [sun-guannan/VectCutAPI](https://github.com/sun-guannan/VectCutAPI) | gera rascunho; renderização final no CapCut |

## 4. Outros conectores hospedados

- **Wireflow**: edita dentro de fluxos do Wireflow; consome créditos. [Docs](https://www.wireflow.ai/docs/mcp)
- Os conectores Descript e Adobe também podem ser usados no Claude Code. [Descript MCP](https://github.com/descriptinc/descript-mcp) · [Adobe docs](https://developer.adobe.com/adobe-for-creativity/)

## Limites

- Ele não avalia estética, ritmo ou expressão facial com confiança. O resultado precisa de revisão humana.
- Escolha de imagens de apoio (B-roll), correção de cor fina e motion design complexo ainda funcionam melhor num editor visual.
- O ffmpeg é a rota mais flexível e também a que mais erra: às vezes o modelo inventa parâmetros de filtro que não existem. Por isso a skill obriga a conferir o arquivo final.

## Teste feito (09/10/2026)

No ambiente do Claude Code (ffmpeg 6.1):
1. Gerei um vídeo de 20s em 1920×1080, cortei de 5s a 15s, coloquei legenda e converti para 1080×1920 (Reels). Funcionou.
2. Rodei o script de remoção de silêncios num vídeo de 15s com dois silêncios de 3s. Resultado: 9,6s. Funcionou.
3. Gravação simulada com voz sintética em português (22s, duas pausas de 2,5s): a remoção de silêncios levou a 16,8s. A imagem de "visão do trecho" (tira de frames + forma de onda) mostrou as pausas com clareza.
4. **Transcrição não testada:** a rede deste ambiente bloqueia o download dos modelos Whisper (Hugging Face e OpenAI). Num computador comum, `pip install faster-whisper` resolve.

## Vídeos do Instagram de referência

Não foi possível abrir os posts (o Instagram exige login e está bloqueado neste ambiente):
- https://www.instagram.com/p/Dd7zohQgyyQ/
- https://www.instagram.com/p/Ddt-i2HALql/ ("editar vídeo direto do Claude")

O mais provável é que tratem do **conector Descript/Adobe no app do Claude** ou do **video-use**, que foram os assuntos mais comentados no período. Falta confirmar.

## Fontes

- [a1adams/mcp-servers-for-video-editing](https://github.com/a1adams/mcp-servers-for-video-editing): comparativo de servidores MCP
- [wilwaldon/Claude-Code-Video-Toolkit](https://github.com/wilwaldon/Claude-Code-Video-Toolkit): lista de skills e ferramentas
- [MindStudio: Automate Video Editing With Claude Code](https://www.mindstudio.ai/blog/automate-video-editing-claude-code)
- [Linkeddit: Can Claude Edit Videos?](https://linkeddit.com/blog/can-claude-edit-videos)
- [explainx: video-use, AI Video Editing With Claude Code](https://explainx.ai/blog/video-use-claude-code-ai-video-editor-guide-2026)
- [browser-use/video-use](https://github.com/browser-use/video-use)
- [Conector Descript](https://claude.com/connectors/descript) · [Descript: Claude Connectors for Video and Podcast Teams](https://www.descript.com/blog/article/claude-connectors-video-podcast)
- [Adobe: Adobe for creativity, now in Claude](https://blog.adobe.com/en/publish/2026/04/28/adobe-for-creativity-connector) · [PetaPixel](https://petapixel.com/2026/04/28/claude-ai-can-orchestrate-creative-workflows-across-adobe-apps/)
- [Conector HyperFrames](https://claude.com/connectors/hyperframes-heygen)
- Servidores MCP no Glama: [DaVinci (apvlv)](https://glama.ai/mcp/servers/apvlv/davinci-resolve-mcp), [Clean-Cut-MCP (Remotion)](https://glama.ai/mcp/servers/endlessblink/clean-cut-mcp)
