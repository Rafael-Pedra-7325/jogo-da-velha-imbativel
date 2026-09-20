"""
Regras do Jogo da Velha: representação do tabuleiro e verificação de vitória/empate.
"""

LINHAS_VITORIA = [
    (0, 1, 2), (3, 4, 5), (6, 7, 8),  # linhas
    (0, 3, 6), (1, 4, 7), (2, 5, 8),  # colunas
    (0, 4, 8), (2, 4, 6),             # diagonais
]


class Tabuleiro:
    def __init__(self, celulas=None):
        self.celulas = celulas if celulas is not None else [" "] * 9

    def copiar(self):
        return Tabuleiro(self.celulas.copy())

    def jogar(self, posicao, simbolo):
        if self.celulas[posicao] != " ":
            raise ValueError(f"Posição {posicao} já está ocupada.")
        self.celulas[posicao] = simbolo

    def posicoes_livres(self):
        return [i for i, valor in enumerate(self.celulas) if valor == " "]

    def vencedor(self):
        for a, b, c in LINHAS_VITORIA:
            if self.celulas[a] != " " and self.celulas[a] == self.celulas[b] == self.celulas[c]:
                return self.celulas[a]
        return None

    def cheio(self):
        return " " not in self.celulas

    def jogo_terminou(self):
        return self.vencedor() is not None or self.cheio()

    def __str__(self):
        linhas = []
        for i in range(0, 9, 3):
            linhas.append(" | ".join(self.celulas[i:i + 3]))
        return "\n---------\n".join(linhas)
