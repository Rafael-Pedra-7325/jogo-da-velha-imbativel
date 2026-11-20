"""
Servidor Web Flask para o Jogo da Velha Imbatível.
Suporta Modo Clássico (Minimax + Alfa-Beta) e Super Jogo da Velha (MCTS).
"""

import os
from flask import Flask, jsonify, render_template, request
from jogo import Tabuleiro
from super_jogo import SuperTabuleiro
from ia import (
    melhor_jogada,
    analisar_jogadas,
    melhor_jogada_super,
    analisar_jogadas_super,
)

app = Flask(__name__)

DIFICULDADES_VALIDAS = {"facil", "medio", "imbativel"}
SIMBOLOS_VALIDOS = {"X", "O"}


def _validar_celulas(celulas):
    if not isinstance(celulas, list) or len(celulas) != 9:
        return False
    return all(c in (" ", "X", "O") for c in celulas)


def _construir_super_tabuleiro(dados):
    celulas = dados.get("celulas")
    sub_ativo = dados.get("sub_ativo", None)
    ultimo_lance = dados.get("ultimo_lance", None)

    if celulas is None:
        return SuperTabuleiro(sub_ativo=sub_ativo, ultimo_lance=ultimo_lance)

    return SuperTabuleiro(celulas=celulas, sub_ativo=sub_ativo, ultimo_lance=ultimo_lance)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/health")
def health():
    return jsonify({
        "status": "ok",
        "engines": ["minimax-alpha-beta", "mcts-ucb1"],
    })


# ==============================================================================
# ROTAS MODO CLÁSSICO (3x3)
# ==============================================================================

@app.route("/api/jogada", methods=["POST"])
def api_jogada():
    dados = request.get_json(silent=True) or {}
    celulas = dados.get("celulas", [" "] * 9)
    simbolo_ia = dados.get("simbolo_ia", "O")
    dificuldade = dados.get("dificuldade", "imbativel")

    if not _validar_celulas(celulas):
        return jsonify({"erro": "Tabuleiro inválido. Envie uma lista com 9 células."}), 400
    if simbolo_ia not in SIMBOLOS_VALIDOS:
        return jsonify({"erro": "Símbolo da IA inválido. Use 'X' ou 'O'."}), 400
    if dificuldade not in DIFICULDADES_VALIDAS:
        dificuldade = "imbativel"

    simbolo_humano = "X" if simbolo_ia == "O" else "O"
    tabuleiro = Tabuleiro(celulas)

    if tabuleiro.jogo_terminou():
        return jsonify({
            "posicao": None,
            "tabuleiro": tabuleiro.para_dict(),
            "telemetria": None,
        })

    posicao, detalhes = melhor_jogada(
        tabuleiro,
        simbolo_ia,
        simbolo_humano,
        dificuldade=dificuldade,
        retornar_detalhes=True,
    )

    if posicao is not None:
        tabuleiro.jogar(posicao, simbolo_ia)

    return jsonify({
        "posicao": posicao,
        "tabuleiro": tabuleiro.para_dict(),
        "telemetria": {
            "nos_avaliados": detalhes.get("nos_avaliados", 0),
            "tempo_ms": detalhes.get("tempo_ms", 0),
            "motivo": detalhes.get("motivo", ""),
            "dificuldade": dificuldade,
        },
    })


