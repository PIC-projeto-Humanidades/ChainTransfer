from pathlib import Path
import requests

RECEIVER_DIR = Path(__file__).resolve().parent.parent / "receiver"
RECEIVER_DIR.mkdir(parents=True, exist_ok=True)

def download_file(ip, file_name):
    try:
        url = f"http://{ip}:3000/file/{file_name}"
        res = requests.get(url, stream=True)

        if res.status_code in [200, 201]:
            file_path = RECEIVER_DIR / file_name
            file_path.parent.mkdir(parents=True, exist_ok=True)

            with open(file_path, 'wb') as f:
                for chunk in res.iter_content(chunk_size=1024 * 1024):  # 1 MB por vez
                    if chunk:
                        f.write(chunk)

            print(f"📥 Arquivo {file_name} baixado com sucesso em {file_path}")
            return True
        else:
            print(f"⚠️ Falha ao baixar {file_name} - Status {res.status_code}")
            return False

    except Exception as e:
        print(f"❌ Erro ao baixar {file_name}: {e}")
        return False
