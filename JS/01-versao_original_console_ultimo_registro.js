// Versão modificada para capturar apenas o último link m3u8
(function () {

    let ultimoEncontrado = null;
    const regex = /\.m3u8(\?[^\s"'<>]*)?$/i;

    function registrar(url) {
        try {
            const abs = new URL(url, location.href).href;

            if (abs !== ultimoEncontrado) {
                ultimoEncontrado = abs;
                console.log("[ÚLTIMO M3U8 DETECTADO]", abs);
            }

        } catch (e) {}
    }

    function verificarTexto(texto) {
        if (!texto) return;
        const partes = texto.split(/[\s"'<>]+/);
        partes.forEach(p => { 
            if (regex.test(p)) registrar(p);
        });
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

    // === 2. MutationObserver (dinâmico) ===
    const obs = new MutationObserver(mutations => {
        mutations.forEach(m => {
            m.addedNodes.forEach(node => {
                if (node.nodeType === 1) {
                    varrerDOM(node);
                } else if (node.nodeType === 3) {
                    verificarTexto(node.textContent);
                }
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

    // === 3. Interceptar fetch ===
    const originalFetch = window.fetch;
    window.fetch = function (...args) {
        const url = args[0];
        if (typeof url === "string" && regex.test(url)) registrar(url);
        return originalFetch(...args).then(resp => resp);
    };

    // === 4. Interceptar XMLHttpRequest ===
    const OriginalXHR = window.XMLHttpRequest;
    function XHRMonitor() {
        const xhr = new OriginalXHR();
        const open = xhr.open;
        xhr.open = function (method, url, ...rest) {
            if (regex.test(url)) registrar(url);
            return open.call(this, method, url, ...rest);
        };
        return xhr;
    }
    window.XMLHttpRequest = XHRMonitor;

    // === 5. Inicial ===
    varrerDOM();

    console.log("%cMonitoramento .m3u8 iniciado (modo: apenas último link).", "color:green;font-weight:bold");
    console.log("Use m3u8_ultimo() para ver o último link encontrado.");

    // expor apenas o último link
    window.m3u8_ultimo = () => ultimoEncontrado;

})();
