import requests
import os
from urllib.parse import urljoin

def baixar_video(url_m3u8, pasta="video_cap"):
    os.makedirs(pasta, exist_ok=True)

    print("Baixando playlist...")
    m3u8 = requests.get(url_m3u8).text

    segmentos = [l for l in m3u8.splitlines() if l.endswith(".ts")]
    lista_arquivos = []

    for i, seg in enumerate(segmentos):
        url_ts = urljoin(url_m3u8, seg)
        nome_ts = os.path.join(pasta, f"seg{i:04d}.ts")
        print(f"Baixando {seg}...")
        with open(nome_ts, "wb") as f:
            f.write(requests.get(url_ts).content)        
        lista_arquivos.append(nome_ts)

    print("Juntando segmentos...") #Concatenando os arquivos .ts
    with open("resultado.mp4", "wb") as outfile:
        for ts in lista_arquivos:
            with open(ts, "rb") as infile:
                outfile.write(infile.read())

    print("Vídeo final gerado como resultado.mp4!")

#baixar_video("https://vod-as-02-03.video.globo.com/j/eyJhbGciOiJSUzUxMiIsImtpZCI6IjEiLCJ0eXAiOiJKV1QifQ.eyJjb3VudHJ5X2NvZGUiOiJCUiIsImRvbWFpbiI6InZvZC1hcy0wMi0wMy52aWRlby5nbG9iby5jb20iLCJleHAiOjE3NjMzODc3MDgsImlhdCI6MTc2MzM4Njc2MywiaXNzIjoicGxheWJhY2stYXBpLXByb2QtZ2NwIiwib3duZXIiOiIiLCJwYXRoIjoiL3IzNjBfMTA4MC92MC80NC9kMy81NS8xMzk3MzA0Ml81NWI1MDM2MzMwODNjNTMwZjllNGRiZWE3Yzk3OGMwNGVmYWQwODM2LzEzOTczMDQyLWpEd1Zjb0ctbWFuaWZlc3QuaXNtLzEzOTczMDQyLm0zdTgifQ.obNZuA0ABDcX-Fai9GQcUy0Ew-fX8AdcHlAUEsyn9EXANL2epNn8sXX1Pilht5soSkwPtt9ECTJZrkLTihFDU4ip07azhrsLl5r4pQjn4qeif9AIMXEwBEyK-a4IaZMJlLO6lodzM5EYSKSXPtYSkKhoFNjoQDOXHWyLj0zlrP-8rkCQH35d3XddaFI8PCDgitfFtmDCKH1PBzTolC6I_TPbrNP4ip2lLOMpZHUKcP05UZm94z1qcg83lkbxrpnnsHrH8oLXFAi9DcE0ihFAavm-LwkFAiiuDV_POiZGM0nYlnpdXMbuMVmnlR98sd7VUx0N99msfTWZnUqXfa0plA/r360_1080/v0/44/d3/55/13973042_55b503633083c530f9e4dbea7c978c04efad0836/13973042-jDwVcoG-manifest.ism/13973042-jDwVcoG-manifest-audio_por=128005-video_por=3027000.m3u8")
