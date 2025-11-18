# LEIAME
- tentativa de capturar e baixar vídeos de m3u8 de sites;
- utilizamos o JS para capturar os links de m3u8 dinamicamente dos sites;
- inserimos no app Python para baixar estes arquivos TS e concatená-los em MP4;

# JS
versões javascript para monitorar sites e obter links dinâmicos de m3u8

- 04-versao_UI_copiar_link_ultimo_favorito.js - roda pelos favoritos

# PYTHON
Para juntar os TS vamos apenas concatenar eles, não iremos usar o FFMPEG

- main.py - versão inicial em console para baixar e gerar o arquivo MP4
- procurando_m3u8 - versão para tentar encontrar links em páginas web, não funciona para inserções dinâmicas
- qpp_gui_pyqt6 - versão em PyQT6 para baixar os arquivos TS através do link contendo o M3U8, utiliza código do main.py
