# Código para verificar se o .m3u8 está presente no HTML de uma página da web
# import requests
# import re

# url = "https://g1.globo.com/saude/noticia/2025/10/21/o-revolucionario-implante-ocular-que-ajuda-pacientes-cegos-a-ler-de-novo.ghtml"
# resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
# html = resp.text

# # Procurar links m3u8 com regex
# m3u8_links = re.findall(r'https?://[^\s\'"]+\.m3u8', html)
# print("Links .m3u8 encontrados no HTML:", m3u8_links)

import yt_dlp

def extrair_m3u8(url):
    ydl_opts = {
        "skip_download": True,
        "quiet": True,
        "no_warnings": True,
        "list_formats": True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        formatos = info.get("formats", [])
        m3u8_urls = []
        for f in formatos:
            # Tipicamente: f["ext"] é "m3u8_native" ou "m3u8"
            if f.get("ext") and "m3u8" in f["ext"]:
                m3u8_urls.append({
                    "format_id": f.get("format_id"),
                    "url": f.get("url"),
                    "resolution": f.get("resolution"),
                    "bitrate": f.get("tbr")
                })
        return m3u8_urls

if __name__ == "__main__":
    url = "https://g1.globo.com/saude/noticia/2025/10/21/o-revolucionario-implante-ocular-que-ajuda-pacientes-cegos-a-ler-de-novo.ghtml"
    links = extrair_m3u8(url)
    if links:
        print("Links m3u8 encontrados:")
        for l in links:
            print(l)
    else:
        print("Nenhum link m3u8 encontrado via yt-dlp.")

