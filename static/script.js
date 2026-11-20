(() => {
  const LINHAS_VITORIA = [
    [0, 1, 2], [3, 4, 5], [6, 7, 8],
    [0, 3, 6], [1, 4, 7], [2, 5, 8],
    [0, 4, 8], [2, 4, 6],
  ];

  const estado = {
    modoJogo: "classico",     // "classico" | "super"
    tipoOponente: "ia",       // "ia" | "local"
    dificuldade: "imbativel", // "facil" | "medio" | "imbativel"
    simboloP1: "X",           // "X" | "O" (Humano 1)
    simboloP2: "O",           // "O" | "X" (IA ou Jogador 2)
    turnoAtual: "X",          // "X" | "O"
    quemComeca: "p1",         // "p1" | "p2" | "alternar"
    proximoInicial: "p1",

    // Estado Clássico (3x3)
    celulas: Array(9).fill(" "),

    // Estado Super Jogo da Velha (9x9)
    superCelulas: Array.from({ length: 9 }, () => Array(9).fill(" ")),
    subAtivo: null,
    subVencedores: Array(9).fill(null),
    subEmpates: Array(9).fill(false),
    subEncerrados: Array(9).fill(false),
    ultimoLanceSuper: null,

    bloqueado: false,
    terminou: false,
    modoRaioX: false,
    somAtivo: true,
    historico: [],
    placar: {
      p1: 0,
      empates: 0,
      p2: 0,
      extra: 0,
    },
  };

  // Elementos do DOM
  const boardContainerEl = document.getElementById("board-container");
  const tabuleiroEl = document.getElementById("tabuleiro");
  const statusBanner = document.getElementById("status-banner");
  const statusTexto = document.getElementById("status-texto");
  const linhaVitoriaEl = document.getElementById("linha-vitoria");
  const telNosEl = document.getElementById("tel-nos");
  const telTempoEl = document.getElementById("tel-tempo");
  const telMotivoEl = document.getElementById("tel-motivo");
  const listaHistoricoEl = document.getElementById("lista-historico");
  const btnRaioX = document.getElementById("btn-raiox");
  const btnDica = document.getElementById("btn-dica");
  const btnSom = document.getElementById("btn-som");
  const badgeMotorEl = document.getElementById("badge-motor");
  const keyboardHintEl = document.getElementById("keyboard-hint");

  // Áudio Web Audio API
  let audioCtx = null;
  function tocarSom(tipo) {
    if (!estado.somAtivo) return;
    try {
      if (!audioCtx) {
        audioCtx = new (window.AudioContext || window.webkitAudioContext)();
      }
      const osc = audioCtx.createOscillator();
      const gain = audioCtx.createGain();
      osc.connect(gain);
      gain.connect(audioCtx.destination);

      const agora = audioCtx.currentTime;
      if (tipo === "p1") {
        osc.type = "sine";
        osc.frequency.setValueAtTime(520, agora);
        osc.frequency.exponentialRampToValueAtTime(680, agora + 0.08);
        gain.gain.setValueAtTime(0.08, agora);
        gain.gain.exponentialRampToValueAtTime(0.001, agora + 0.09);
        osc.start(agora);
        osc.stop(agora + 0.09);
      } else if (tipo === "p2") {
        osc.type = "triangle";
        osc.frequency.setValueAtTime(380, agora);
        osc.frequency.exponentialRampToValueAtTime(290, agora + 0.09);
        gain.gain.setValueAtTime(0.08, agora);
        gain.gain.exponentialRampToValueAtTime(0.001, agora + 0.1);
        osc.start(agora);
        osc.stop(agora + 0.1);
      } else if (tipo === "vitoria") {
        osc.type = "sine";
        osc.frequency.setValueAtTime(523.25, agora);
        osc.frequency.setValueAtTime(659.25, agora + 0.1);
        osc.frequency.setValueAtTime(783.99, agora + 0.2);
        gain.gain.setValueAtTime(0.1, agora);
        gain.gain.exponentialRampToValueAtTime(0.001, agora + 0.38);
        osc.start(agora);
        osc.stop(agora + 0.38);
      } else if (tipo === "derrota") {
        osc.type = "sawtooth";
        osc.frequency.setValueAtTime(240, agora);
        osc.frequency.linearRampToValueAtTime(160, agora + 0.28);
        gain.gain.setValueAtTime(0.06, agora);
        gain.gain.exponentialRampToValueAtTime(0.001, agora + 0.3);
        osc.start(agora);
        osc.stop(agora + 0.3);
      }
    } catch (_) {}
  }

  // Placar separado por modo (clássico/super e vs IA/2 Jogadores)
  function chavePlacar() {
    return `jdv_placar_${estado.modoJogo}_${estado.tipoOponente}`;
  }

  function carregarPlacar() {
    estado.placar = { p1: 0, empates: 0, p2: 0, extra: 0 };
    try {
      const salvo = localStorage.getItem(chavePlacar());
      if (salvo) {
        estado.placar = { ...estado.placar, ...JSON.parse(salvo) };
      }
    } catch (_) {}
    atualizarPlacarUI();
  }

  function salvarPlacar() {
    try {
      localStorage.setItem(chavePlacar(), JSON.stringify(estado.placar));
    } catch (_) {}
    atualizarPlacarUI();
  }

  function atualizarPlacarUI() {
    document.getElementById("placar-vitorias").textContent = estado.placar.p1;
    document.getElementById("placar-empates").textContent = estado.placar.empates;
    document.getElementById("placar-derrotas").textContent = estado.placar.p2;
    document.getElementById("placar-sequencia").textContent = estado.placar.extra;
  }

  function atualizarRotulosUI() {
    const ehLocal = estado.tipoOponente === "local";
    const ehSuper = estado.modoJogo === "super";

    badgeMotorEl.textContent = ehSuper
      ? "SUPER 9×9 • MCTS UCB1"
      : "CLÁSSICO 3×3 • MINIMAX + ALFA-BETA";

    document.getElementById("bloco-dificuldade").classList.toggle("hidden", ehLocal);
    document.getElementById("label-simbolo").textContent = ehLocal ? "Símbolo Jogador 1" : "Seu Símbolo";
    document.getElementById("btn-inicio-p1").textContent = ehLocal ? "Jogador 1" : "Você";
    document.getElementById("btn-inicio-p2").textContent = ehLocal ? "Jogador 2" : "IA";

    document.getElementById("label-placar-1").textContent = ehLocal ? `Jogador 1 (${estado.simboloP1})` : "Vitórias";
    document.getElementById("label-placar-2").textContent = ehLocal ? `Jogador 2 (${estado.simboloP2})` : "IA Venceu";
    document.getElementById("label-placar-extra").textContent = ehLocal ? "Partidas" : "Invencibilidade";

    document.getElementById("label-stat-nos").textContent = ehSuper ? "Simulações MCTS" : "Estados Analisados";
    boardContainerEl.classList.toggle("super-mode", ehSuper);

    keyboardHintEl.innerHTML = ehSuper
      ? 'Clique no mini-tabuleiro destacado em azul • <kbd>R</kbd> para nova partida'
      : 'Atalhos: teclas <kbd>1</kbd>–<kbd>9</kbd> para jogar rápido • <kbd>R</kbd> para nova partida';
  }

  function criarSvgSimbolo(simbolo) {
    if (simbolo === "X") {
      return `
        <svg class="symbol-svg symbol-x" viewBox="0 0 100 100">
          <line x1="22" y1="22" x2="78" y2="78" />
          <line x1="78" y1="22" x2="22" y2="78" />
        </svg>
      `;
    }
    return `
      <svg class="symbol-svg symbol-o" viewBox="0 0 100 100">
        <circle cx="50" cy="50" r="32" />
      </svg>
    `;
  }

  function atualizarStatus(texto, classe) {
    statusTexto.textContent = texto;
    statusBanner.className = `status-banner ${classe}`;
  }

  function nomeJogadorPorSimbolo(simbolo) {
    if (estado.tipoOponente === "ia") {
      return simbolo === estado.simboloP1 ? "Você" : "IA";
    }
    return simbolo === estado.simboloP1 ? "Jogador 1" : "Jogador 2";
  }

  function adicionarHistorico(autor, simbolo, descricao) {
    estado.historico.push({ autor, simbolo, descricao });
    listaHistoricoEl.innerHTML = "";
    estado.historico.forEach((item, idx) => {
      const li = document.createElement("li");
      li.innerHTML = `<span>#${idx + 1} ${item.autor} (<strong>${item.simbolo}</strong>)</span><span class="mono">${item.descricao}</span>`;
      listaHistoricoEl.appendChild(li);
    });
    listaHistoricoEl.scrollTop = listaHistoricoEl.scrollHeight;
  }

  function desenharLinhaVitoria(linha) {
    if (!linha || linha.length !== 3) return;
    const coords = [
      [50, 50], [150, 50], [250, 50],
      [50, 150], [150, 150], [250, 150],
      [50, 250], [150, 250], [250, 250],
    ];
    const [x1, y1] = coords[linha[0]];
    const [x2, y2] = coords[linha[2]];
    linhaVitoriaEl.setAttribute("x1", x1);
    linhaVitoriaEl.setAttribute("y1", y1);
    linhaVitoriaEl.setAttribute("x2", x2);
    linhaVitoriaEl.setAttribute("y2", y2);
    linhaVitoriaEl.classList.add("visible");

    if (estado.modoJogo === "classico") {
      const cells = tabuleiroEl.querySelectorAll(".cell");
      linha.forEach((idx) => cells[idx]?.classList.add("win-cell"));
    } else {
      const subs = tabuleiroEl.querySelectorAll(".sub-board");
      linha.forEach((idx) => subs[idx]?.classList.add("macro-win-sub"));
    }
  }

  // ============================================================================
  // LÓGICA DO MODO CLÁSSICO (3x3)
  // ============================================================================

  function verificarLinha3x3(c) {
    for (const [a, b, d] of LINHAS_VITORIA) {
      if (c[a] !== " " && c[a] === c[b] && c[a] === c[d]) {
        return [a, b, d];
      }
    }
    return null;
  }

  function renderizarTabuleiroClassico() {
    tabuleiroEl.innerHTML = "";
    estado.celulas.forEach((valor, indice) => {
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "cell";
      btn.dataset.index = indice;
      btn.setAttribute("aria-label", `Casa ${indice + 1}`);

      if (valor !== " ") {
        btn.classList.add("occupied");
        btn.innerHTML = `<span class="cell-index">${indice + 1}</span>${criarSvgSimbolo(valor)}`;
      } else {
        btn.innerHTML = `<span class="cell-index">${indice + 1}</span>`;
        if (estado.bloqueado || estado.terminou) {
          btn.classList.add("locked");
        } else {
          btn.addEventListener("click", () => jogarClassico(indice));
        }
      }
      tabuleiroEl.appendChild(btn);
    });

    if (estado.modoRaioX && !estado.terminou && !estado.bloqueado) {
      atualizarRaioX();
    }
  }

  async function jogarClassico(posicao) {
    if (estado.bloqueado || estado.terminou || estado.celulas[posicao] !== " ") {
      return;
    }

    const simboloJogado = estado.turnoAtual;
    const autor = nomeJogadorPorSimbolo(simboloJogado);

    estado.celulas[posicao] = simboloJogado;
    tocarSom(simboloJogado === estado.simboloP1 ? "p1" : "p2");
    adicionarHistorico(autor, simboloJogado, `Casa ${posicao + 1}`);

    const linha = verificarLinha3x3(estado.celulas);
    const cheio = !estado.celulas.includes(" ");

    if (linha || cheio) {
      finalizarPartida({
        terminou: true,
        vencedor: linha ? estado.celulas[linha[0]] : null,
        linha_vitoria: linha,
      });
      return;
    }

    estado.turnoAtual = simboloJogado === "X" ? "O" : "X";

    if (estado.tipoOponente === "local") {
      renderizarTabuleiro();
      atualizarMensagemTurnoLocal();
      return;
    }

    // Turno da IA
    estado.bloqueado = true;
    renderizarTabuleiro();
    await turnoIAClassico();
  }

  async function turnoIAClassico() {
    estado.bloqueado = true;
    atualizarStatus("🤖 IA calculando melhores futuros...", "turno-ia");

    try {
      const resp = await fetch("/api/jogada", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          celulas: estado.celulas,
          simbolo_ia: estado.simboloP2,
          dificuldade: estado.dificuldade,
        }),
      });

      const dados = await resp.json();
      if (!resp.ok) throw new Error(dados.erro || "Erro ao consultar a IA.");

      if (dados.telemetria) {
        telNosEl.textContent = dados.telemetria.nos_avaliados.toLocaleString("pt-BR");
        telTempoEl.textContent = `${dados.telemetria.tempo_ms} ms`;
        telMotivoEl.textContent = dados.telemetria.motivo;
      }

      if (dados.posicao !== null && dados.posicao !== undefined) {
        estado.celulas = dados.tabuleiro.celulas;
        tocarSom("p2");
        adicionarHistorico("IA", estado.simboloP2, `Casa ${dados.posicao + 1}`);
      }

      estado.bloqueado = false;
      estado.turnoAtual = estado.simboloP1;

      if (!finalizarPartida(dados.tabuleiro)) {
        renderizarTabuleiro();
        atualizarStatus("Sua vez! Escolha uma casa no tabuleiro.", "turno-humano");
      }
    } catch (erro) {
      estado.bloqueado = false;
      atualizarStatus(`⚠️ ${erro.message}`, "resultado-derrota");
    }
  }

  // ============================================================================
  // LÓGICA DO SUPER JOGO DA VELHA (9x9)
  // ============================================================================

  function recalcularSuperEstadoLocal() {
    for (let s = 0; s < 9; s++) {
      const sub = estado.superCelulas[s];
      const linha = verificarLinha3x3(sub);
      if (linha) {
        estado.subVencedores[s] = sub[linha[0]];
        estado.subEmpates[s] = false;
        estado.subEncerrados[s] = true;
      } else if (!sub.includes(" ")) {
        estado.subVencedores[s] = null;
        estado.subEmpates[s] = true;
        estado.subEncerrados[s] = true;
      } else {
        estado.subVencedores[s] = null;
        estado.subEmpates[s] = false;
        estado.subEncerrados[s] = false;
      }
    }

    if (estado.subAtivo !== null && estado.subEncerrados[estado.subAtivo]) {
      estado.subAtivo = null;
    }

    const macro = estado.subVencedores.map((v) => v || " ");
    const linhaMacro = verificarLinha3x3(macro);
    const vencedor = linhaMacro ? macro[linhaMacro[0]] : null;
    const terminou = vencedor !== null || estado.subEncerrados.every(Boolean);

    return {
      terminou,
      vencedor,
      linha_vitoria: linhaMacro,
    };
  }

  function aplicarDadosSuperDoServidor(tab) {
    estado.superCelulas = tab.celulas;
    estado.subAtivo = tab.sub_ativo;
    estado.subVencedores = tab.sub_vencedores;
    estado.subEmpates = tab.sub_empates;
    estado.subEncerrados = tab.sub_encerrados;
    estado.ultimoLanceSuper = tab.ultimo_lance;
  }

  function renderizarTabuleiroSuper() {
    tabuleiroEl.innerHTML = "";
    const jogadaLivre = estado.subAtivo === null && !estado.terminou && !estado.bloqueado;

    for (let s = 0; s < 9; s++) {
      const subEl = document.createElement("div");
      subEl.className = "sub-board";
      subEl.dataset.sub = s;

      const subEncerrado = estado.subEncerrados[s];
      const subVencedor = estado.subVencedores[s];
      const subAtivoAgora =
        !estado.terminou &&
        !estado.bloqueado &&
        !subEncerrado &&
        (estado.subAtivo === null || estado.subAtivo === s);

      if (subVencedor === "X") subEl.classList.add("won-x");
      else if (subVencedor === "O") subEl.classList.add("won-o");
      else if (estado.subEmpates[s]) subEl.classList.add("drawn-sub");

      if (!estado.terminou) {
        if (estado.subAtivo === s && !subEncerrado) {
          subEl.classList.add("active-target");
        } else if (jogadaLivre && !subEncerrado) {
          subEl.classList.add("free-target");
        } else {
          subEl.classList.add("inactive-sub");
        }
      }

      for (let c = 0; c < 9; c++) {
        const valor = estado.superCelulas[s][c];
        const cellBtn = document.createElement("button");
        cellBtn.type = "button";
        cellBtn.className = "super-cell";
        cellBtn.dataset.sub = s;
        cellBtn.dataset.cell = c;
        cellBtn.setAttribute("aria-label", `Sub-tabuleiro ${s + 1}, Casa ${c + 1}`);

        if (
          estado.ultimoLanceSuper &&
          estado.ultimoLanceSuper[0] === s &&
          estado.ultimoLanceSuper[1] === c
        ) {
          cellBtn.classList.add("last-move");
        }

        if (valor !== " ") {
          cellBtn.classList.add("occupied");
          cellBtn.innerHTML = criarSvgSimbolo(valor);
        } else if (!subAtivoAgora) {
          cellBtn.classList.add("locked");
        } else {
          cellBtn.addEventListener("click", () => jogarSuper(s, c));
        }

        subEl.appendChild(cellBtn);
      }

      if (subVencedor === "X" || subVencedor === "O") {
        const overlay = document.createElement("div");
        overlay.className = `sub-overlay overlay-${subVencedor.toLowerCase()}`;
        overlay.innerHTML = criarSvgSimbolo(subVencedor);
        subEl.appendChild(overlay);
      } else if (estado.subEmpates[s]) {
        const overlay = document.createElement("div");
        overlay.className = "sub-overlay overlay-draw";
        overlay.textContent = "=";
        subEl.appendChild(overlay);
      }

      tabuleiroEl.appendChild(subEl);
    }

    if (estado.modoRaioX && !estado.terminou && !estado.bloqueado) {
      atualizarRaioX();
    }
  }

  async function jogarSuper(subIdx, cellIdx) {
    if (estado.bloqueado || estado.terminou) return;
    if (estado.subEncerrados[subIdx]) return;
    if (estado.subAtivo !== null && estado.subAtivo !== subIdx) return;
    if (estado.superCelulas[subIdx][cellIdx] !== " ") return;

    const simboloJogado = estado.turnoAtual;
    const autor = nomeJogadorPorSimbolo(simboloJogado);

    estado.superCelulas[subIdx][cellIdx] = simboloJogado;
    estado.ultimoLanceSuper = [subIdx, cellIdx];
    estado.subAtivo = cellIdx;

    tocarSom(simboloJogado === estado.simboloP1 ? "p1" : "p2");
    adicionarHistorico(autor, simboloJogado, `Q${subIdx + 1}·C${cellIdx + 1}`);

    const info = recalcularSuperEstadoLocal();
    if (info.terminou) {
      finalizarPartida(info);
      return;
    }

    estado.turnoAtual = simboloJogado === "X" ? "O" : "X";

    if (estado.tipoOponente === "local") {
      renderizarTabuleiro();
      atualizarMensagemTurnoLocal();
      return;
    }

    // Turno da IA (MCTS)
    estado.bloqueado = true;
    renderizarTabuleiro();
    await turnoIASuper();
  }

  async function turnoIASuper() {
    estado.bloqueado = true;
    atualizarStatus("🤖 MCTS simulando milhares de partidas...", "turno-ia");

    try {
      const resp = await fetch("/api/super/jogada", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          celulas: estado.superCelulas,
          sub_ativo: estado.subAtivo,
          ultimo_lance: estado.ultimoLanceSuper,
          simbolo_ia: estado.simboloP2,
          dificuldade: estado.dificuldade,
        }),
      });

      const dados = await resp.json();
      if (!resp.ok) throw new Error(dados.erro || "Erro ao consultar o motor MCTS.");

      if (dados.telemetria) {
        telNosEl.textContent = dados.telemetria.simulacoes.toLocaleString("pt-BR");
        telTempoEl.textContent = `${dados.telemetria.tempo_ms} ms`;
        telMotivoEl.textContent = dados.telemetria.motivo;
      }

      if (dados.lance) {
        aplicarDadosSuperDoServidor(dados.tabuleiro);
        tocarSom("p2");
        adicionarHistorico("IA", estado.simboloP2, `Q${dados.lance[0] + 1}·C${dados.lance[1] + 1}`);
      }

      estado.bloqueado = false;
      estado.turnoAtual = estado.simboloP1;

      if (!finalizarPartida(dados.tabuleiro)) {
        renderizarTabuleiro();
        atualizarMensagemTurnoHumanoSuper();
      }
    } catch (erro) {
      estado.bloqueado = false;
      atualizarStatus(`⚠️ ${erro.message}`, "resultado-derrota");
    }
  }

  // ============================================================================
  // COMPARTILHADO: MENSAGENS, FINALIZAÇÃO, RAIO-X E DICA
  // ============================================================================

  function atualizarMensagemTurnoHumanoSuper() {
    if (estado.subAtivo === null) {
      atualizarStatus("Sua vez! Jogada livre: escolha qualquer quadrante aberto.", "turno-humano");
    } else {
      atualizarStatus(`Sua vez! Jogue no quadrante #${estado.subAtivo + 1} destacado.`, "turno-humano");
    }
  }

  function atualizarMensagemTurnoLocal() {
    const ehP1 = estado.turnoAtual === estado.simboloP1;
    const nome = ehP1 ? `Jogador 1 (${estado.simboloP1})` : `Jogador 2 (${estado.simboloP2})`;
    const classe = ehP1 ? "turno-humano" : "turno-ia";

    if (estado.modoJogo === "super") {
      const alvo =
        estado.subAtivo === null
          ? "jogada livre em qualquer quadrante aberto"
          : `jogue no quadrante #${estado.subAtivo + 1}`;
      atualizarStatus(`Vez de ${nome} — ${alvo}.`, classe);
    } else {
      atualizarStatus(`Vez de ${nome}! Escolha uma casa.`, classe);
    }
  }

  function renderizarTabuleiro() {
    if (estado.modoJogo === "super") {
      renderizarTabuleiroSuper();
    } else {
      renderizarTabuleiroClassico();
    }
  }

  function finalizarPartida(info) {
    if (!info || !info.terminou) return false;

    estado.terminou = true;
    estado.bloqueado = true;
    renderizarTabuleiro();

    const ehLocal = estado.tipoOponente === "local";

    if (info.vencedor) {
      desenharLinhaVitoria(info.linha_vitoria);
      if (info.vencedor === estado.simboloP1) {
        estado.placar.p1 += 1;
        estado.placar.extra += 1;
        atualizarStatus(
          ehLocal
            ? `🏆 Vitória do Jogador 1 (${estado.simboloP1})!`
            : "🎉 Incrível! Você venceu a IA!",
          "resultado-vitoria"
        );
        tocarSom("vitoria");
      } else {
        estado.placar.p2 += 1;
        estado.placar.extra = ehLocal ? estado.placar.extra + 1 : 0;
        atualizarStatus(
          ehLocal
            ? `🏆 Vitória do Jogador 2 (${estado.simboloP2})!`
            : "🤖 A IA venceu! Mais sorte na próxima.",
          ehLocal ? "resultado-vitoria" : "resultado-derrota"
        );
        tocarSom(ehLocal ? "vitoria" : "derrota");
      }
    } else {
      estado.placar.empates += 1;
      estado.placar.extra += 1;
      atualizarStatus("🤝 Empate perfeito! Partida muito disputada.", "resultado-empate");
    }

    salvarPlacar();
    return true;
  }

  async function atualizarRaioX() {
    if (estado.terminou || estado.bloqueado) return;
    const simboloConsulta = estado.turnoAtual;

    if (estado.modoJogo === "classico") {
      try {
        const resp = await fetch("/api/analisar", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            celulas: estado.celulas,
            simbolo_jogador: simboloConsulta,
          }),
        });
        const dados = await resp.json();
        if (!resp.ok || !dados.avaliacoes) return;

        const cells = tabuleiroEl.querySelectorAll(".cell");
        cells.forEach((cell) => cell.querySelector(".xray-badge")?.remove());

        const mapaRotulo = { vitoria: "Vitória", empate: "Empate", derrota: "Derrota" };
        dados.avaliacoes.forEach((item) => {
          const cell = cells[item.posicao];
          if (!cell || cell.classList.contains("occupied")) return;
          const badge = document.createElement("span");
          badge.className = `xray-badge xray-${item.desfecho}`;
          badge.textContent = `${mapaRotulo[item.desfecho]} (${item.pontuacao > 0 ? "+" : ""}${item.pontuacao})`;
          cell.appendChild(badge);
        });
      } catch (_) {}
    } else {
      try {
        const resp = await fetch("/api/super/analisar", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            celulas: estado.superCelulas,
            sub_ativo: estado.subAtivo,
            simbolo_jogador: simboloConsulta,
          }),
        });
        const dados = await resp.json();
        if (!resp.ok || !dados.avaliacoes) return;

        tabuleiroEl.querySelectorAll(".xray-badge").forEach((el) => el.remove());
        dados.avaliacoes.slice(0, 12).forEach((item) => {
          const cell = tabuleiroEl.querySelector(
            `.super-cell[data-sub="${item.sub_tabuleiro}"][data-cell="${item.celula}"]`
          );
          if (!cell || cell.classList.contains("occupied")) return;
          const badge = document.createElement("span");
          badge.className = `xray-badge xray-${item.desfecho}`;
          badge.textContent = `${Math.round(item.taxa_vitoria)}%`;
          cell.appendChild(badge);
        });
      } catch (_) {}
    }
  }

  async function mostrarDica() {
    if (estado.bloqueado || estado.terminou) return;
    const simboloConsulta = estado.turnoAtual;

    if (estado.modoJogo === "classico") {
      try {
        const resp = await fetch("/api/analisar", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            celulas: estado.celulas,
            simbolo_jogador: simboloConsulta,
          }),
        });
        const dados = await resp.json();
        if (!resp.ok || dados.melhor_posicao === null) return;

        const cells = tabuleiroEl.querySelectorAll(".cell");
        cells.forEach((c) => c.classList.remove("hint-cell"));
        const alvo = cells[dados.melhor_posicao];
        if (alvo) {
          alvo.classList.add("hint-cell");
          telMotivoEl.textContent = `Dica (${simboloConsulta}): jogar na casa ${dados.melhor_posicao + 1} é a melhor opção (${dados.nos_avaliados} estados).`;
        }
      } catch (_) {}
    } else {
      try {
        telMotivoEl.textContent = "Calculando dica via MCTS...";
        const resp = await fetch("/api/super/analisar", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            celulas: estado.superCelulas,
            sub_ativo: estado.subAtivo,
            simbolo_jogador: simboloConsulta,
          }),
        });
        const dados = await resp.json();
        if (!resp.ok || !dados.melhor_lance) return;

        tabuleiroEl.querySelectorAll(".hint-cell").forEach((c) => c.classList.remove("hint-cell"));
        const [s, c] = dados.melhor_lance;
        const alvo = tabuleiroEl.querySelector(`.super-cell[data-sub="${s}"][data-cell="${c}"]`);
        if (alvo) {
          alvo.classList.add("hint-cell");
          const top = dados.avaliacoes[0];
          telNosEl.textContent = dados.simulacoes.toLocaleString("pt-BR");
          telTempoEl.textContent = `${dados.tempo_ms} ms`;
          telMotivoEl.textContent = `Dica (${simboloConsulta}): Quadrante #${s + 1}, Casa #${c + 1} (${top?.taxa_vitoria ?? 50}% de vitórias em ${dados.simulacoes} simulações).`;
        }
      } catch (_) {}
    }
  }

  async function iniciarNovaPartida() {
    estado.celulas = Array(9).fill(" ");
    estado.superCelulas = Array.from({ length: 9 }, () => Array(9).fill(" "));
    estado.subAtivo = null;
    estado.subVencedores = Array(9).fill(null);
    estado.subEmpates = Array(9).fill(false);
    estado.subEncerrados = Array(9).fill(false);
    estado.ultimoLanceSuper = null;

    estado.terminou = false;
    estado.bloqueado = false;
    estado.historico = [];
    linhaVitoriaEl.classList.remove("visible");
    listaHistoricoEl.innerHTML = '<li class="empty-history">Nenhum lance realizado ainda.</li>';
    telNosEl.textContent = "—";
    telTempoEl.textContent = "—";
    telMotivoEl.textContent = "Nova partida iniciada. Aguardando lance.";

    let inicial = estado.quemComeca;
    if (inicial === "alternar") {
      inicial = estado.proximoInicial;
      estado.proximoInicial = estado.proximoInicial === "p1" ? "p2" : "p1";
    }

    estado.turnoAtual = inicial === "p1" ? estado.simboloP1 : estado.simboloP2;
    atualizarRotulosUI();
    renderizarTabuleiro();

    if (estado.tipoOponente === "ia" && inicial === "p2") {
      if (estado.modoJogo === "super") {
        await turnoIASuper();
      } else {
        await turnoIAClassico();
      }
    } else if (estado.tipoOponente === "local") {
      atualizarMensagemTurnoLocal();
    } else if (estado.modoJogo === "super") {
      atualizarMensagemTurnoHumanoSuper();
    } else {
      atualizarStatus("Sua vez! Escolha uma casa no tabuleiro.", "turno-humano");
    }
  }

  // Configuração dos controles
  function configurarSegmented(containerId, callback) {
    const container = document.getElementById(containerId);
    container.querySelectorAll("button").forEach((btn) => {
      btn.addEventListener("click", () => {
        container.querySelectorAll("button").forEach((b) => b.classList.remove("active"));
        btn.classList.add("active");
        callback(btn.dataset.value);
      });
    });
  }

  configurarSegmented("grupo-modo", (valor) => {
    estado.modoJogo = valor;
    carregarPlacar();
    iniciarNovaPartida();
  });

  configurarSegmented("grupo-oponente", (valor) => {
    estado.tipoOponente = valor;
    carregarPlacar();
    iniciarNovaPartida();
  });

  configurarSegmented("grupo-dificuldade", (valor) => {
    estado.dificuldade = valor;
    iniciarNovaPartida();
  });

  configurarSegmented("grupo-simbolo", (valor) => {
    estado.simboloP1 = valor;
    estado.simboloP2 = valor === "X" ? "O" : "X";
    atualizarRotulosUI();
    iniciarNovaPartida();
  });

  configurarSegmented("grupo-inicio", (valor) => {
    estado.quemComeca = valor;
    iniciarNovaPartida();
  });

  document.getElementById("btn-reiniciar").addEventListener("click", iniciarNovaPartida);

  document.getElementById("btn-zerar-placar").addEventListener("click", () => {
    estado.placar = { p1: 0, empates: 0, p2: 0, extra: 0 };
    salvarPlacar();
  });

  btnRaioX.addEventListener("click", () => {
    estado.modoRaioX = !estado.modoRaioX;
    btnRaioX.classList.toggle("active", estado.modoRaioX);
    renderizarTabuleiro();
  });

  btnDica.addEventListener("click", mostrarDica);

  btnSom.addEventListener("click", () => {
    estado.somAtivo = !estado.somAtivo;
    btnSom.textContent = estado.somAtivo ? "🔊" : "🔇";
  });

  const modalRegras = document.getElementById("modal-regras");
  document.getElementById("btn-regras").addEventListener("click", () => modalRegras.showModal());
  document.getElementById("btn-fechar-regras").addEventListener("click", () => modalRegras.close());
  modalRegras.addEventListener("click", (e) => {
    if (e.target === modalRegras) modalRegras.close();
  });

  document.addEventListener("keydown", (e) => {
    if (estado.modoJogo === "classico" && e.key >= "1" && e.key <= "9") {
      const idx = parseInt(e.key, 10) - 1;
      jogarClassico(idx);
    } else if (e.key.toLowerCase() === "r") {
      iniciarNovaPartida();
    }
  });

  carregarPlacar();
  iniciarNovaPartida();
})();
