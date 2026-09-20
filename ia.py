"""
Inteligência artificial do Jogo da Velha usando o algoritmo Minimax.
Joga com perfeição: nunca perde (empata contra outro jogador perfeito, vence
contra qualquer erro do adversário).
"""


def _avaliar(tabuleiro, simbolo_ia, simbolo_adversario, profundidade):
    vencedor = tabuleiro.vencedor()
    if vencedor == simbolo_ia:
        return 10 - profundidade
    if vencedor == simbolo_adversario:
        return profundidade - 10
    return 0


def minimax(tabuleiro, simbolo_atual, simbolo_ia, simbolo_adversario, profundidade=0):
    """Retorna a pontuação da melhor jogada possível a partir deste estado."""
    if tabuleiro.jogo_terminou():
        return _avaliar(tabuleiro, simbolo_ia, simbolo_adversario, profundidade)

    maximizando = simbolo_atual == simbolo_ia
    melhor_pontuacao = float("-inf") if maximizando else float("inf")
    proximo_simbolo = simbolo_adversario if maximizando else simbolo_ia

    for posicao in tabuleiro.posicoes_livres():
        copia = tabuleiro.copiar()
        copia.jogar(posicao, simbolo_atual)
        pontuacao = minimax(copia, proximo_simbolo, simbolo_ia, simbolo_adversario, profundidade + 1)

        if maximizando:
            melhor_pontuacao = max(melhor_pontuacao, pontuacao)
        else:
            melhor_pontuacao = min(melhor_pontuacao, pontuacao)

    return melhor_pontuacao


def melhor_jogada(tabuleiro, simbolo_ia, simbolo_adversario):
    """Retorna a posição (0-8) da melhor jogada disponível para a IA."""
    melhor_posicao = None
    melhor_pontuacao = float("-inf")

    for posicao in tabuleiro.posicoes_livres():
        copia = tabuleiro.copiar()
        copia.jogar(posicao, simbolo_ia)
        pontuacao = minimax(copia, simbolo_adversario, simbolo_ia, simbolo_adversario, profundidade=1)

        if pontuacao > melhor_pontuacao:
            melhor_pontuacao = pontuacao
            melhor_posicao = posicao

    return melhor_posicao
