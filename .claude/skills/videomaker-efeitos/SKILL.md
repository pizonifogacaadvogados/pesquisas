---
name: videomaker-efeitos
description: Skill-filha do videomaker para a "edição com IA" no nível dos criadores que editam com Claude Code (Tiago Lemos, André Nunes, edicaomia, castilho.ia) - efeitos HyperFrames sobre o vídeo (título com brilho, card de PERGUNTA, card flutuante, HUD de visão computacional com rastreamento real, perspectiva 3D em camadas, motion explicativo com lista, transcrição ao vivo com forma de onda, preto e branco de ênfase), cortes de vídeo longo em N clipes e variações de gancho. Use quando o usuário pedir "edição incrível", "igual ao do Tiago", efeitos 3D, motion explicativo, cortes de podcast/live ou versões para teste.
---

# Efeitos de edição IA (o Claude é o editor)

Base: `sistema-redes/estudos/22-claude-editor.md` (análise das referências) e registro R15. Trabalhe em `sistema-redes/`.
**Princípio:** o Claude edita o vídeo inteiro por código (sem abrir editor). O efeito serve à fala; nunca efeito pelo efeito.

## 1. Briefing (as 5 "skills" de direção, preencha antes de editar)
| Eixo | Pergunta | Onde vira código |
|---|---|---|
| **Estilo** | Qual cor/clima? (perfil: dourado jurídico, azul político; "roxo" = clima tech) | `--estilo`, `tema_efeitos`, LUT |
| **Ritmo** | Cortes secos, respiração cortada, pausa dramática antes do ponto principal? | preset (`juridico`, `politico`, `dinamico`), `cortes_pausa` |
| **Legendas** | Palavra-chave em destaque? Estilo premium/forte/viral? | legenda do estilo |
| **Movimento** | Push-ins, camadas 3D, cards entrando? | câmera do estilo + efeitos |
| **Composição** | O que fica onde (rosto, legenda, card, título) sem colidir? | zonas seguras (R12) |

## 2. Catálogo (`python3 -m redes efeitos VIDEO efeitos.json --perfil <id>`)
| Efeito | O que faz | Quando usar (advocacia/política) | Custo de render |
|---|---|---|---|
| `titulo` | kicker + título enorme com gradiente e brilho | abertura de tema forte ("SEU DIREITO"), virada de assunto | ~1 min |
| `pergunta` | card "PERGUNTA" no topo | **formato "você pergunta, eu respondo"** (melhor formato jurídico) | ~1 min |
| `card` | card inclinado com imagem e etiqueta ("SALVO", "DECISÃO", "LEI") | mostrar print de decisão, notícia, artigo de lei, post anterior | ~1 min |
| `lista` | motion explicativo: título + itens que acendem no tempo da fala + apresentador em janela | "3 direitos", "o que muda com a lei", propostas | ~3 min |
| `camadas` | o quadro se abre em 5 camadas 3D e fecha | abertura de série/quadro especial (com moderação) | ~6-10 min |
| `transcricao` | linha do tempo com palavras, forma de onda e contador | conteúdo sobre IA, tecnologia, LGPD, "bastidores da edição" | ~3 min |
| `hud` | visão computacional com rastreamento real de rosto/olhos/boca | conteúdo sobre IA, reconhecimento facial, provas digitais | ~1 min |
| `pb` | trecho em preto e branco (+ título opcional) | ênfase: "ATENÇÃO", o ponto que não pode passar | instantâneo |
Spec: lista JSON com `tipo`, `ini`, `fim` (segundos do vídeo final) e os campos de cada efeito (docstring de `redes/video/efeitos.py`). Pelo gestor: campo `efeitos` da pauta (`pauta editar <id> --campos '{"efeitos": [...]}'`); o `executar` aplica depois da produção e antes da exportação, e tira o título padrão quando um `titulo`/`camadas` abre o vídeo.

## 3. Regras de uso
- **No máximo 2-3 efeitos "grandes" por vídeo de 60 s** (camadas, lista, transcrição). Pergunta e card podem aparecer mais.
- Tempos pelos **momentos da fala**: use `producao.json → palavras` para achar onde cada frase começa.
- Nada sob a legenda nem no terço inferior direito (botões): os efeitos já respeitam isso; confira nos quadros.
- HUD e transcrição são "meta": funcionam quando o tema é tecnologia; em vídeo de direito do consumidor comum, prefira `pergunta`, `lista`, `card`.
- Tema: cores do perfil por padrão; `roxo` só se o perfil assumir o clima "tech".

## 4. Reutilizar (um material, muitas peças)
```bash
python3 -m redes cortes live.mp4 --srt live.srt -n 10 --preset juridico --dur 30-60 --saida cortes/   # 1 hora → 10 clipes
python3 -m redes variacoes gravacao.mp4 --srt g.srt -n 3 --saida variacoes/                           # versões A/B/C de gancho
```
Publique as variações como **Trial Reels** e mantenha a que tiver menor taxa de pulo (registre em `metricas`).

## 5. Revisão (ficha, obrigatória)
Extraia quadros de cada efeito (início, meio, fim) e confira: (1) texto legível no celular; (2) nada cortado nas bordas;
(3) o efeito entra e sai com movimento (sem "pulo"); (4) não cobre rosto nem legenda; (5) sincronia com a fala;
(6) cores do perfil; (7) conformidade (`checar`) do texto dos efeitos.
