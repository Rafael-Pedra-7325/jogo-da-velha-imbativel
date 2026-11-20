"""
Jogo da Velha Imbatível — interface de console.
Suporta Clássico (3x3) e Super Jogo da Velha (9x9), contra a IA ou 2 Jogadores Locais.
"""

from jogo import Tabuleiro
from super_jogo import SuperTabuleiro
from ia import melhor_jogada, melhor_jogada_super

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


def exibir_super_tabuleiro(tab):
    print()
    for macro_linha in range(3):
        for sub_linha in range(3):
            partes = []
            for macro_col in range(3):
                s = macro_linha * 3 + macro_col
                ativo = tab.sub_ativo in (None, s) and not tab.sub_encerrados[s]
                cor_borda = COR_CIANO if ativo else COR_CINZA
                celulas_linha = []
                for sub_col in range(3):
                    c = sub_linha * 3 + sub_col
                    val = tab.celulas[s][c]
                    celulas_linha.append(formatar_celula(val, c))
                partes.append(f"{cor_borda}[{COR_RESET}" + " ".join(celulas_linha) + f"{cor_borda}]{COR_RESET}")
            print("  " + " ┃ ".join(partes))
        if macro_linha < 2:
            print(" ════════╬════════╬════════")
    print(f"\n  Sub-tabuleiros vencidos: {tab.sub_vencedores}")
    alvo = "LIVRE (qualquer aberto)" if tab.sub_ativo is None else f"#{tab.sub_ativo}"
    print(f"  Sub-tabuleiro obrigatório: {NEGRITO}{COR_AMARELO}{alvo}{COR_RESET}\n")


def escolher_opcoes():
    print(f"{NEGRITO}{COR_CIANO}╔══════════════════════════════════════════╗{COR_RESET}")
    print(f"{NEGRITO}{COR_CIANO}║  ❌⭕ JOGO DA VELHA IMBATÍVEL & SUPER 9x9 ║{COR_RESET}")
    print(f"{NEGRITO}{COR_CIANO}╚══════════════════════════════════════════╝{COR_RESET}")

    print("\nEscolha o modo de jogo:")
    print("  [1] Clássico (3x3)")
    print("  [2] Super Jogo da Velha (9x9)")
    modo = "super" if input("Modo [1]: ").strip() == "2" else "classico"

    print("\nEscolha o adversário:")
    print("  [1] Contra a IA")
    print("  [2] 2 Jogadores (Mesmo Local)")
    dois_jogadores = input("Adversário [1]: ").strip() == "2"

    dificuldade = "imbativel"
    if not dois_jogadores:
        print("\nEscolha a dificuldade da IA:")
        print("  [1] Fácil")
        print("  [2] Médio")
        print("  [3] Imbatível")
        opcao_dif = input("Opção [3]: ").strip()
        dificuldade = {"1": "facil", "2": "medio", "3": "imbativel"}.get(opcao_dif, "imbativel")

    simbolo_p1 = input("Jogador 1 quer jogar com X ou O? [X]: ").strip().upper()
    if simbolo_p1 not in ("X", "O"):
        simbolo_p1 = "X"
    simbolo_p2 = "O" if simbolo_p1 == "X" else "X"

    rotulo_p2 = "Jogador 2" if dois_jogadores else "IA"
    comeca = input(f"Quem começa? [1] Jogador 1  [2] {rotulo_p2} [1]: ").strip()
    turno_p2 = comeca == "2"

    return modo, dois_jogadores, simbolo_p1, simbolo_p2, dificuldade, turno_p2


def pedir_jogada_classica(tabuleiro, nome_jogador):
    while True:
        entrada = input(f"{nome_jogador}, sua jogada (0-8): ").strip()
        if not entrada.isdigit():
            print(f"{COR_AMARELO}Digite um número de 0 a 8.{COR_RESET}")
            continue
        posicao = int(entrada)
        if posicao not in range(9) or posicao not in tabuleiro.posicoes_livres():
            print(f"{COR_AMARELO}Posição inválida ou já ocupada.{COR_RESET}")
            continue
        return posicao


