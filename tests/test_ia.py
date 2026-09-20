import os
import sys
import random
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from jogo import Tabuleiro
from ia import melhor_jogada

IA = "O"
HUMANO = "X"


class MinimaxTestCase(unittest.TestCase):
    def test_ia_vence_quando_possivel(self):
        # O joga em 0 e 1: se jogar em 2, vence.
        tabuleiro = Tabuleiro(list("OO       "))
        posicao = melhor_jogada(tabuleiro, IA, HUMANO)
        self.assertEqual(posicao, 2)

    def test_ia_bloqueia_vitoria_do_adversario(self):
        # X joga em 0 e 1: se não for bloqueado, X vence jogando em 2.
        tabuleiro = Tabuleiro(list("XX       "))
        posicao = melhor_jogada(tabuleiro, IA, HUMANO)
        self.assertEqual(posicao, 2)

    def test_ia_nunca_perde_contra_jogadas_aleatorias(self):
        random.seed(42)

        for _ in range(30):
            tabuleiro = Tabuleiro()
            jogador_atual = HUMANO  # humano (aleatório) sempre começa

            while not tabuleiro.jogo_terminou():
                if jogador_atual == HUMANO:
                    posicao = random.choice(tabuleiro.posicoes_livres())
                else:
                    posicao = melhor_jogada(tabuleiro, IA, HUMANO)

                tabuleiro.jogar(posicao, jogador_atual)
                jogador_atual = IA if jogador_atual == HUMANO else HUMANO

            self.assertNotEqual(
                tabuleiro.vencedor(), HUMANO,
                f"A IA perdeu uma partida! Tabuleiro final:\n{tabuleiro}"
            )

    def test_duas_ias_perfeitas_sempre_empatam(self):
        tabuleiro = Tabuleiro()
        jogador_atual = HUMANO

        while not tabuleiro.jogo_terminou():
            adversario = IA if jogador_atual == HUMANO else HUMANO
            posicao = melhor_jogada(tabuleiro, jogador_atual, adversario)
            tabuleiro.jogar(posicao, jogador_atual)
            jogador_atual = adversario

        self.assertIsNone(tabuleiro.vencedor())


if __name__ == "__main__":
    unittest.main()
