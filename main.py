"""
Jogo da Velha Imbatível — interface de console aprimorada.
Permite escolher dificuldade, símbolo (X ou O) e exibe telemetria da IA.
"""

from jogo import Tabuleiro
from ia import melhor_jogada

COR_RESET = "\033[0m"
COR_CIANO = "\033[96m"
COR_ROSA = "\033[95m"
COR_VERDE = "\033[92m"
COR_AMARELO = "\033[93m"
COR_CINZA = "\033[90m"
NEGRITO = "\033[1m"


def formatar_celula(valor, indice):
    if valor == "X":
        return f"{NEGRITO}{COR_CIANO}X{COR_RESET}"
    if valor == "O":
        return f"{NEGRITO}{COR_ROSA}O{COR_RESET}"
    return f"{COR_CINZA}{indice}{COR_RESET}"


def exibir_tabuleiro(tabuleiro):
    print()
    for linha in range(3):
        inicio = linha * 3
        celulas = [formatar_celula(tabuleiro.celulas[inicio + c], inicio + c) for c in range(3)]
        print(f"  {celulas[0]} │ {celulas[1]} │ {celulas[2]}")
        if linha < 2:
            print(" ───┼───┼───")
    print()


def escolher_opcoes():
    print(f"{NEGRITO}{COR_CIANO}╔══════════════════════════════════════╗{COR_RESET}")
    print(f"{NEGRITO}{COR_CIANO}║     ❌⭕ JOGO DA VELHA IMBATÍVEL     ║{COR_RESET}")
    print(f"{NEGRITO}{COR_CIANO}╚══════════════════════════════════════╝{COR_RESET}")

    print("\nEscolha a dificuldade:")
    print("  [1] Fácil (Aprendiz)")
    print("  [2] Médio (Desafiante)")
    print("  [3] Imbatível (Minimax + Poda Alfa-Beta)")
    opcao_dif = input("Opção [3]: ").strip()
    mapa_dif = {"1": "facil", "2": "medio", "3": "imbativel"}
    dificuldade = mapa_dif.get(opcao_dif, "imbativel")

    simbolo_humano = input("Você quer jogar com X ou O? [X]: ").strip().upper()
    if simbolo_humano not in ("X", "O"):
        simbolo_humano = "X"
    simbolo_ia = "O" if simbolo_humano == "X" else "X"

    comeca = input("Quem começa? [1] Você  [2] IA [1]: ").strip()
    turno_ia = comeca == "2"

    return simbolo_humano, simbolo_ia, dificuldade, turno_ia


def pedir_jogada(tabuleiro):
    while True:
        entrada = input("Sua jogada (0-8): ").strip()
        if not entrada.isdigit():
            print(f"{COR_AMARELO}Digite um número de 0 a 8.{COR_RESET}")
            continue

        posicao = int(entrada)
        if posicao not in range(9) or posicao not in tabuleiro.posicoes_livres():
            print(f"{COR_AMARELO}Posição inválida ou já ocupada.{COR_RESET}")
            continue

        return posicao


def jogar():
    simbolo_humano, simbolo_ia, dificuldade, turno_ia = escolher_opcoes()
    tabuleiro = Tabuleiro()

    while not tabuleiro.jogo_terminou():
        exibir_tabuleiro(tabuleiro)

        if turno_ia:
            posicao_ia, detalhes = melhor_jogada(
                tabuleiro, simbolo_ia, simbolo_humano,
                dificuldade=dificuldade, retornar_detalhes=True
            )
            tabuleiro.jogar(posicao_ia, simbolo_ia)
            print(
                f"{COR_ROSA}🤖 IA jogou na casa {posicao_ia}{COR_RESET} "
                f"{COR_CINZA}({detalhes['nos_avaliados']} estados em {detalhes['tempo_ms']}ms — {detalhes['motivo']}){COR_RESET}"
            )
        else:
            posicao = pedir_jogada(tabuleiro)
            tabuleiro.jogar(posicao, simbolo_humano)

        turno_ia = not turno_ia

    exibir_tabuleiro(tabuleiro)
    vencedor = tabuleiro.vencedor()

    if vencedor == simbolo_humano:
        print(f"{NEGRITO}{COR_VERDE}🎉 Parabéns! Você venceu a IA!{COR_RESET}")
    elif vencedor == simbolo_ia:
        print(f"{NEGRITO}{COR_ROSA}🤖 A IA venceu! Tente novamente.{COR_RESET}")
    else:
        print(f"{NEGRITO}{COR_AMARELO}🤝 Empate perfeito!{COR_RESET}")


if __name__ == "__main__":
    jogar()
