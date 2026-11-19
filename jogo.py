"""
Regras do Jogo da Velha: representação do tabuleiro, validação e verificação de vitória/empate.
"""

LINHAS_VITORIA = [
    (0, 1, 2), (3, 4, 5), (6, 7, 8),  # linhas
    (0, 3, 6), (1, 4, 7), (2, 5, 8),  # colunas
    (0, 4, 8), (2, 4, 6),             # diagonais
]


class Tabuleiro:
    def __init__(self, celulas=None):
        if celulas is not None:
            if len(celulas) != 9:
                raise ValueError("O tabuleiro deve conter exatamente 9 células.")
            self.celulas = list(celulas)
        else:
            self.celulas = [" "] * 9

    def copiar(self):
        return Tabuleiro(self.celulas.copy())

    def jogar(self, posicao, simbolo):
        if simbolo not in ("X", "O"):
            raise ValueError(f"Símbolo inválido: {simbolo}. Use 'X' ou 'O'.")
        if not isinstance(posicao, int) or posicao not in range(9):
            raise ValueError(f"Posição inválida: {posicao}. Use um inteiro de 0 a 8.")
        if self.celulas[posicao] != " ":
            raise ValueError(f"Posição {posicao} já está ocupada.")
        self.celulas[posicao] = simbolo

    def posicoes_livres(self):
        return [i for i, valor in enumerate(self.celulas) if valor == " "]

    def linha_vitoria(self):
        """Retorna a tupla (a, b, c) da linha vencedora ou None se ainda não houver vencedor."""
        for a, b, c in LINHAS_VITORIA:
            if self.celulas[a] != " " and self.celulas[a] == self.celulas[b] == self.celulas[c]:
                return (a, b, c)
        return None

    def vencedor(self):
        linha = self.linha_vitoria()
        return self.celulas[linha[0]] if linha else None

    def cheio(self):
        return " " not in self.celulas

    def jogo_terminou(self):
        return self.vencedor() is not None or self.cheio()

    def para_dict(self):
        linha = self.linha_vitoria()
        vencedor = self.celulas[linha[0]] if linha else None
        return {
            "celulas": self.celulas,
            "vencedor": vencedor,
            "linha_vitoria": list(linha) if linha else None,
            "empate": vencedor is None and self.cheio(),
            "terminou": vencedor is not None or self.cheio(),
            "posicoes_livres": self.posicoes_livres(),
        }

    def __str__(self):
        linhas = []
        for i in range(0, 9, 3):
            linhas.append(" | ".join(self.celulas[i:i + 3]))
        return "\n---------\n".join(linhas)
