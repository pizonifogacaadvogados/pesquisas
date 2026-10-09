# Edição de vídeo com o Claude: ferramentas disponíveis (out/2026)

## Resumo

O Claude não "assiste" vídeo. Ele edita **lendo** o vídeo por três vias: metadados, transcrição com tempos e frames extraídos como imagem. A partir disso, ele decide os cortes e executa por uma de quatro rotas:

| Rota | Como funciona | Bom para | Precisa de |
|---|---|---|---|
| **1. ffmpeg direto (Claude Code)** | Claude escreve e roda comandos ffmpeg | cortes, legendas, vertical, silêncios, compressão | ffmpeg (grátis) |
| **2. Vídeo como código (Remotion / Manim)** | Claude escreve código React/Python que vira MP4 | vídeos com animação, textos, gráficos, marca | Node.js ou Python |
| **3. MCP controlando editor desktop** | Claude opera DaVinci / Premiere / CapCut | timeline real, revisão humana no editor | o editor instalado |
| **4. Conectores hospedados** | Claude edita na nuvem do fornecedor | quem não quer instalar nada | conta paga (Descript, Adobe…) |

**Recomendação para começar:** rota 1 (ffmpeg + skill). É grátis e roda em qualquer lugar; já está testada neste repositório (ver `../.claude/skills/editor-de-video/`).

## 1. ffmpeg direto + skills

- **Skill própria `editor-de-video`** (neste repo): fluxo inspecionar → transcrever → propor cortes → renderizar → conferir, com receitas prontas e scripts de remoção de silêncio e transcrição.
- **Youtube Clipper Skill** (op7418): baixa vídeo, gera capítulos, corta, traduz e queima legendas. `npx skills add https://github.com/op7418/Youtube-clipper-skill`. [GitHub](https://github.com/op7418/Youtube-clipper-skill)
- **ffmpeg-mcp-lite**: servidor MCP local que corta, junta e queima legendas. [GitHub](https://github.com/kevinwatt/ffmpeg-mcp-lite)
- **Edição guiada por transcrição**: transcreve → o modelo propõe um EDL (lista de cortes) → ffmpeg renderiza. Funciona melhor com vídeos de pessoa falando para a câmera e podcasts.

## 2. Vídeo como código

- **Remotion Agent Skills (oficial do Remotion)**: `npx skills add remotion` e você descreve o vídeo; o Claude escreve os componentes React e renderiza o MP4. [Docs](https://www.remotion.dev/docs/ai/claude-code). Atenção: o Remotion exige licença paga para empresas acima de um certo porte; confira antes de usar comercialmente.
- **Claude Code Video Toolkit** (digitalsamba): modelo de projeto com temas, transições e perfis de marca. [GitHub](https://github.com/digitalsamba/claude-code-video-toolkit)
- **Manim** (animações estilo 3Blue1Brown): [manim-skill](https://github.com/Yusuke710/manim-skill).

## 3. MCP controlando editores (comunitários, não oficiais)

| Editor | Projeto | Observações |
|---|---|---|
| DaVinci Resolve | [samuelgursky/davinci-resolve-mcp](https://github.com/samuelgursky/davinci-resolve-mcp) | o mais popular; versão grátis do Resolve só via script ponte |
| DaVinci Resolve (grátis) | [hiteshK03/davinci-resolve-mcp](https://github.com/hiteshK03/davinci-resolve-mcp) | ponte para a versão gratuita, transcrição local |
| Premiere Pro | [hetpatel-11/Adobe_Premiere_Pro_MCP](https://github.com/hetpatel-11/Adobe_Premiere_Pro_MCP) | painel CEP aberto no Premiere; telemetria ligada por padrão |
| After Effects | [Dakkshin/after-effects-mcp](https://github.com/Dakkshin/after-effects-mcp) | só camadas/composições |
| CapCut / Jianying | [sun-guannan/VectCutAPI](https://github.com/sun-guannan/VectCutAPI) | gera rascunho; renderização final no CapCut |

## 4. Conectores hospedados (oficiais dos fornecedores)

- **Descript MCP**: edita projetos do Descript por comando; consome minutos e créditos de IA. [GitHub](https://github.com/descriptinc/descript-mcp)
- **Adobe for creativity**: conector da Adobe com fluxos prontos (ex.: Quick Cut). [Docs](https://developer.adobe.com/adobe-for-creativity/)
- **Wireflow**: edita dentro de fluxos do Wireflow; consome créditos. [Docs](https://www.wireflow.ai/docs/mcp)

## Limites

- Ele não avalia estética, ritmo ou expressão facial com confiança. O resultado precisa de revisão humana.
- Escolha de imagens de apoio (B-roll), correção de cor fina e motion design complexo ainda funcionam melhor num editor visual.
- O ffmpeg é a rota mais flexível e também a que mais erra: às vezes o modelo inventa parâmetros de filtro que não existem. Por isso a skill obriga a conferir o arquivo final.

## Teste feito (09/10/2026)

No ambiente do Claude Code (ffmpeg 6.1):
1. Gerei um vídeo de 20s em 1920×1080, cortei de 5s a 15s, coloquei legenda e converti para 1080×1920 (Reels). Funcionou.
2. Rodei o script de remoção de silêncios num vídeo de 15s com dois silêncios de 3s. Resultado: 9,6s. Funcionou.

## Fontes

- [a1adams/mcp-servers-for-video-editing](https://github.com/a1adams/mcp-servers-for-video-editing): comparativo de servidores MCP
- [wilwaldon/Claude-Code-Video-Toolkit](https://github.com/wilwaldon/Claude-Code-Video-Toolkit): lista de skills e ferramentas
- [MindStudio: Automate Video Editing With Claude Code](https://www.mindstudio.ai/blog/automate-video-editing-claude-code)
- [Linkeddit: Can Claude Edit Videos?](https://linkeddit.com/blog/can-claude-edit-videos)
- [explainx: video-use, AI Video Editing With Claude Code](https://explainx.ai/blog/video-use-claude-code-ai-video-editor-guide-2026)
- Servidores MCP no Glama: [DaVinci (apvlv)](https://glama.ai/mcp/servers/apvlv/davinci-resolve-mcp), [Clean-Cut-MCP (Remotion)](https://glama.ai/mcp/servers/endlessblink/clean-cut-mcp)