def pedir_jogada_super(tab, nome_jogador):
    legais = set(tab.jogadas_legais())
    while True:
        if tab.sub_ativo is not None:
            sub = tab.sub_ativo
            entrada = input(f"{nome_jogador} (Sub #{sub}), escolha a célula (0-8): ").strip()
            if not entrada.isdigit():
                print(f"{COR_AMARELO}Digite um número de 0 a 8.{COR_RESET}")
                continue
            cel = int(entrada)
            if (sub, cel) not in legais:
                print(f"{COR_AMARELO}Célula inválida ou já ocupada.{COR_RESET}")
                continue
            return (sub, cel)
        else:
            entrada = input(f"{nome_jogador} (Jogada Livre), digite 'sub celula' (ex: 4 0): ").strip().split()
            if len(entrada) != 2 or not all(p.isdigit() for p in entrada):
                print(f"{COR_AMARELO}Formato inválido. Digite dois números de 0 a 8 separados por espaço.{COR_RESET}")
                continue
            sub, cel = int(entrada[0]), int(entrada[1])
            if (sub, cel) not in legais:
                print(f"{COR_AMARELO}Jogada inválida ou sub-tabuleiro já encerrado.{COR_RESET}")
                continue
            return (sub, cel)


def jogar():
    modo, dois_jogadores, simbolo_p1, simbolo_p2, dificuldade, turno_p2 = escolher_opcoes()

    if modo == "classico":
        tabuleiro = Tabuleiro()
        while not tabuleiro.jogo_terminou():
            exibir_tabuleiro(tabuleiro)
            if turno_p2 and not dois_jogadores:
                pos, det = melhor_jogada(
                    tabuleiro, simbolo_p2, simbolo_p1,
                    dificuldade=dificuldade, retornar_detalhes=True
                )
                tabuleiro.jogar(pos, simbolo_p2)
                print(f"{COR_ROSA}🤖 IA jogou na casa {pos}{COR_RESET} ({det['nos_avaliados']} estados em {det['tempo_ms']}ms)")
            elif turno_p2:
                pos = pedir_jogada_classica(tabuleiro, f"Jogador 2 ({simbolo_p2})")
                tabuleiro.jogar(pos, simbolo_p2)
            else:
                pos = pedir_jogada_classica(tabuleiro, f"Jogador 1 ({simbolo_p1})")
                tabuleiro.jogar(pos, simbolo_p1)
            turno_p2 = not turno_p2

        exibir_tabuleiro(tabuleiro)
        vencedor = tabuleiro.vencedor()
    else:
        tab = SuperTabuleiro()
        while not tab.jogo_terminou():
            exibir_super_tabuleiro(tab)
            if turno_p2 and not dois_jogadores:
                lance, det = melhor_jogada_super(
                    tab, simbolo_p2, simbolo_p1,
                    dificuldade=dificuldade, retornar_detalhes=True
                )
                tab.jogar(lance[0], lance[1], simbolo_p2)
                print(f"{COR_ROSA}🤖 IA jogou em Sub #{lance[0]}, Casa #{lance[1]}{COR_RESET} ({det['motivo']})")
            elif turno_p2:
                sub, cel = pedir_jogada_super(tab, f"Jogador 2 ({simbolo_p2})")
                tab.jogar(sub, cel, simbolo_p2)
            else:
                sub, cel = pedir_jogada_super(tab, f"Jogador 1 ({simbolo_p1})")
                tab.jogar(sub, cel, simbolo_p1)
            turno_p2 = not turno_p2

        exibir_super_tabuleiro(tab)
        vencedor = tab.vencedor()

    if vencedor == simbolo_p1:
        print(f"{NEGRITO}{COR_VERDE}🎉 Vitória do Jogador 1 ({simbolo_p1})!{COR_RESET}")
    elif vencedor == simbolo_p2:
        vencedor_nome = f"Jogador 2 ({simbolo_p2})" if dois_jogadores else "IA"
        print(f"{NEGRITO}{COR_ROSA}🏆 Vitória de {vencedor_nome}!{COR_RESET}")
    else:
        print(f"{NEGRITO}{COR_AMARELO}🤝 Empate perfeito!{COR_RESET}")


if __name__ == "__main__":
    jogar()
