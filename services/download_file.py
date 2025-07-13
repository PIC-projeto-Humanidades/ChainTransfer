# download_file client

from pathlib import Path
import requests

RECEIVER_DIR = Path(__file__).resolve().parent.parent / "receiver"
RECEIVER_DIR.mkdir(parents=True, exist_ok=True)

def download_file(ip, file_name):
    url = f"http://{ip}:3000/file/{file_name}"
    tmp_path = RECEIVER_DIR / (file_name + ".part")
    final_path = RECEIVER_DIR / file_name
    tmp_path.parent.mkdir(parents=True, exist_ok=True)

    # Retoma se já existe parcial
    downloaded_bytes = tmp_path.stat().st_size if tmp_path.exists() else 0
    headers = {"Range": f"bytes={downloaded_bytes}-"} if downloaded_bytes else {}

    try:
        res = requests.get(url, headers=headers, stream=True, timeout=30)
        if res.status_code not in (200, 206):
            print(f"⚠️ Falha ao baixar {file_name} — Status {res.status_code}")
            return False

        # Determina tamanho total esperado
        if "Content-Range" in res.headers:
            total_expected = int(res.headers["Content-Range"].split("/")[-1])
        else:
            total_expected = int(res.headers.get("Content-Length", 0))

        mode = "ab" if downloaded_bytes else "wb"
        with open(tmp_path, mode) as f:
            for chunk in res.iter_content(chunk_size=1024*1024):
                if chunk:
                    f.write(chunk)

        current_size = tmp_path.stat().st_size
        if current_size >= total_expected:
            tmp_path.rename(final_path)
            print(f"📥 Download completo: {final_path}")
            return True
        else:
            print(f"⏳ Download parcial: {current_size}/{total_expected} bytes salvos em {tmp_path}")
            return False

    except Exception as e:
        print(f"❌ Erro ao baixar {file_name}: {e}")
        return False
