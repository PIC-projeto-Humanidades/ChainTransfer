from pathlib import Path
import requests

RECEIVER_DIR = Path(__file__).resolve().parent.parent / "receiver"
RECEIVER_DIR.mkdir(parents=True, exist_ok=True)

def download_file(ip, file_name, session_id, node):
    try:
        res = requests.post(f"http://{ip}:3000/file", json={
            "fileName": file_name,
            "sessao": session_id,
            "node": node
        }, timeout=5)

        if res.status_code in [200, 201]:
            file_path = RECEIVER_DIR / file_name
            file_path.parent.mkdir(parents=True, exist_ok=True)

            with open(file_path, 'wb') as f:
                f.write(res.content)

            print(f"📥 Arquivo {file_name} baixado com sucesso em {file_path}")

            # Envia feedback se necessário
            if res.status_code == 201:
                try:
                    feedback_res = requests.post(f"http://{ip}:3000/monitoring/feedback", json={
                        "fileName": file_name,
                        "sessao": session_id,
                        "node": node
                    }, timeout=5)

                    if feedback_res.status_code in [200, 201]:
                        print("📬 Feedback enviado com sucesso.")

                except Exception as feedback_error:
                    print(f"⚠️ Erro ao enviar feedback: {feedback_error}")

            return True
        else:
            print(f"⚠️ Falha ao baixar {file_name} - Status {res.status_code}")
            return False

    except Exception as e:
        print(f"❌ Erro ao baixar {file_name}: {e}")
        return False
