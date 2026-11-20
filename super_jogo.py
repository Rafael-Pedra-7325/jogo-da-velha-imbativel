"""
Regras do Super Jogo da Velha (Ultimate Tic-Tac-Toe):
Tabuleiro 3x3 composto por 9 sub-tabuleiros 3x3 (81 casas no total).
A célula escolhida em um sub-tabuleiro determina em qual sub-tabuleiro o oponente deve jogar.
"""

from jogo import LINHAS_VITORIA


class SuperTabuleiro:
    def __init__(self, celulas=None, sub_ativo=None, ultimo_lance=None):
        if celulas is None:
            self.celulas = [[" "] * 9 for _ in range(9)]
        elif len(celulas) == 81 and all(isinstance(c, str) for c in celulas):
            self.celulas = [list(celulas[i * 9:(i + 1) * 9]) for i in range(9)]
        elif len(celulas) == 9 and all(isinstance(sub, list) and len(sub) == 9 for sub in celulas):
            self.celulas = [list(sub) for sub in celulas]
        else:
            raise ValueError("O Super Tabuleiro deve conter 9 sub-tabuleiros de 9 células (81 no total).")

        for sub in self.celulas:
            if any(c not in (" ", "X", "O") for c in sub):
                raise ValueError("Células devem conter apenas ' ', 'X' ou 'O'.")

        if sub_ativo is not None and (not isinstance(sub_ativo, int) or sub_ativo not in range(9)):
            raise ValueError("sub_ativo deve ser None ou um inteiro de 0 a 8.")

        self.sub_ativo = sub_ativo
        self.ultimo_lance = tuple(ultimo_lance) if ultimo_lance is not None else None
        self._recalcular_estado()

    def _recalcular_estado(self):
        self.sub_vencedores = [None] * 9
        self.sub_linhas_vitoria = [None] * 9
        self.sub_empates = [False] * 9
        self.sub_encerrados = [False] * 9

        for s in range(9):
            sub = self.celulas[s]
            linha_v = None
            for a, b, c in LINHAS_VITORIA:
                if sub[a] != " " and sub[a] == sub[b] == sub[c]:
                    linha_v = (a, b, c)
                    break

            if linha_v is not None:
                self.sub_linhas_vitoria[s] = linha_v
                self.sub_vencedores[s] = sub[linha_v[0]]
                self.sub_encerrados[s] = True
            elif " " not in sub:
                self.sub_empates[s] = True
                self.sub_encerrados[s] = True

        # Se sub_ativo apontar para um sub-tabuleiro já encerrado, libera jogada em qualquer sub-tabuleiro aberto
        if self.sub_ativo is not None and self.sub_encerrados[self.sub_ativo]:
            self.sub_ativo = None

    def copiar(self):
        return SuperTabuleiro(
            celulas=[sub.copy() for sub in self.celulas],
            sub_ativo=self.sub_ativo,
            ultimo_lance=self.ultimo_lance,
        )

    def linha_vitoria(self):
        """Retorna a tupla (a, b, c) dos sub-tabuleiros vencedores no macro-tabuleiro, ou None."""
        for a, b, c in LINHAS_VITORIA:
            va = self.sub_vencedores[a]
            if va is not None and va == self.sub_vencedores[b] == self.sub_vencedores[c]:
                return (a, b, c)
        return None

    def vencedor(self):
        linha = self.linha_vitoria()
        return self.sub_vencedores[linha[0]] if linha else None

    def empate(self):
        return self.vencedor() is None and all(self.sub_encerrados)

    def jogo_terminou(self):
        return self.vencedor() is not None or all(self.sub_encerrados)

    def jogadas_legais(self):
        """Retorna lista de tuplas (sub_tabuleiro, celula) válidas no estado atual."""
        if self.jogo_terminou():
            return []

        if self.sub_ativo is not None and not self.sub_encerrados[self.sub_ativo]:
            subs = [self.sub_ativo]
        else:
            subs = [s for s in range(9) if not self.sub_encerrados[s]]

        legais = []
        for s in subs:
            sub = self.celulas[s]
            for c, val in enumerate(sub):
                if val == " ":
                    legais.append((s, c))
        return legais

    def jogar(self, sub_tabuleiro, celula, simbolo):
        if simbolo not in ("X", "O"):
            raise ValueError(f"Símbolo inválido: {simbolo}. Use 'X' ou 'O'.")
        if not isinstance(sub_tabuleiro, int) or sub_tabuleiro not in range(9):
            raise ValueError(f"Sub-tabuleiro inválido: {sub_tabuleiro}. Use um inteiro de 0 a 8.")
        if not isinstance(celula, int) or celula not in range(9):
            raise ValueError(f"Célula inválida: {celula}. Use um inteiro de 0 a 8.")
        if self.jogo_terminou():
            raise ValueError("A partida já terminou.")
        if self.sub_ativo is not None and sub_tabuleiro != self.sub_ativo:
            raise ValueError(f"Jogada obrigatória no sub-tabuleiro {self.sub_ativo}.")
        if self.sub_encerrados[sub_tabuleiro]:
            raise ValueError(f"O sub-tabuleiro {sub_tabuleiro} já foi encerrado.")
        if self.celulas[sub_tabuleiro][celula] != " ":
            raise ValueError(f"A casa ({sub_tabuleiro}, {celula}) já está ocupada.")

        self.celulas[sub_tabuleiro][celula] = simbolo
        self.ultimo_lance = (sub_tabuleiro, celula)
        self._recalcular_estado()

        # O próximo jogador é enviado ao sub-tabuleiro correspondente à célula jogada
        if self.jogo_terminou() or self.sub_encerrados[celula]:
            self.sub_ativo = None
        else:
            self.sub_ativo = celula

    def para_dict(self):
        linha = self.linha_vitoria()
        vencedor = self.sub_vencedores[linha[0]] if linha else None
        terminou = vencedor is not None or all(self.sub_encerrados)
        return {
            "celulas": self.celulas,
            "sub_ativo": None if terminou else self.sub_ativo,
            "sub_vencedores": self.sub_vencedores,
            "sub_linhas_vitoria": [list(lv) if lv else None for lv in self.sub_linhas_vitoria],
            "sub_empates": self.sub_empates,
            "sub_encerrados": self.sub_encerrados,
            "vencedor": vencedor,
            "linha_vitoria": list(linha) if linha else None,
            "empate": vencedor is None and all(self.sub_encerrados),
            "terminou": terminou,
            "ultimo_lance": list(self.ultimo_lance) if self.ultimo_lance else None,
            "jogadas_legais": [list(j) for j in self.jogadas_legais()],
        }
