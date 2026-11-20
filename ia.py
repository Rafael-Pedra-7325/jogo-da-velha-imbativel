"""
Inteligência Artificial do Jogo da Velha:
- Modo Clássico (3x3): Minimax com Poda Alfa-Beta (matematicamente invencível).
- Modo Super Jogo da Velha (9x9): Monte Carlo Tree Search (MCTS + UCB1) com bitmasks
  e simulações táticas semi-guiadas (milhares de simulações por segundo).
"""

import math
import random
import time

ORDEM_PREFERENCIA = (4, 0, 2, 6, 8, 1, 3, 5, 7)


# ==============================================================================
# 1. MOTOR CLÁSSICO (3x3) — MINIMAX + PODA ALFA-BETA
# ==============================================================================

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
    """Avalia todas as posições livres do tabuleiro 3x3 para `simbolo_jogador`."""
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
    """Retorna a posição (0-8) da jogada escolhida pela IA no modo clássico."""
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


# ==============================================================================
# 2. MOTOR SUPER JOGO DA VELHA (9x9) — MCTS (MONTE CARLO TREE SEARCH + BITMASKS)
# ==============================================================================

_WIN_MASKS = (
    0b000000111,  # 0, 1, 2
    0b000111000,  # 3, 4, 5
    0b111000000,  # 6, 7, 8
    0b001001001,  # 0, 3, 6
    0b010010010,  # 1, 4, 7
    0b100100100,  # 2, 5, 8
    0b100010001,  # 0, 4, 8
    0b001010100,  # 2, 4, 6
)
_FULL_MASK = 0b111111111

# Tabelas pré-computadas para todas as 512 combinações possíveis de um tabuleiro 3x3
_IS_WIN = tuple(any((m & w) == w for w in _WIN_MASKS) for m in range(512))
_FREE_CELLS = tuple(tuple(c for c in range(9) if not (occ & (1 << c))) for occ in range(512))
_THREAT_CELLS = [0] * 512
for _m in range(512):
    _t = 0
    for _c in range(9):
        _bit = 1 << _c
        if not (_m & _bit) and _IS_WIN[_m | _bit]:
            _t |= _bit
    _THREAT_CELLS[_m] = _t
_THREAT_CELLS = tuple(_THREAT_CELLS)


