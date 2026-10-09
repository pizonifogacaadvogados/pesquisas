# E6: Automação do CapCut Web pelo Claude

## 1. Opções avaliadas

| Opção | Como funciona | Veredito |
|---|---|---|
| **Claude in Chrome** (extensão oficial) | o Claude vê a página, clica, digita e arrasta no **seu** Chrome, já logado no CapCut | ✅ **escolhida**: é exatamente o que você pediu (Chrome Web logado) |
| Computer use (app desktop do Claude) | o Claude controla a tela inteira | ✅ alternativa, se a extensão falhar |
| Playwright/Selenium com seletores fixos | script clica em elementos por código | ❌ frágil: o CapCut muda a interface com frequência e a página é feita de canvas, sem seletores estáveis |
| API do CapCut | não existe API pública de edição | ❌ |
| VectCutAPI (gera rascunhos do CapCut desktop) | escreve o projeto do CapCut desktop diretamente | 🟡 possível no futuro, mas é para desktop, não web |
| Render direto por ffmpeg | o próprio sistema monta o vídeo final | ✅ **plano B garantido**, que também serve de pré-visualização |

## 2. Riscos e como o sistema lida com eles

| Risco | Mitigação |
|---|---|
| **Upload de arquivo pelo Claude in Chrome é instável** (vários relatos de bug em 2026) | **Você** sobe o vídeo bruto (e o pacote de assets) para o CapCut. O sistema só usa o que já está em "Mídia" |
| Interface muda | roteiro por **intenção + verificação visual**; o Claude procura o equivalente e tira print após cada etapa |
| Arrastar com precisão de tempo é difícil | preferir digitar valores (tempo, escala) nos campos; dar zoom na timeline antes de cortar; cortar **do fim para o começo** |
| Ações longas (dezenas de cortes) | o pipeline local já entrega o trecho **pré-cortado** (sem silêncios) quando possível; no CapCut ficam só os efeitos criativos |
| Recursos Pro | o plano traz alternativa grátis para cada efeito |
| Erro no meio | o roteiro é dividido em **etapas com checkpoint**; o projeto do CapCut salva sozinho, e dá para retomar da etapa N |
| Conta e termos de uso | uso pessoal, no seu navegador e com sua conta, com ritmo humano. Sem raspagem e sem automação em massa |

## 3. Arquitetura escolhida (dois modos)

```
                      ┌──────────────────────────┐
  vídeo bruto ──────► │ 1. ANÁLISE (local)       │  transcrição palavra a palavra,
                      │    videomaker analisar   │  silêncios, energia da voz
                      └────────────┬─────────────┘
                                   ▼
                      ┌──────────────────────────┐
                      │ 2. MOMENTOS + PLANO      │  melhores trechos, gancho, cortes,
                      │    videomaker planejar   │  zooms, emojis, SFX, legendas → plano.json
                      │    (+ revisão do Claude) │
                      └───────┬───────────┬──────┘
                              ▼           ▼
          ┌──────────────────────┐   ┌──────────────────────────────┐
          │ 3A. RENDER ffmpeg    │   │ 3B. ROTEIRO CAPCUT           │
          │ videomaker renderizar│   │ videomaker capcut → roteiro.md│
          │ → final.mp4 (pronto) │   │ Claude in Chrome executa no  │
          └──────────────────────┘   │ seu CapCut Web logado        │
                                     └──────────────────────────────┘
```

- **Modo completo:** análise local + render ffmpeg + execução no CapCut (você ajusta no CapCut à vontade).
- **Modo só CapCut** (sem instalar transcrição): o Claude gera a legenda automática no próprio CapCut, lê o texto das legendas na tela, planeja e executa.

## Fontes

- [Relatos de bug do file_upload no Claude in Chrome (2026)](https://claudeissues.com/issue/73161-claude-in-chrome-file-upload-and-upload-image-are-100-broken-client-extension-pr)
- [Feature request: acesso a pasta local](https://claudeissues.com/issue/75896-feature-claude-in-chromes-file-upload-upload-image-cannot-reference-local-folder)
- [VectCutAPI](https://github.com/sun-guannan/VectCutAPI)
- [a1adams/mcp-servers-for-video-editing](https://github.com/a1adams/mcp-servers-for-video-editing)
