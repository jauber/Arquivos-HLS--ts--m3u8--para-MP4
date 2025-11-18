// Versão com UI e com copiar link, último link apresentado
(function () {
    if (window.__M3U8_MONITOR_UI__) return;
    window.__M3U8_MONITOR_UI__ = true;

    const encontrados = new Set();
    const regex = /\.m3u8(\?[^\s"'<>]*)?$/i;

    // === UI FLUTUANTE COM BOTÃO ===
    const ui = document.createElement("div");
    ui.id = "m3u8-ui";
    ui.style.cssText = `
        position: fixed;
        bottom: 20px;
        right: 20px;
        z-index: 999999999;
        background: rgba(0,0,0,0.85);
        padding: 12px 14px;
        border-radius: 8px;
        color: #0f0;
        font-size: 13px;
        max-width: 380px;
        font-family: Consolas, monospace;
        box-shadow: 0 0 10px #000;
        backdrop-filter: blur(3px);
        white-space: break-spaces;
    `;

    ui.innerHTML = `
        <div id="m3u8-last">Aguardando .m3u8...</div>
        <button id="m3u8-copy-btn"
            style="
                margin-top: 5px;
                padding: 6px 5px;
                border: none;
                border-radius: 5px;
                background: #444;
                color: #fff;
                cursor: pointer;
                font-size: 12px;
                width: 100%;
            ">
            Copiar link
        </button>
    `;

    document.body.appendChild(ui);

    const lastEl = document.getElementById("m3u8-last");
    const copyBtn = document.getElementById("m3u8-copy-btn");

    // === Ação do botão ===
    copyBtn.addEventListener("click", () => {
        const texto = lastEl.textContent.trim();
        if (!texto || texto === "Aguardando .m3u8...") return;

        navigator.clipboard.writeText(texto).then(() => {
            copyBtn.textContent = "Copiado!";
            setTimeout(() => (copyBtn.textContent = "Copiar link"), 1500);
        });
    });

    // === Para atualizar o último link ===
    function atualizarUI(url) {
        lastEl.textContent = url;
    }

    function registrar(url) {
        try {
            const abs = new URL(url, location.href).href;
            if (!encontrados.has(abs)) {
                encontrados.add(abs);
                atualizarUI(abs);
                console.log("[M3U8 DETECTADO]", abs);
            }
        } catch {}
    }

    function verificarTexto(texto) {
        if (!texto) return;
        texto.split(/[\s"'<>]+/).forEach(p => {
            if (regex.test(p)) registrar(p);
        });
    }

    // === 1. Varredura ===
    function varrerDOM(root = document) {
        const attrs = ["src", "href", "data-src", "data-href", "poster", "content"];
        const elementos = root.querySelectorAll("*");

        elementos.forEach(el => {
            attrs.forEach(a => {
                const v = el.getAttribute && el.getAttribute(a);
                if (v && regex.test(v)) registrar(v);
            });

            if (el.innerText && regex.test(el.innerText)) verificarTexto(el.innerText);
        });
    }

    // === 2. MutationObserver ===
    const obs = new MutationObserver(muts => {
        muts.forEach(m => {
            m.addedNodes.forEach(node => {
                if (node.nodeType === 1) varrerDOM(node);
                else if (node.nodeType === 3) verificarTexto(node.textContent);
            });

            if (m.type === "attributes") {
                const v = m.target.getAttribute(m.attributeName);
                if (v && regex.test(v)) registrar(v);
            }
        });
    });

    obs.observe(document.documentElement, {
        childList: true,
        attributes: true,
        subtree: true
    });

    // === 3. Interceptar FETCH ===
    const originalFetch = window.fetch;
    window.fetch = function (...args) {
        const url = args[0];
        if (typeof url === "string" && regex.test(url)) registrar(url);
        return originalFetch(...args);
    };

    // === 4. Interceptar XHR ===
    const OriginalXHR = window.XMLHttpRequest;
    window.XMLHttpRequest = function () {
        const xhr = new OriginalXHR();
        const open = xhr.open;
        xhr.open = function (method, url, ...rest) {
            if (regex.test(url)) registrar(url);
            return open.call(this, method, url, ...rest);
        };
        return xhr;
    };

    // === 5. Inicial ===
    varrerDOM();

    window.m3u8_lista = () => Array.from(encontrados);
    console.log("%cMonitoramento .m3u8 iniciado com UI + botão copiar.", "color:lightgreen;font-weight:bold");
})();