class _EstadoMCTS:
    """Representação ultraleve via bitmasks inteiros para milhares de rollouts/seg."""
    __slots__ = ("xm", "om", "mx", "mo", "mc", "active", "turn", "winner")

    def __init__(self, xm, om, mx, mo, mc, active, turn, winner=None):
        self.xm = xm
        self.om = om
        self.mx = mx
        self.mo = mo
        self.mc = mc
        self.active = active  # -1 = livre, 0..8 = sub-tabuleiro obrigatório
        self.turn = turn      # 0 = X, 1 = O
        self.winner = winner  # None = em andamento, 0 = X, 1 = O, 2 = empate

    @classmethod
    def from_super_tabuleiro(cls, tab, turno_simbolo):
        xm = [0] * 9
        om = [0] * 9
        mx = 0
        mo = 0
        mc = 0

        for s in range(9):
            sub = tab.celulas[s]
            bx = 0
            bo = 0
            for c, val in enumerate(sub):
                if val == "X":
                    bx |= (1 << c)
                elif val == "O":
                    bo |= (1 << c)
            xm[s] = bx
            om[s] = bo
            if _IS_WIN[bx]:
                mx |= (1 << s)
                mc |= (1 << s)
            elif _IS_WIN[bo]:
                mo |= (1 << s)
                mc |= (1 << s)
            elif (bx | bo) == _FULL_MASK:
                mc |= (1 << s)

        winner = None
        if _IS_WIN[mx]:
            winner = 0
        elif _IS_WIN[mo]:
            winner = 1
        elif mc == _FULL_MASK:
            winner = 2

        active = -1 if tab.sub_ativo is None or (mc & (1 << tab.sub_ativo)) else tab.sub_ativo
        turn = 0 if turno_simbolo == "X" else 1
        return cls(xm, om, mx, mo, mc, active, turn, winner)

    def clone(self):
        return _EstadoMCTS(
            self.xm.copy(),
            self.om.copy(),
            self.mx,
            self.mo,
            self.mc,
            self.active,
            self.turn,
            self.winner,
        )

    def legal_moves(self):
        if self.winner is not None:
            return []
        if self.active != -1 and not (self.mc & (1 << self.active)):
            s = self.active
            occ = self.xm[s] | self.om[s]
            return [(s, c) for c in _FREE_CELLS[occ]]

        moves = []
        for s in _FREE_CELLS[self.mc]:
            occ = self.xm[s] | self.om[s]
            for c in _FREE_CELLS[occ]:
                moves.append((s, c))
        return moves

    def apply_move(self, sub, cell):
        bit = 1 << cell
        if self.turn == 0:
            nm = self.xm[sub] | bit
            self.xm[sub] = nm
            if _IS_WIN[nm]:
                self.mx |= (1 << sub)
                self.mc |= (1 << sub)
                if _IS_WIN[self.mx]:
                    self.winner = 0
            elif (nm | self.om[sub]) == _FULL_MASK:
                self.mc |= (1 << sub)
        else:
            nm = self.om[sub] | bit
            self.om[sub] = nm
            if _IS_WIN[nm]:
                self.mo |= (1 << sub)
                self.mc |= (1 << sub)
                if _IS_WIN[self.mo]:
                    self.winner = 1
            elif (nm | self.xm[sub]) == _FULL_MASK:
                self.mc |= (1 << sub)

        if self.winner is None and self.mc == _FULL_MASK:
            self.winner = 2

        self.active = -1 if (self.winner is not None or (self.mc & (1 << cell))) else cell
        self.turn ^= 1

    def rollout(self):
        """Executa uma partida simulada rápida com heurística tática local."""
        if self.winner is not None:
            return self.winner

        xm = self.xm.copy()
        om = self.om.copy()
        mx = self.mx
        mo = self.mo
        mc = self.mc
        active = self.active
        turn = self.turn

        rng = random.random
        randbelow = random._inst._randbelow
        is_win = _IS_WIN
        free_cells = _FREE_CELLS
        threats = _THREAT_CELLS
        full = _FULL_MASK

        while True:
            if active != -1 and not (mc & (1 << active)):
                sub = active
            else:
                open_subs = free_cells[mc]
                if not open_subs:
                    return 2
                sub = open_subs[randbelow(len(open_subs))]

            occ = xm[sub] | om[sub]
            free = free_cells[occ]
            if not free:
                mc |= (1 << sub)
                active = -1
                continue

            # Política tática semi-guiada (75%): prioriza ganhar ou bloquear no sub-tabuleiro
            if rng() < 0.75:
                my_m = xm[sub] if turn == 0 else om[sub]
                op_m = om[sub] if turn == 0 else xm[sub]
                win_bits = threats[my_m] & ~occ
                if win_bits:
                    lsb = win_bits & -win_bits
                    cell = lsb.bit_length() - 1
                else:
                    blk_bits = threats[op_m] & ~occ
                    if blk_bits:
                        lsb = blk_bits & -blk_bits
                        cell = lsb.bit_length() - 1
                    else:
                        cell = free[randbelow(len(free))]
            else:
                cell = free[randbelow(len(free))]

            bit = 1 << cell
            if turn == 0:
                nm = xm[sub] | bit
                xm[sub] = nm
                if is_win[nm]:
                    mx |= (1 << sub)
                    mc |= (1 << sub)
                    if is_win[mx]:
                        return 0
                elif (nm | om[sub]) == full:
                    mc |= (1 << sub)
            else:
                nm = om[sub] | bit
                om[sub] = nm
                if is_win[nm]:
                    mo |= (1 << sub)
                    mc |= (1 << sub)
                    if is_win[mo]:
                        return 1
                elif (nm | xm[sub]) == full:
                    mc |= (1 << sub)

            if mc == full:
                return 2

            active = -1 if (mc & (1 << cell)) else cell
            turn ^= 1


class _NoMCTS:
    __slots__ = ("pai", "lance", "jogador", "filhos", "nao_explorados", "visitas", "vitorias")

    def __init__(self, estado, pai=None, lance=None, jogador=None):
        self.pai = pai
        self.lance = lance
        self.jogador = jogador  # 0 (X) ou 1 (O) que realizou `lance` para chegar aqui
        self.filhos = []
        self.nao_explorados = estado.legal_moves()
        random.shuffle(self.nao_explorados)
        self.visitas = 0
        self.vitorias = 0.0

    def selecionar_filho_ucb1(self, c=1.41):
        log_pai = math.log(self.visitas)
        melhor_valor = float("-inf")
        melhor_filho = None
        for f in self.filhos:
            taxa = f.vitorias / f.visitas
            exploracao = c * math.sqrt(log_pai / f.visitas)
            ucb = taxa + exploracao
            if ucb > melhor_valor:
                melhor_valor = ucb
                melhor_filho = f
        return melhor_filho


