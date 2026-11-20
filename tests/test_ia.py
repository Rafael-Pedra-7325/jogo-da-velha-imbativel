import os
import sys
import random
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from jogo import Tabuleiro
from super_jogo import SuperTabuleiro
from ia import (
    melhor_jogada,
    analisar_jogadas,
    melhor_jogada_super,
    analisar_jogadas_super,
)
from app import app

IA = "O"
HUMANO = "X"


class MinimaxTestCase(unittest.TestCase):
    def test_ia_vence_quando_possivel(self):
        tabuleiro = Tabuleiro(list("OO       "))
        posicao = melhor_jogada(tabuleiro, IA, HUMANO)
        self.assertEqual(posicao, 2)

    def test_ia_bloqueia_vitoria_do_adversario(self):
        tabuleiro = Tabuleiro(list("XX       "))
        posicao = melhor_jogada(tabuleiro, IA, HUMANO)
        self.assertEqual(posicao, 2)

    def test_linha_vitoria_retorna_indices_corretos(self):
        tabuleiro = Tabuleiro(list("XXXOO    "))
        self.assertEqual(tabuleiro.linha_vitoria(), (0, 1, 2))
        self.assertEqual(tabuleiro.vencedor(), "X")

    def test_ia_nunca_perde_contra_jogadas_aleatorias(self):
        random.seed(42)

        for _ in range(30):
            tabuleiro = Tabuleiro()
            jogador_atual = HUMANO

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

    def test_analise_jogadas_retorna_telemetria(self):
        tabuleiro = Tabuleiro(list("X   O    "))
        resultado = analisar_jogadas(tabuleiro, HUMANO, IA)
        self.assertGreater(resultado["nos_avaliados"], 0)
        self.assertEqual(len(resultado["avaliacoes"]), 7)


class SuperJogoMCTSTestCase(unittest.TestCase):
    def test_direcionamento_de_sub_tabuleiro(self):
        tab = SuperTabuleiro()
        tab.jogar(0, 4, "X")
        self.assertEqual(tab.sub_ativo, 4)
        with self.assertRaises(ValueError):
            tab.jogar(1, 0, "O")

    def test_jogada_livre_quando_sub_alvo_ja_vencido(self):
        tab = SuperTabuleiro()
        # X vence o sub-tabuleiro 0
        tab.jogar(0, 0, "X")
        tab.jogar(0, 3, "O")
        tab.jogar(3, 0, "X")
        tab.jogar(0, 4, "O")
        tab.jogar(4, 0, "X")
        tab.jogar(0, 1, "X")
        tab.jogar(1, 0, "O")
        tab.jogar(0, 2, "X")  # X completa (0, 1, 2) no sub 0

        self.assertEqual(tab.sub_vencedores[0], "X")
        # O joga em qualquer sub aberto enviando para o sub 0 (já encerrado)
        tab.jogar(2, 0, "O")
        self.assertIsNone(tab.sub_ativo)

    def test_mcts_vence_macro_em_um_lance(self):
        celulas = [[" "] * 9 for _ in range(9)]
        celulas[0] = ["O", "O", "O", " ", " ", " ", " ", " ", " "]
        celulas[1] = ["O", "O", "O", " ", " ", " ", " ", " ", " "]
        celulas[2] = ["O", "O", " ", " ", " ", " ", " ", " ", " "]
        tab = SuperTabuleiro(celulas=celulas, sub_ativo=2)

        lance, detalhes = melhor_jogada_super(tab, "O", "X", retornar_detalhes=True)
        self.assertEqual(lance, (2, 2))
        self.assertEqual(detalhes["taxa_vitoria"], 100.0)

    def test_mcts_retorna_lance_valido_e_telemetria(self):
        tab = SuperTabuleiro()
        tab.jogar(4, 4, "X")
        lance, detalhes = melhor_jogada_super(
            tab, "O", "X", tempo_limite_s=0.08, retornar_detalhes=True
        )
        self.assertIn(lance, tab.jogadas_legais())
        self.assertGreater(detalhes["simulacoes"], 50)


class WebApiTestCase(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_pagina_principal_carrega(self):
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b"Jogo da Velha", resp.data)

    def test_api_jogada_responde_lance_valido(self):
        resp = self.client.post("/api/jogada", json={
            "celulas": list("X        "),
            "simbolo_ia": "O",
            "dificuldade": "imbativel",
        })
        self.assertEqual(resp.status_code, 200)
        dados = resp.get_json()
        self.assertEqual(dados["posicao"], 4)
        self.assertIn("telemetria", dados)

    def test_api_analisar_retorna_dica(self):
        resp = self.client.post("/api/analisar", json={
            "celulas": list("XX O O   "),
            "simbolo_jogador": "X",
        })
        self.assertEqual(resp.status_code, 200)
        dados = resp.get_json()
        self.assertEqual(dados["melhor_posicao"], 2)

    def test_api_super_jogada_e_analise(self):
        celulas = [[" "] * 9 for _ in range(9)]
        celulas[4][4] = "X"
        resp = self.client.post("/api/super/jogada", json={
            "celulas": celulas,
            "sub_ativo": 4,
            "simbolo_ia": "O",
            "dificuldade": "facil",
        })
        self.assertEqual(resp.status_code, 200)
        dados = resp.get_json()
        self.assertEqual(dados["lance"][0], 4)
        self.assertGreater(dados["telemetria"]["simulacoes"], 0)


if __name__ == "__main__":
    unittest.main()
