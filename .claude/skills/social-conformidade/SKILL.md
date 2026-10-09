---
name: social-conformidade
description: Skill de conformidade do sistema de redes (vídeo e foto) - semáforo automático (`python -m redes checar`) e checagem jurídica de vídeos, carrosséis, posts e legendas - direito autoral (Lei 9.610/98 art. 46, III), direito de imagem (Súmula 403 STJ), honra, Marco Civil (STF 2025), OAB (Provimento 205/2021 e Código de Ética art. 42), Justiça Eleitoral (Res. TSE 23.610 com 23.732/2024 e 23.755/2026), IA/deepfake, LGPD e termos do CapCut. Calendário eleitoral 2026 embutido (16/08, 01/10, 04/10, 22/10, 25/10). Use antes de produzir e antes de publicar qualquer peça, especialmente react e conteúdo político.
---

# Conformidade

Base: `sistema-redes/estudos/10-react.md` §8 (checklists), `05` e `12` (OAB/TSE), registros R04.12-R04.24, R06, R07.04. **Você sinaliza riscos; quem decide é o advogado responsável.** Em dúvida relevante, recomende consulta ao texto oficial (norma ou acórdão).

## 1. Camada automática (sempre roda no pacote; rode também à mão em roteiros)
```bash
python3 -m redes checar "texto da legenda ou roteiro" --perfil <id> [--data 2026-10-20] [--impulsionar] [--usa-ia]
python3 -m redes checar --arquivo roteiro.txt --perfil <id>
```
Saída 0 verde · 1 amarelo · 2 vermelho. Regras e fontes: `pesquisa/registro/R13-conformidade-automatica.md` e `redes/nucleo/conformidade.py`:
OAB (promessa de resultado, captação/preço/"consulta grátis", superlativos, "especialista", ostentação, caso de cliente) ·
TSE (pedido de voto antes de 16/08; dia da eleição; impulsionamento após 01/10 e 22/10/2026; IA na janela de 72 h/24 h; rótulo de IA; deepfake) ·
LGPD (CPF, CNPJ, processo CNJ, telefone, e-mail) · autoral (música sem licença, terceiro sem crédito) · limites de cada rede.
**A camada automática é a primeira barreira, não a decisão.** Ela não entende contexto (ironia, citação de terceiro, notícia). Leia sempre os itens e julgue.

## 2. Semáforo
- 🟢 **Verde:** pode seguir.
- 🟡 **Amarelo:** pode seguir com ajuste (diga qual).
- 🔴 **Vermelho:** não produzir ou não publicar sem decisão expressa do usuário.

## 3. Checklist humano (o que o código não vê)
**Direito autoral (react, trechos, música):** finalidade de crítica, estudo ou polêmica · trecho na medida justificada · autor e origem na tela · não substitui o original · música de terceiro fora · trechos de TV curtos e comentados.
**Imagem e honra:** pessoa pública em contexto público ou pessoa comum (desfocar) · sem escárnio nem intimidade · opinião ≠ imputação de fato (calúnia, difamação, injúria).
**Advocacia:** CED art. 42 (sem consulta habitual na mídia; **não debater causa de outro advogado**; dignidade; sem lista de clientes) · Prov. 205 (sem honorários, gratuidade, promessa de resultado, autoengrandecimento ou caso de cliente) · IA: Recomendação CFOAB 01/2024 (supervisão humana, sigilo).
**Política (2026):** nada sabidamente inverídico ou gravemente descontextualizado · data e fonte na tela · **não impulsionar negativo** · impulsionamento só pelo candidato/partido, com CPF/CNPJ · sem influenciador pago · **sem IA em rosto ou voz** (deepfake); qualquer IA rotulada; nada sintético novo 72h antes / 24h depois do pleito · sem campeonato de cortes pago · perfis de candidato fora da recomendação (o alcance vem de compartilhamento) · sátira é permitida (ADI 4451) dentro desses limites.
**Dados e ferramentas:** nada sigiloso de cliente no CapCut ou em IA de terceiros (termos do CapCut de 12/06/2025; LGPD; sigilo profissional).
**Plataforma:** sem marca d'água de outra rede; transformação real (originalidade do Instagram e do TikTok).

## Saída
Liste os itens 🟡/🔴 com: o problema, a regra (com a referência) e o ajuste sugerido. Registre em `plano.json` → `alertas`, se aplicável.