def _executar_mcts(tabuleiro, simbolo_ia, tempo_limite_s=0.85, max_simulacoes=None):
    estado_raiz = _EstadoMCTS.from_super_tabuleiro(tabuleiro, simbolo_ia)
    legais = estado_raiz.legal_moves()
    if not legais:
        return [], 0, 0.0

    inicio = time.perf_counter()
    raiz = _NoMCTS(estado_raiz)
    simulacoes = 0

    while True:
        if max_simulacoes is not None and simulacoes >= max_simulacoes:
            break
        if (simulacoes & 31) == 0 and (time.perf_counter() - inicio) >= tempo_limite_s and simulacoes > 0:
            break

        no = raiz
        estado = estado_raiz.clone()

        # 1. Seleção (UCB1)
        while not no.nao_explorados and no.filhos:
            no = no.selecionar_filho_ucb1()
            estado.apply_move(no.lance[0], no.lance[1])

        # 2. Expansão
        if no.nao_explorados and estado.winner is None:
            lance = no.nao_explorados.pop()
            jogador_lance = estado.turn
            estado.apply_move(lance[0], lance[1])
            filho = _NoMCTS(estado, pai=no, lance=lance, jogador=jogador_lance)
            no.filhos.append(filho)
            no = filho

        # 3. Simulação (Rollout tático)
        vencedor = estado.rollout()
        simulacoes += 1

        # 4. Retropropagação
        while no is not None:
            no.visitas += 1
            if no.jogador is not None:
                if vencedor == no.jogador:
                    no.vitorias += 1.0
                elif vencedor == 2:
                    no.vitorias += 0.5
            no = no.pai

    tempo_ms = round((time.perf_counter() - inicio) * 1000, 2)

    avaliacoes = []
    for f in raiz.filhos:
        taxa = round((f.vitorias / f.visitas) * 100, 1) if f.visitas > 0 else 50.0
        if taxa >= 58.0:
            desfecho = "vitoria"
        elif taxa <= 42.0:
            desfecho = "derrota"
        else:
            desfecho = "empate"

        avaliacoes.append({
            "sub_tabuleiro": f.lance[0],
            "celula": f.lance[1],
            "visitas": f.visitas,
            "taxa_vitoria": taxa,
            "desfecho": desfecho,
        })

    avaliacoes.sort(key=lambda item: (item["visitas"], item["taxa_vitoria"]), reverse=True)
    return avaliacoes, simulacoes, tempo_ms


def analisar_jogadas_super(tabuleiro, simbolo_jogador, simbolo_oponente, tempo_limite_s=0.45):
    """Analisa as jogadas legais do Super Tabuleiro via MCTS para Raio-X e Dica."""
    avaliacoes, simulacoes, tempo_ms = _executar_mcts(
        tabuleiro, simbolo_jogador, tempo_limite_s=tempo_limite_s
    )
    melhor = avaliacoes[0] if avaliacoes else None
    return {
        "avaliacoes": avaliacoes,
        "melhor_lance": [melhor["sub_tabuleiro"], melhor["celula"]] if melhor else None,
        "simulacoes": simulacoes,
        "nos_avaliados": simulacoes,
        "tempo_ms": tempo_ms,
    }


def melhor_jogada_super(
    tabuleiro,
    simbolo_ia,
    simbolo_adversario,
    dificuldade="imbativel",
    tempo_limite_s=None,
    max_simulacoes=None,
    retornar_detalhes=False,
):
    """
    Escolhe a melhor jogada (sub_tabuleiro, celula) no Super Jogo da Velha usando MCTS.
    """
    legais = tabuleiro.jogadas_legais()
    if not legais:
        return (None, {}) if retornar_detalhes else None

    # Atalho tático imediato: vitória direta no macro-tabuleiro em 1 lance
    for sub, cel in legais:
        copia = tabuleiro.copiar()
        copia.jogar(sub, cel, simbolo_ia)
        if copia.vencedor() == simbolo_ia:
            lance_vitoria = (sub, cel)
            if retornar_detalhes:
                return lance_vitoria, {
                    "lance": [sub, cel],
                    "simulacoes": 1,
                    "nos_avaliados": 1,
                    "tempo_ms": 0.05,
                    "taxa_vitoria": 100.0,
                    "motivo": "Vitória imediata no macro-tabuleiro!",
                    "avaliacoes": [{
                        "sub_tabuleiro": sub,
                        "celula": cel,
                        "visitas": 1,
                        "taxa_vitoria": 100.0,
                        "desfecho": "vitoria",
                    }],
                }
            return lance_vitoria

    orcamentos = {
        "facil": 0.10,
        "medio": 0.35,
        "imbativel": 0.90,
    }
    orcamento = tempo_limite_s if tempo_limite_s is not None else orcamentos.get(dificuldade, 0.90)

    avaliacoes, simulacoes, tempo_ms = _executar_mcts(
        tabuleiro,
        simbolo_ia,
        tempo_limite_s=orcamento,
        max_simulacoes=max_simulacoes,
    )

    if not avaliacoes:
        escolhido_item = {
            "sub_tabuleiro": legais[0][0],
            "celula": legais[0][1],
            "visitas": 0,
            "taxa_vitoria": 50.0,
            "desfecho": "empate",
        }
    elif dificuldade == "facil" and len(avaliacoes) > 1 and random.random() < 0.45:
        escolhido_item = random.choice(avaliacoes[:min(4, len(avaliacoes))])
    elif dificuldade == "medio" and len(avaliacoes) > 1 and random.random() < 0.25:
        escolhido_item = random.choice(avaliacoes[:min(2, len(avaliacoes))])
    else:
        escolhido_item = avaliacoes[0]

    lance = (escolhido_item["sub_tabuleiro"], escolhido_item["celula"])
    taxa = escolhido_item["taxa_vitoria"]

    if retornar_detalhes:
        detalhes = {
            "lance": [lance[0], lance[1]],
            "simulacoes": simulacoes,
            "nos_avaliados": simulacoes,
            "tempo_ms": tempo_ms,
            "taxa_vitoria": taxa,
            "motivo": f"MCTS UCB1: {taxa}% de vitórias em {simulacoes:,} simulações".replace(",", "."),
            "avaliacoes": avaliacoes,
        }
        return lance, detalhes

    return lance
