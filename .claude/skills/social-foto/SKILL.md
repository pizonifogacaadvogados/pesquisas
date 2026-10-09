---
name: social-foto
description: Braço de FOTO do sistema de redes - posts de imagem única (frase, manchete, dado, comunicado, evento, foto com texto, pergunta), stories, capas de Reels/TikTok, thumbnails do YouTube, tratamento de fotos (enquadramento pelo rosto, cor do perfil), recorte de pessoa, anonimização LGPD e moldura de prints; orquestra o social-carrossel. Use quando o usuário pedir post, arte, stories, capa, thumbnail, tratar foto, print de notícia ou qualquer peça de imagem.
---

# Braço de foto

Trabalhe em `sistema-redes/`. Bases: `estudos/17` (carrosséis e design), R10, R12 (tamanhos por rede), R14 (thumbnails). Mesma identidade visual do perfil em tudo (`identidade_foto` + `cores`).

## Peças
| Peça | Comando | Saída |
|---|---|---|
| Carrossel | skill `social-carrossel` (`carrossel spec.json --formato 4x5 9x16`) | PNG por slide + PDF (LinkedIn) |
| Post/stories | `post post.json --formatos 4x5 9x16 1x1 16x9 --perfil <id>` | `post_<formato>.png` (+ .html editável) |
| Capa de Reels/TikTok | `capa final.mp4 "Título com ==destaque==" --perfil <id> --rotulo "TEMA"` | `capa_reels.png` + `capa_grade.png` (prévia 3:4) |
| Thumbnail YouTube | `thumbnail video.mp4 "Até 5 palavras" --perfil <id> --rotulo "CDC art. 49"` | `thumbnail.jpg` 1280×720 + `thumbnail_mini.png` |
| Tratar foto | `foto tratar retrato.jpg --formatos 4x5 9x16 --perfil <id>` | enquadrada pelo rosto, cor do perfil |
| Recortar pessoa | `foto recortar retrato.jpg` | PNG com transparência |
| Anonimizar | `foto anonimizar print.png --caixas "0.1,0.2,0.3,0.05;…" --modo tarja` | nomes/CPF/rostos de terceiros ocultos |
| Print com fonte | `foto print manchete.png --fonte "G1" --data "08/10/2026" --perfil <id>` | print em moldura com fonte |
Tipos de post (`post.json`): `frase`, `manchete`, `dado`, `comunicado`, `evento`, `foto`, `pergunta` (campos na docstring de `redes/foto/post.py`).

## Regras de design (não negociáveis)
- **Uma ideia por peça**; post ≤ 30 palavras (detalhe vai na legenda); capa ≤ 8 palavras; thumbnail 1-5 palavras.
- Dado e notícia **com fonte e data**. Print: recorte só o essencial e **anonimize** dados pessoais (você olha a imagem e marca as caixas).
- Contraste ≥ 4,5:1 (o gerador avisa). Nada de banco de imagem genérico nem clipart.
- Stories: texto fora das zonas da interface (o gerador já respeita topo 270 px e base 380 px).
- Capa: sempre do vídeo **sem legenda queimada** (o sistema usa `base.mp4` automaticamente).

## Revisão (obrigatória)
Leia (Read) cada PNG gerado em tamanho real e a `capa_grade.png`/`thumbnail_mini.png`: texto legível no celular, nada cortado, rosto bem enquadrado, cores da identidade. Ajuste o JSON e gere de novo se preciso.

## Pelo gestor
Na rotina normal, crie a pauta com `--formato post|stories|carrossel --material spec.json` e rode `executar <pauta>`: o sistema gera as artes, ajusta para cada rede do perfil (Instagram, Facebook, LinkedIn, X, Threads, Pinterest, TikTok Modo Foto), escreve legendas, texto alternativo e o pacote.
