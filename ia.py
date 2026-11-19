"""
Inteligência Artificial do Jogo da Velha com Minimax + Poda Alfa-Beta.
Suporta múltiplos níveis de dificuldade, telemetria de nós avaliados e modo Raio-X.
"""

import random
import time

ORDEM_PREFERENCIA = (4, 0, 2, 6, 8, 1, 3, 5, 7)


def _avaliar(tabuleiro, simbolo_ia, simbolo_adversario, profundidade):
    vencedor = tabuleiro.vencedor()
    if vencedor == simbolo_ia:
        return 10 - profundidade
    if vencedor == simbolo_adversario:
        return profundidade - 10
    return 0


def minimax(
    tabuleiro,
    simbolo_atual,
    simbolo_ia,
    simbolo_adversario,
    profundidade=0,
    alfa=float("-inf"),
    beta=float("inf"),
    metricas=None,
):
    """Retorna a pontuação da melhor jogada possível usando Minimax com Poda Alfa-Beta."""
    if metricas is not None:
        metricas["nos"] += 1

    if tabuleiro.jogo_terminou():
        return _avaliar(tabuleiro, simbolo_ia, simbolo_adversario, profundidade)

    maximizando = simbolo_atual == simbolo_ia
    proximo_simbolo = simbolo_adversario if maximizando else simbolo_ia
    livres = [p for p in ORDEM_PREFERENCIA if p in tabuleiro.posicoes_livres()]

    if maximizando:
        melhor_pontuacao = float("-inf")
        for posicao in livres:
            copia = tabuleiro.copiar()
            copia.jogar(posicao, simbolo_atual)
            pontuacao = minimax(
                copia, proximo_simbolo, simbolo_ia, simbolo_adversario,
                profundidade + 1, alfa, beta, metricas
            )
            melhor_pontuacao = max(melhor_pontuacao, pontuacao)
            alfa = max(alfa, melhor_pontuacao)
            if beta <= alfa:
                break
        return melhor_pontuacao
    else:
        melhor_pontuacao = float("inf")
        for posicao in livres:
            copia = tabuleiro.copiar()
            copia.jogar(posicao, simbolo_atual)
            pontuacao = minimax(
                copia, proximo_simbolo, simbolo_ia, simbolo_adversario,
                profundidade + 1, alfa, beta, metricas
            )
            melhor_pontuacao = min(melhor_pontuacao, pontuacao)
            beta = min(beta, melhor_pontuacao)
            if beta <= alfa:
                break
        return melhor_pontuacao


def analisar_jogadas(tabuleiro, simbolo_jogador, simbolo_oponente):
    """
    Avalia todas as posições livres para `simbolo_jogador` e retorna:
    - avaliacoes: lista de dicts com posicao, pontuacao e desfecho ('vitoria', 'empate', 'derrota')
    - nos_avaliados: total de estados simulados
    - tempo_ms: tempo de cálculo em milissegundos
    """
    inicio = time.perf_counter()
    metricas = {"nos": 0}
    avaliacoes = []

    livres = [p for p in ORDEM_PREFERENCIA if p in tabuleiro.posicoes_livres()]

    for posicao in livres:
        copia = tabuleiro.copiar()
        copia.jogar(posicao, simbolo_jogador)
        pontuacao = minimax(
            copia, simbolo_oponente, simbolo_jogador, simbolo_oponente,
            profundidade=1, metricas=metricas
        )
        if pontuacao > 0:
            desfecho = "vitoria"
        elif pontuacao < 0:
            desfecho = "derrota"
        else:
            desfecho = "empate"

        avaliacoes.append({
            "posicao": posicao,
            "pontuacao": pontuacao,
            "desfecho": desfecho,
        })

    avaliacoes.sort(key=lambda item: item["pontuacao"], reverse=True)
    tempo_ms = round((time.perf_counter() - inicio) * 1000, 2)

    return {
        "avaliacoes": avaliacoes,
        "nos_avaliados": metricas["nos"],
        "tempo_ms": tempo_ms,
    }


def melhor_jogada(tabuleiro, simbolo_ia, simbolo_adversario, dificuldade="imbativel", retornar_detalhes=False):
    """
    Retorna a posição (0-8) da jogada escolhida pela IA conforme a dificuldade:
    - 'facil': joga aleatoriamente na maior parte do tempo
    - 'medio': alterna entre jogadas ótimas e subótimas
    - 'imbativel': usa Minimax com Poda Alfa-Beta (nunca perde)
    """
    livres = tabuleiro.posicoes_livres()
    if not livres:
        return (None, {}) if retornar_detalhes else None

    analise = analisar_jogadas(tabuleiro, simbolo_ia, simbolo_adversario)
    avaliacoes = analise["avaliacoes"]

    if dificuldade == "facil" and random.random() < 0.72:
        escolhida = random.choice(livres)
        motivo = "Jogada exploratória (Modo Aprendiz)"
    elif dificuldade == "medio" and random.random() < 0.45 and len(avaliacoes) > 1:
        candidatas = avaliacoes[1:]
        escolhida = random.choice(candidatas)["posicao"]
        motivo = "Jogada equilibrada (Modo Desafiante)"
    else:
        melhor_pontuacao = avaliacoes[0]["pontuacao"]
        melhores = [a["posicao"] for a in avaliacoes if a["pontuacao"] == melhor_pontuacao]
        escolhida = melhores[0]
        if melhor_pontuacao > 0:
            passos = 10 - melhor_pontuacao
            motivo = f"Vitória forçada em {passos} lance(s)"
        elif melhor_pontuacao < 0:
            motivo = "Defesa máxima (adversário tem vantagem)"
        else:
            motivo = "Equilíbrio perfeito (empate garantido)"

    if retornar_detalhes:
        detalhes = {
            "posicao": escolhida,
            "nos_avaliados": analise["nos_avaliados"],
            "tempo_ms": analise["tempo_ms"],
            "motivo": motivo,
            "avaliacoes": avaliacoes,
        }
        return escolhida, detalhes

    return escolhida
