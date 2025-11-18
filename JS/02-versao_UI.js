// Versão boa UI mas sem download, mostra último link
(function () {
    // Evitar instalação duplicada
    if (window.__M3U8_MONITOR_UI__) return;
    window.__M3U8_MONITOR_UI__ = true;

    const encontrados = new Set();
    const regex = /\.m3u8(\?[^\s"'<>]*)?$/i;

    // === UI MINIMALISTA ===
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
        cursor: move;
        user-select: text;
        white-space: break-spaces;
    `;
    ui.innerHTML = "Aguardando .m3u8...";
    document.body.appendChild(ui);

    // Permite arrastar a UI
    (function enableDrag(el) {
        let isDown = false, ox = 0, oy = 0;
        el.addEventListener("mousedown", e => {
            isDown = true;
            ox = e.clientX - el.offsetLeft;
            oy = e.clientY - el.offsetTop;
            el.style.transition = "none";
        });
        document.addEventListener("mouseup", () => isDown = false);
        document.addEventListener("mousemove", e => {
            if (!isDown) return;
            el.style.left = (e.clientX - ox) + "px";
            el.style.top  = (e.clientY - oy) + "px";
        });
    })(ui);

    // Atualizar somente o último link exibido
    function atualizarUI(url) {
        ui.textContent = url;
    }

    // Registrar links
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
        const partes = texto.split(/[\s"'<>]+/);
        partes.forEach(p => { if (regex.test(p)) registrar(p); });
    }

    // === 1. Varredura inicial do DOM ===
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
    const obs = new MutationObserver(m => {
        m.forEach(mut => {
            mut.addedNodes.forEach(node => {
                if (node.nodeType === 1) varrerDOM(node);
                else if (node.nodeType === 3) verificarTexto(node.textContent);
            });

            if (mut.type === "attributes") {
                const v = mut.target.getAttribute(mut.attributeName);
                if (v && regex.test(v)) registrar(v);
            }
        });
    });

    obs.observe(document.documentElement, {
        childList: true,
        attributes: true,
        subtree: true
    });

    // === 3. Interceptar fetch ===
    const originalFetch = window.fetch;
    window.fetch = function (...args) {
        const url = args[0];
        if (typeof url === "string" && regex.test(url)) registrar(url);
        return originalFetch(...args);
    };

    // === 4. Interceptar XMLHttpRequest ===
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

    console.log("%cMonitoramento .m3u8 iniciado.", "color:green;font-weight:bold");
    console.log("Último link é exibido na UI flutuante.");
    console.log("Use m3u8_lista() para obter todos os links.");

    window.m3u8_lista = () => Array.from(encontrados);
})();
