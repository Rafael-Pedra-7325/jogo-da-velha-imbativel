# ❌⭕ Jogo da Velha Imbatível

Jogo da velha de console em Python com uma IA baseada no algoritmo **Minimax**: ela nunca perde — no pior caso, empata.

## ✨ Funcionalidades
- Tabuleiro em texto, jogável direto no terminal
- IA com Minimax que sempre vence ou empata
- Testado com partidas simuladas aleatoriamente (30 partidas) + cenários táticos específicos (bloqueio e vitória)

## 🏗️ Arquitetura
```
jogo-da-velha-imbativel/
├── jogo.py     # regras e estado do tabuleiro
├── ia.py       # algoritmo Minimax
├── main.py     # interface de console
└── tests/
    └── test_ia.py
```

## 🚀 Como executar
```bash
python main.py
```

## 🧠 Sobre o Minimax
A IA simula recursivamente todas as jogadas possíveis a partir do estado atual, assumindo que o adversário também joga da melhor forma possível, e escolhe o caminho que maximiza sua própria pontuação (vitória) e minimiza a do oponente. Isso é exatamente o "algoritmo de busca" e "agente inteligente" citados no currículo aplicados na prática.

## 🧪 Testes
```bash
python -m unittest tests.test_ia -v
```
Inclui um teste que simula 30 partidas com jogadas aleatórias do "humano" e garante que a IA nunca perde nenhuma.

## 🔭 Próximos passos
- Interface gráfica com Pygame ou Tkinter
- Poda alfa-beta para otimizar a busca em tabuleiros maiores (ex: 4x4)
- Modo "fácil" com IA que erra de propósito
