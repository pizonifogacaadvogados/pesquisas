---
name: social-planejamento
description: Skill-filha do gestor-redes para planejamento - cadastro de perfis (escritório, advogado, político, mandato), backlog de pautas por pilar de conteúdo, sugestão de pautas por nicho, calendário editorial semanal multi-rede (md, json e .ics para Google Agenda) e regras de datas (eleição, feriados). Use quando o usuário pedir pauta, ideias, calendário, cronograma de postagens, planejamento do mês ou configurar uma nova conta.
---

# Planejamento (perfis, pautas, calendário)

Trabalhe em `sistema-redes/`. Bases: `estudos/11` (algoritmos e horários), `12` (nichos), `17` (carrosséis), registro R12 (especificações por rede), R13 (calendário eleitoral).

## Perfil
`python3 -m redes perfil criar <id> --tipo advocacia|politico|juridico` cria `perfis/<id>.json` a partir do modelo. Campos que mudam tudo:
- `assinatura` (nome, cargo, **registro OAB**, handle) → lower third, legendas e assinatura obrigatória;
- `redes.<rede>.semana` → o que o calendário agenda (ex.: `"instagram": {"semana": {"reels": 3, "carrossel": 2, "post": 1, "stories": 5}}`);
- `horarios` (`seg-sex`, `sab`, `dom` ou o dia) · `pilares` (pesos somando 1) · `identidade_foto` e `cores` · `foto_autor` · `fundo_foto`;
- político: `candidato`, `cnpj_campanha`.
`perfil validar <id>` lista o que falta.

## Pautas
Status: ideia → roteiro → material → produzido → aprovado → publicado → medido.
```bash
python3 -m redes pauta sugerir <perfil>                 # esqueletos equilibrando os pilares
python3 -m redes pauta criar <perfil> "Tema" --formato reels --gancho "Você sabia que…?" \
   --material bruto.mp4 --srt bruto.srt --data 2026-10-20 --hora 19:00 --hashtags direitodoconsumidor cdc
python3 -m redes pauta criar <perfil> "Tema" --formato carrossel --material carrossel.json
python3 -m redes pauta editar p0003 --campos '{"legenda_corpo": "…", "titulo_capa": "…", "usa_ia": false}'
python3 -m redes pauta painel --perfil <perfil>
```
Escreva o **gancho** como o público fala (com a palavra-chave de busca). Formatos: reels, carrossel, post, stories, react, video_longo, documento.

## Calendário
`python3 -m redes calendario <perfil> --inicio 2026-10-12 --semanas 2 --saida planejamento/` → `calendario.md`, `.json`, `.ics`.
Regras embutidas: vídeo-âncora no horário nobre e repetido nas redes irmãs (TikTok +1 h, Shorts +2 h, Kwai, Facebook) no mesmo dia; carrossel do mesmo tema 2 dias depois; stories diários; LinkedIn de manhã em dias úteis; **perfil político: nada nos dias de eleição** (04/10 e 25/10/2026).
Espaços "(a definir)" = faltam pautas: sugira e crie.

## Boas práticas
- Feriados e datas do nicho (Dia do Consumidor 15/03, Dia do Advogado 11/08, mudanças de lei, prazos como IR) viram pautas com antecedência.
- Época eleitoral: veja `social-conformidade` (pré-campanha sem pedido de voto antes de 16/08; impulsionamento só até 01/10 e 22/10/2026).
- Revise o calendário com o usuário antes de pedir gravações.