@app.route("/api/analisar", methods=["POST"])
def api_analisar():
    dados = request.get_json(silent=True) or {}
    celulas = dados.get("celulas", [" "] * 9)
    simbolo_jogador = dados.get("simbolo_jogador", "X")

    if not _validar_celulas(celulas):
        return jsonify({"erro": "Tabuleiro inválido."}), 400
    if simbolo_jogador not in SIMBOLOS_VALIDOS:
        return jsonify({"erro": "Símbolo inválido."}), 400

    simbolo_oponente = "O" if simbolo_jogador == "X" else "X"
    tabuleiro = Tabuleiro(celulas)

    if tabuleiro.jogo_terminou():
        return jsonify({
            "avaliacoes": [],
            "melhor_posicao": None,
            "nos_avaliados": 0,
            "tempo_ms": 0,
        })

    resultado = analisar_jogadas(tabuleiro, simbolo_jogador, simbolo_oponente)
    melhor_posicao = resultado["avaliacoes"][0]["posicao"] if resultado["avaliacoes"] else None

    return jsonify({
        "avaliacoes": resultado["avaliacoes"],
        "melhor_posicao": melhor_posicao,
        "nos_avaliados": resultado["nos_avaliados"],
        "tempo_ms": resultado["tempo_ms"],
    })


# ==============================================================================
# ROTAS SUPER JOGO DA VELHA (9x9 — ULTIMATE TIC-TAC-TOE)
# ==============================================================================

@app.route("/api/super/jogada", methods=["POST"])
def api_super_jogada():
    dados = request.get_json(silent=True) or {}
    simbolo_ia = dados.get("simbolo_ia", "O")
    dificuldade = dados.get("dificuldade", "imbativel")

    if simbolo_ia not in SIMBOLOS_VALIDOS:
        return jsonify({"erro": "Símbolo da IA inválido. Use 'X' ou 'O'."}), 400
    if dificuldade not in DIFICULDADES_VALIDAS:
        dificuldade = "imbativel"

    try:
        tabuleiro = _construir_super_tabuleiro(dados)
    except ValueError as exc:
        return jsonify({"erro": str(exc)}), 400

    if tabuleiro.jogo_terminou():
        return jsonify({
            "lance": None,
            "tabuleiro": tabuleiro.para_dict(),
            "telemetria": None,
        })

    simbolo_humano = "X" if simbolo_ia == "O" else "O"
    lance, detalhes = melhor_jogada_super(
        tabuleiro,
        simbolo_ia,
        simbolo_humano,
        dificuldade=dificuldade,
        retornar_detalhes=True,
    )

    if lance is not None:
        tabuleiro.jogar(lance[0], lance[1], simbolo_ia)

    return jsonify({
        "lance": list(lance) if lance is not None else None,
        "tabuleiro": tabuleiro.para_dict(),
        "telemetria": {
            "simulacoes": detalhes.get("simulacoes", 0),
            "nos_avaliados": detalhes.get("nos_avaliados", 0),
            "tempo_ms": detalhes.get("tempo_ms", 0),
            "taxa_vitoria": detalhes.get("taxa_vitoria", 50.0),
            "motivo": detalhes.get("motivo", ""),
            "dificuldade": dificuldade,
        },
    })


@app.route("/api/super/analisar", methods=["POST"])
def api_super_analisar():
    dados = request.get_json(silent=True) or {}
    simbolo_jogador = dados.get("simbolo_jogador", "X")

    if simbolo_jogador not in SIMBOLOS_VALIDOS:
        return jsonify({"erro": "Símbolo inválido."}), 400

    try:
        tabuleiro = _construir_super_tabuleiro(dados)
    except ValueError as exc:
        return jsonify({"erro": str(exc)}), 400

    if tabuleiro.jogo_terminou():
        return jsonify({
            "avaliacoes": [],
            "melhor_lance": None,
            "simulacoes": 0,
            "nos_avaliados": 0,
            "tempo_ms": 0,
        })

    simbolo_oponente = "O" if simbolo_jogador == "X" else "X"
    resultado = analisar_jogadas_super(tabuleiro, simbolo_jogador, simbolo_oponente)

    return jsonify({
        "avaliacoes": resultado["avaliacoes"],
        "melhor_lance": resultado["melhor_lance"],
        "simulacoes": resultado["simulacoes"],
        "nos_avaliados": resultado["nos_avaliados"],
        "tempo_ms": resultado["tempo_ms"],
    })


if __name__ == "__main__":
    porta = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=porta, debug=False)
