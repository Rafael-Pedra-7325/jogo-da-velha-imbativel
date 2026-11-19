(() => {
  const estado = {
    celulas: Array(9).fill(" "),
    simboloHumano: "X",
    simboloIA: "O",
    dificuldade: "imbativel",
    quemComeca: "humano",
    proximoInicial: "humano",
    bloqueado: false,
    terminou: false,
    modoRaioX: false,
    somAtivo: true,
    historico: [],
    placar: {
      vitorias: 0,
      empates: 0,
      derrotas: 0,
      sequencia: 0,
    },
  };

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
      if (tipo === "humano") {
        osc.type = "sine";
        osc.frequency.setValueAtTime(520, agora);
        osc.frequency.exponentialRampToValueAtTime(680, agora + 0.08);
        gain.gain.setValueAtTime(0.08, agora);
        gain.gain.exponentialRampToValueAtTime(0.001, agora + 0.09);
        osc.start(agora);
        osc.stop(agora + 0.09);
      } else if (tipo === "ia") {
        osc.type = "triangle";
        osc.frequency.setValueAtTime(360, agora);
        osc.frequency.exponentialRampToValueAtTime(280, agora + 0.09);
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

  function carregarPlacar() {
    try {
      const salvo = localStorage.getItem("jdv_imbativel_placar");
      if (salvo) {
        estado.placar = { ...estado.placar, ...JSON.parse(salvo) };
      }
    } catch (_) {}
    atualizarPlacarUI();
  }

  function salvarPlacar() {
    try {
      localStorage.setItem("jdv_imbativel_placar", JSON.stringify(estado.placar));
    } catch (_) {}
    atualizarPlacarUI();
  }

  function atualizarPlacarUI() {
    document.getElementById("placar-vitorias").textContent = estado.placar.vitorias;
    document.getElementById("placar-empates").textContent = estado.placar.empates;
    document.getElementById("placar-derrotas").textContent = estado.placar.derrotas;
    document.getElementById("placar-sequencia").textContent = estado.placar.sequencia;
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

  function renderizarTabuleiro() {
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
          btn.addEventListener("click", () => jogarHumano(indice));
        }
      }

      tabuleiroEl.appendChild(btn);
    });

    if (estado.modoRaioX && !estado.terminou && !estado.bloqueado) {
      atualizarRaioX();
    }
  }

  function atualizarStatus(texto, classe) {
    statusTexto.textContent = texto;
    statusBanner.className = `status-banner ${classe}`;
  }

  function adicionarHistorico(autor, simbolo, posicao) {
    estado.historico.push({ autor, simbolo, posicao: posicao + 1 });
    listaHistoricoEl.innerHTML = "";
    estado.historico.forEach((item, idx) => {
      const li = document.createElement("li");
      li.innerHTML = `<span>#${idx + 1} ${item.autor} (<strong>${item.simbolo}</strong>)</span><span class="mono">Casa ${item.posicao}</span>`;
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

    const cells = tabuleiroEl.querySelectorAll(".cell");
    linha.forEach((idx) => cells[idx]?.classList.add("win-cell"));
  }

  function verificarFimDeJogo(infoTabuleiro) {
    if (!infoTabuleiro || !infoTabuleiro.terminou) return false;

    estado.terminou = true;
    estado.bloqueado = true;
    renderizarTabuleiro();

    if (infoTabuleiro.vencedor) {
      desenharLinhaVitoria(infoTabuleiro.linha_vitoria);
      if (infoTabuleiro.vencedor === estado.simboloHumano) {
        estado.placar.vitorias += 1;
        estado.placar.sequencia += 1;
        atualizarStatus("🎉 Incrível! Você venceu a IA!", "resultado-vitoria");
        tocarSom("vitoria");
      } else {
        estado.placar.derrotas += 1;
        estado.placar.sequencia = 0;
        atualizarStatus("🤖 A IA venceu! Mais sorte na próxima.", "resultado-derrota");
        tocarSom("derrota");
      }
    } else {
      estado.placar.empates += 1;
      estado.placar.sequencia += 1;
      atualizarStatus("🤝 Empate perfeito! Ninguém cedeu espaço.", "resultado-empate");
    }

    salvarPlacar();
    return true;
  }

  async function jogarHumano(posicao) {
    if (estado.bloqueado || estado.terminou || estado.celulas[posicao] !== " ") {
      return;
    }

    estado.celulas[posicao] = estado.simboloHumano;
    estado.bloqueado = true;
    tocarSom("humano");
    adicionarHistorico("Você", estado.simboloHumano, posicao);
    renderizarTabuleiro();

    const linhaLocal = verificarLinhaLocal(estado.celulas);
    const cheioLocal = !estado.celulas.includes(" ");
    if (linhaLocal || cheioLocal) {
      verificarFimDeJogo({
        terminou: true,
        vencedor: linhaLocal ? estado.celulas[linhaLocal[0]] : null,
        linha_vitoria: linhaLocal,
      });
      return;
    }

    await turnoIA();
  }

  function verificarLinhaLocal(c) {
    const linhas = [
      [0, 1, 2], [3, 4, 5], [6, 7, 8],
      [0, 3, 6], [1, 4, 7], [2, 5, 8],
      [0, 4, 8], [2, 4, 6],
    ];
    for (const [a, b, d] of linhas) {
      if (c[a] !== " " && c[a] === c[b] && c[a] === c[d]) {
        return [a, b, d];
      }
    }
    return null;
  }

  async function turnoIA() {
    estado.bloqueado = true;
    atualizarStatus("🤖 IA calculando melhores futuros...", "turno-ia");

    try {
      const resp = await fetch("/api/jogada", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          celulas: estado.celulas,
          simbolo_ia: estado.simboloIA,
          dificuldade: estado.dificuldade,
        }),
      });

      const dados = await resp.json();
      if (!resp.ok) {
        throw new Error(dados.erro || "Erro ao consultar a IA.");
      }

      if (dados.telemetria) {
        telNosEl.textContent = dados.telemetria.nos_avaliados.toLocaleString("pt-BR");
        telTempoEl.textContent = `${dados.telemetria.tempo_ms} ms`;
        telMotivoEl.textContent = dados.telemetria.motivo;
      }

      if (dados.posicao !== null && dados.posicao !== undefined) {
        estado.celulas = dados.tabuleiro.celulas;
        tocarSom("ia");
        adicionarHistorico("IA", estado.simboloIA, dados.posicao);
      }

      estado.bloqueado = false;
      renderizarTabuleiro();

      if (!verificarFimDeJogo(dados.tabuleiro)) {
        atualizarStatus("Sua vez! Escolha uma casa no tabuleiro.", "turno-humano");
      }
    } catch (erro) {
      estado.bloqueado = false;
      atualizarStatus(`⚠️ ${erro.message}`, "resultado-derrota");
    }
  }

  async function atualizarRaioX() {
    if (estado.terminou) return;
    try {
      const resp = await fetch("/api/analisar", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          celulas: estado.celulas,
          simbolo_jogador: estado.simboloHumano,
        }),
      });
      const dados = await resp.json();
      if (!resp.ok || !dados.avaliacoes) return;

      const cells = tabuleiroEl.querySelectorAll(".cell");
      cells.forEach((cell) => {
        const antigo = cell.querySelector(".xray-badge");
        if (antigo) antigo.remove();
      });

      const mapaRotulo = {
        vitoria: "Vitória",
        empate: "Empate",
        derrota: "Derrota",
      };

      dados.avaliacoes.forEach((item) => {
        const cell = cells[item.posicao];
        if (!cell || cell.classList.contains("occupied")) return;
        const badge = document.createElement("span");
        badge.className = `xray-badge xray-${item.desfecho}`;
        badge.textContent = `${mapaRotulo[item.desfecho]} (${item.pontuacao > 0 ? "+" : ""}${item.pontuacao})`;
        cell.appendChild(badge);
      });
    } catch (_) {}
  }

  async function mostrarDica() {
    if (estado.bloqueado || estado.terminou) return;
    try {
      const resp = await fetch("/api/analisar", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          celulas: estado.celulas,
          simbolo_jogador: estado.simboloHumano,
        }),
      });
      const dados = await resp.json();
      if (!resp.ok || dados.melhor_posicao === null) return;

      const cells = tabuleiroEl.querySelectorAll(".cell");
      cells.forEach((c) => c.classList.remove("hint-cell"));
      const alvo = cells[dados.melhor_posicao];
      if (alvo) {
        alvo.classList.add("hint-cell");
        telMotivoEl.textContent = `Dica: jogar na casa ${dados.melhor_posicao + 1} é sua melhor opção (${dados.nos_avaliados} estados simulados).`;
      }
    } catch (_) {}
  }

  async function iniciarNovaPartida() {
    estado.celulas = Array(9).fill(" ");
    estado.terminou = false;
    estado.bloqueado = false;
    estado.historico = [];
    linhaVitoriaEl.classList.remove("visible");
    listaHistoricoEl.innerHTML = '<li class="empty-history">Nenhum lance realizado ainda.</li>';
    telNosEl.textContent = "—";
    telTempoEl.textContent = "—";
    telMotivoEl.textContent = "Nova partida iniciada. Aguardando lance.";

    let comeca = estado.quemComeca;
    if (comeca === "alternar") {
      comeca = estado.proximoInicial;
      estado.proximoInicial = estado.proximoInicial === "humano" ? "ia" : "humano";
    }

    renderizarTabuleiro();

    if (comeca === "ia") {
      await turnoIA();
    } else {
      atualizarStatus("Sua vez! Escolha uma casa no tabuleiro.", "turno-humano");
    }
  }

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

  configurarSegmented("grupo-dificuldade", (valor) => {
    estado.dificuldade = valor;
    iniciarNovaPartida();
  });

  configurarSegmented("grupo-simbolo", (valor) => {
    estado.simboloHumano = valor;
    estado.simboloIA = valor === "X" ? "O" : "X";
    iniciarNovaPartida();
  });

  configurarSegmented("grupo-inicio", (valor) => {
    estado.quemComeca = valor;
    iniciarNovaPartida();
  });

  document.getElementById("btn-reiniciar").addEventListener("click", iniciarNovaPartida);

  document.getElementById("btn-zerar-placar").addEventListener("click", () => {
    estado.placar = { vitorias: 0, empates: 0, derrotas: 0, sequencia: 0 };
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

  document.addEventListener("keydown", (e) => {
    if (e.key >= "1" && e.key <= "9") {
      const idx = parseInt(e.key, 10) - 1;
      jogarHumano(idx);
    } else if (e.key.toLowerCase() === "r") {
      iniciarNovaPartida();
    }
  });

  carregarPlacar();
  iniciarNovaPartida();
})();
