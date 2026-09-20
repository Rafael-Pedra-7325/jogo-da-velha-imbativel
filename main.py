"""
Jogo da Velha Imbatível — interface de console.
Você joga com 'X', a IA joga com 'O' e nunca perde.
"""

from jogo import Tabuleiro
from ia import melhor_jogada

SIMBOLO_HUMANO = "X"
SIMBOLO_IA = "O"


def pedir_jogada(tabuleiro):
    while True:
        entrada = input("Sua jogada (0-8, veja o mapa de posições acima): ").strip()
        if not entrada.isdigit():
            print("Digite um número de 0 a 8.")
            continue

        posicao = int(entrada)
        if posicao not in range(9) or posicao not in tabuleiro.posicoes_livres():
            print("Posição inválida ou já ocupada.")
            continue

        return posicao


def mostrar_mapa_posicoes():
    print("Mapa de posições:")
    print(" 0 | 1 | 2 \n---------\n 3 | 4 | 5 \n---------\n 6 | 7 | 8 ")
    print()


def jogar():
    tabuleiro = Tabuleiro()
    mostrar_mapa_posicoes()

    while not tabuleiro.jogo_terminou():
        print(tabuleiro)
        print()

        posicao = pedir_jogada(tabuleiro)
        tabuleiro.jogar(posicao, SIMBOLO_HUMANO)

        if tabuleiro.jogo_terminou():
            break

        posicao_ia = melhor_jogada(tabuleiro, SIMBOLO_IA, SIMBOLO_HUMANO)
        tabuleiro.jogar(posicao_ia, SIMBOLO_IA)
        print(f"\nA IA jogou na posição {posicao_ia}.\n")

    print(tabuleiro)
    vencedor = tabuleiro.vencedor()

    if vencedor == SIMBOLO_HUMANO:
        print("\n🎉 Você venceu! (isso não deveria acontecer...)")
    elif vencedor == SIMBOLO_IA:
        print("\n🤖 A IA venceu!")
    else:
        print("\n🤝 Empate!")


if __name__ == "__main__":
    jogar()
