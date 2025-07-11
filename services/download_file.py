from pathlib import Path
import requests

def download_file(ip, file_name, session_id, node):
    try:
        res = requests.post(f"http://{ip}:3000/ndn/file", json={
            "fileName": file_name,
            "sessao": session_id,
            "node": node
        }, timeout=5)
        if res.status_code in [200, 201]:
            file_path = Path(__file__).resolve().parent.parent / "media_data"
            with open(file_path, 'wb') as f:
                f.write(res.content)
            print(f"Arquivo {file_name} baixado com sucesso.")
            if res.status_code == 201:
                requests.post(f"http://{ip}:3000/monitoring/feedback", json={
                    "fileName": file_name,
                    "sessao": session_id,
                    "node": node
                }, timeout=5)
            return True
        else:
            print(f"Falha ao baixar {file_name} - Status {res.status_code}")
            return False
    except Exception as e:
        print(f"Erro ao baixar {file_name}: {e}")
        return False