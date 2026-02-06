from fastapi import FastAPI, Request, HTTPException
import subprocess
import os
import logging

# Configuração de Logs para depuração
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

BASE_APPS_DIR = "/home/felicruel/apps"

@app.post("/update")
async def github_webhook(request: Request):
    payload = await request.json()
    
    # Identifica o nome do repositório (ex: zendesk_manager)
    repo_name = payload.get("repository", {}).get("name")
    
    if not repo_name:
        logger.error("Payload sem nome de repositório")
        raise HTTPException(status_code=400, detail="Payload inválido")

    project_path = os.path.join(BASE_APPS_DIR, repo_name)

    # Verifica se temos esse projeto instalado aqui
    if os.path.exists(project_path):
        logger.info(f"🚀 Iniciando deploy automático: {repo_name}")
        
        # Comando para atualizar: Puxa código -> Reinicia serviço
        # Nota: O sudo aqui exige que o usuário tenha permissão NOPASSWD no sudoers
        command = f"cd {project_path} && git pull origin main && sudo systemctl restart {repo_name}"
        
        try:
            # Executa em background para não travar o GitHub
            subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return {"status": "success", "message": f"Deploy do {repo_name} solicitado."}
        except Exception as e:
            logger.error(f"Erro ao executar deploy: {str(e)}")
            return {"status": "error", "detail": str(e)}
    
    return {"status": "ignored", "message": f"Projeto {repo_name} não monitorado neste servidor."}

@app.get("/")
def health():
    return {"status": "Webhook Online", "ip": "34.11.132.26"}