from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import firebase_admin
from firebase_admin import credentials, db
import os, json, uuid, time, traceback
import re 
# TODO: biblioteca de filtragem de ofensas
from better_profanity import profanity 


# TODO: ---  CONFIGURAÇÃO DO FILTRO DE OFENSAS ---
profanity.load_censor_words() 
# Se quiser adicionar palavras em português:
PALAVRAS_PT_ADICIONAIS = ['puta', 'caralho', 'merda', 'bosta', 'viado', 'cuzao', 'porra', 'cacete']
profanity.add_censor_words(PALAVRAS_PT_ADICIONAIS)


# TODO --- CONFIGURAÇÃO DO FIREBASE ---

# TODO 1. Chave de Serviço: O arquivo deve estar na mesma pasta.
# ATUALIZADO com a chave fornecida na última interação
FIREBASE_KEY_PATH = "notas-keep-inventory-firebase-adminsdk-fbsvc-43e0dfb35c.json" 

# TODO 2. URL do Realtime Database
DATABASE_URL = "https://notas-keep-inventory-default-rtdb.firebaseio.com/"

# TODO 3. Credenciais (ATUALIZADAS com a chave fornecida)
FIREBASE_KEY_DATA = {
  "type": "service_account",
  "project_id": "notas-keep-inventory",
  "private_key_id": "43e0dfb35c9c301191404a4dd11d56e6013a67ef",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQCnrAj5KvUMBtjf\n8w0xS7CIEr/r2ZePgmRdGueTonNIpbpog7kSuB75ky57Wd8YncgSJ2BMp+7Wrnin\nbIlnQgRJjxV9J6V1Pb4FKG68QlLRA7oR9pvUBd5Dof8jFQnBIAwpwHKy3RWTVV60\nxlh+h1tp+OYtS0S/zUOGCfeLIWATmTUDEhB5QIiulfs8MYKpCguvPJJNTOrL09B5\nYCEKLvNqw3lFHObWoCGUEyh9z0x8oWFVSq7Oz8DRS3zpBjRi2oL4iYYiVqWPUoBG\nbDV4QrKp62FtAewjknKMz/ahZgCzAU6oLW4wffG9FoshZ5SPbjekHd6q1+0mugQm\nMBil7xSJAgMBAAECggEAFNESgiDXsIkPFuq9ig+8GIC/bCAlJW+KV1bWRmmGR5Av\nzvb/nLfYPKMNw8m6HXvFUZ+q4Il+6Q9bMmoSuwuiraFCiTnJXH9wXoKREPVpA8Mj\nMES+PvoFiL8NhoT/o4b/i5V1iAhTu+l+6xGu/fJ/Im6A4UG1hNyOlA8buR3JKFWL\nFLJ2IBA/jZMeNhI/hTFcyUAFioOQMO/mdR00KPZV2i/hZGearDp6kLk7iKKUF2rN\nKGzU0SlYsApjI88dYfQhZzN9OSKVNb7VMA7iawhTvaL8XOpvtXvK51Y+2k14QevV\n7d6l2QZWbdK706z1yN98wBzxAGew8316tzPOKSN56QKBgQDYvHhbSkO0wnDjhfb4\n9nX1G0N4h1GMlrWDBvpUq8SPsbGajXg3i4vG+qqn99cB4b1k77DBs6nbnsXnk6WV\n5y9kshaG4/skSoKJWh8Bl9GjoeItza7Ncgr6ld5b/eebWl1xLfr7FODxgqdyih2T\nitauumEUCRROkH6pEyF8nmrZNQKBgQDGDB/zbsBuPTRP0gcTtmuwrlhgsLGcpWhS\nq1dE+kS75dGepj6JguPwR2PebeWkcr84BzZOY+7S46w66v4SB4WSTQdFAl0BG+iu\nU0MytxdhTwaC9baOJ3wJCYSgHJncgCuuOpuLpMltpu33boD4q3LAILKUAD3v4cbv\ngwytxr7MhQKBgQCt/SbVilmuC4XacDnh5OCuwpM4d9EUfov6QqjFPhsOi8Sa4MTI\nOmMcenBzZPeakCCdnfmUlmleYChZjmKYYz3dpUWGRhB/gr0mDE3l1n250aQjxwFz\n9gAwSA14Zez+/t0Slans1Eb8Ojm4Ln4tyoArRn3WOq+tnju/+Rah1v7JnQKBgA8K\nQq7o/UIh8cQSDimIE/uR8fI92O8tfJOyoWkCnI+sb1PeCifFQewwb7wnmmX3tN/b\nZFtlqXBoi97Zk7voyFMI+IFcIZYA+ZWrixHh56ujJbpyUI/RHdFN4L2MDn85WJfd\nqYxcUlO6dp3wzWiVFJzUntswfYOnIMV1rVPRIRJFAoGBALv0TS3v4FH/wP7z9DWl\nkk5Iru64hZh3pz8N25TXfifb/pSDfqb5gaB/8zeFP88MMt0/3bjJa3hVAQ8MAigl\nkE0F+uQAqY0nrnwDvjhqS6+Bp+G1N5GlTy0nArkZ8cN7q44uIxHUAY5wftwbFlSw\nQybNtLpRSjpbhccnN/ltDphB\n-----END PRIVATE KEY-----\n",
  "client_email": "firebase-adminsdk-fbsvc@notas-keep-inventory.iam.gserviceaccount.com",
  "client_id": "113772746389689089200",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/o/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-fbsvc%40notas-keep-inventory.iam.gserviceaccount.com",
  "universe_domain": "googleapis.com"
}


def init_credentials():
    # TODO Tenta carregar as credenciais do arquivo local, senão usa as credenciais embutidas.
    try:
        if os.path.exists(FIREBASE_KEY_PATH):
            return credentials.Certificate(FIREBASE_KEY_PATH)
        else:
            # TODO Se o arquivo não existir, usa o JSON embutido
            return credentials.Certificate(FIREBASE_KEY_DATA)
    except Exception:
        raise

try:
    cred = init_credentials()
    # TODO Inicializa o Firebase, evitando reinicialização se já estiver rodando.
    if not firebase_admin._apps: 
        firebase_admin.initialize_app(cred, {"databaseURL": DATABASE_URL})
    
    # TODO Referência principal para o nó /produtos no Realtime Database
    ref_notas = db.reference("/produtos") 
    print("✅ Conectado ao Realtime Database com sucesso!")
except Exception as e:
    # TODO Em caso de falha na conexão, exibe o erro e encerra o app.
    print("❌ ERRO FATAL: Falha na inicialização do Firebase. Verifique a chave e a URL.")
    traceback.print_exc()
    raise SystemExit(1)


app = Flask(__name__)
# TODO Habilita CORS para permitir comunicação com o frontend.
CORS(app) 


def validar_texto(texto, min_len, max_len, nome_campo):
    # TODO Valida campos de texto: tamanho, caracteres e ofensas.
    
    # TODO 1. Checa se o campo é obrigatório
    if not texto:
        return f"O campo '{nome_campo}' é obrigatório."
        
    # TODO 2. Checa o tamanho do texto
    if len(texto) < min_len or len(texto) > max_len:
        return f"O campo '{nome_campo}' deve ter entre {min_len} e {max_len} caracteres."
    
    # TODO 3. Restringe a apenas letras, números, espaços e acentos comuns
    if not re.fullmatch(r"^[a-zA-Z0-9áàâãéèêíïóôõúüçÁÀÂÃÉÈÊÍÏÓÔÕÚÜÇ\s]+$", texto):
        return f"O campo '{nome_campo}' contém caracteres inválidos (somente letras, números e espaços)."
    
    # ----------------------------------------------------------------------
    # TODO 4. REGRAS EXCLUSIVAS PARA O CAMPO NOME DO PRODUTO
    # ----------------------------------------------------------------------
    if nome_campo == "Nome do Produto":
        
        # TODO 4a. Verifica se há palavras repetidas seguidas (ex: "Produto Produto")
        if re.search(r"(\w+)\s+\1", texto, re.IGNORECASE):
            return "O campo 'Nome do Produto' não pode ter palavras repetidas seguidas."

        # TODO 4b. Limita a no máximo duas palavras (para forçar "Nome" e "Sobrenome" no máximo)
        palavras = [p for p in texto.split() if p]
        if len(palavras) > 2:
            return "O campo 'Nome do Produto' pode ter no máximo duas palavras (Nome e Sobrenome)."
    # ----------------------------------------------------------------------
    
    # TODO 5. Checagem de Palavrões com a biblioteca Better-Profanity
    if profanity.contains_profanity(texto):
        return f"O campo '{nome_campo}' contém termos proibidos."
            
    return None # TODO Validação OK

# TODO --- ROTAS ESTÁTICAS (SERVE OS ARQUIVOS DO FRONTEND) ---
@app.route('/')
def index():
    # TODO Serve o arquivo HTML principal (index.html).
    return send_from_directory('.', 'index.html')

@app.route('/style.css')
def css():
    # TODO Serve o arquivo CSS.
    return send_from_directory('.', 'style.css')

@app.route('/script.js')
def js():
    # TODO Serve o arquivo JavaScript.
    return send_from_directory('.', 'script.js')

@app.route('/logo.png')
def logo():
    # TODO Serve o arquivo de logo (exemplo).
    return send_from_directory('.', 'logo.png')


# TODO --- ROTAS DA API (CRUD DE PRODUTOS) ---

@app.route('/create_product', methods=['POST'])
def create_product():
    try:
        data = request.json or {}
        
        # TODO 1. Obtenção e Normalização de Campos do JSON
        nome_produto = data.get("nome_produto", "").strip()
        marca = data.get("marca", "").strip()
        categoria = data.get("categoria", "").strip()
        prateleira = data.get("prateleira", "").strip()
        # TODO Normaliza o preço (troca vírgula por ponto para conversão em float)
        preco_str = str(data.get("preco", "")).replace(',', '.') 
        
        # TODO 2. Validação de Campos de Texto
        erro = (
            validar_texto(nome_produto, 3, 100, "Nome do Produto") or
            validar_texto(marca, 2, 50, "Marca") or
            validar_texto(categoria, 3, 50, "Categoria") or
            validar_texto(prateleira, 1, 20, "Prateleira")
        )
        if erro:
            # TODO Retorna erro de validação, impedindo o cadastro.
            return jsonify({"erro": erro}), 400 
            
        # TODO 3. Validação de Preço (Formato e Valor)
        if not re.fullmatch(r"^[0-9]*\.?[0-9]+$", preco_str):
            return jsonify({"erro": "O Preço deve conter apenas números (0-9) e um ponto/vírgula decimal (ex: 33.00)."}), 400
            
        try:
            preco = float(preco_str)
            if preco <= 0:
                return jsonify({"erro": "O Preço deve ser um valor positivo."}), 400
        except ValueError:
            return jsonify({"erro": "O Preço deve ser um número válido."}), 400

        # TODO 4. Criação do Produto no Firebase
        product_id = str(uuid.uuid4())
        product = {
            "id": product_id,
            "nome_produto": nome_produto,
            "marca": marca,
            "categoria": categoria,
            "prateleira": prateleira,
            "preco": f"{preco:.2f}",
            "timestamp": int(time.time()) # TODO Adiciona timestamp de criação/atualização
        }
        
        ref_notas.child(product_id).set(product)
        return jsonify(product), 201 # TODO Retorna o produto criado com status 201 (Created)
        
    except Exception as e:
        # TODO Captura e retorna erros internos do servidor (status 500).
        return jsonify({"erro": f"Erro interno ao criar produto: {str(e)}"}), 500

@app.route('/get_products', methods=['GET'])
def get_products():
    try:
        raw = ref_notas.get()
        if not raw:
            return jsonify([]) # TODO Retorna lista vazia se não houver produtos
            
        produtos = list(raw.values())
        # TODO Ordena os produtos do mais recente para o mais antigo pelo timestamp.
        produtos.sort(key=lambda n: n.get("timestamp", 0), reverse=True)
        
        return jsonify(produtos)
        
    except Exception as e:
        # TODO Captura e retorna erros internos do servidor.
        return jsonify({"erro": f"Erro interno ao buscar produtos: {str(e)}"}), 500

@app.route('/edit_product/<product_id>', methods=['PUT'])
def edit_product(product_id):
    try:
        data = request.json or {}
        updates = {}
        
        # TODO Validação de Campos Individuais:
        
        if "nome_produto" in data:
            nome = data["nome_produto"].strip()
            erro = validar_texto(nome, 3, 100, "Nome do Produto")
            if erro: return jsonify({"erro": erro}), 400
            updates["nome_produto"] = nome
            
        if "marca" in data:
            marca = data["marca"].strip()
            erro = validar_texto(marca, 2, 50, "Marca")
            if erro: return jsonify({"erro": erro}), 400
            updates["marca"] = marca

        if "categoria" in data:
            categoria = data["categoria"].strip()
            erro = validar_texto(categoria, 3, 50, "Categoria")
            if erro: return jsonify({"erro": erro}), 400
            updates["categoria"] = categoria

        if "prateleira" in data:
            prateleira = data["prateleira"].strip()
            erro = validar_texto(prateleira, 1, 20, "Prateleira")
            if erro: return jsonify({"erro": erro}), 400
            updates["prateleira"] = prateleira
            
        if "preco" in data:
            preco_str = str(data["preco"]).replace(',', '.')
            
            # TODO Garante apenas dígitos e ponto
            if not re.fullmatch(r"^[0-9]*\.?[0-9]+$", preco_str):
                return jsonify({"erro": "O Preço deve conter apenas números (0-9) e um ponto/vírgula decimal (ex: 33.00)."}), 400

            try:
                preco = float(preco_str)
                if preco <= 0:
                    return jsonify({"erro": "O Preço deve ser um valor positivo."}), 400
                updates["preco"] = f"{preco:.2f}"
            except ValueError:
                return jsonify({"erro": "O Preço deve ser um número válido."}), 400

        if not updates:
            return jsonify({"erro": "Nada para atualizar."}), 400

        ref = ref_notas.child(product_id)
        # TODO Verifica se o produto existe antes de atualizar.
        if not ref.get():
            return jsonify({"erro": f"Produto com ID '{product_id}' não encontrado"}), 404

        # TODO Adiciona o novo timestamp e realiza a atualização no Firebase.
        updates["timestamp"] = int(time.time())
        ref.update(updates)
        return jsonify({"success": True})
        
    except Exception as e:
        # TODO Captura e retorna erros internos do servidor.
        return jsonify({"erro": f"Erro interno ao editar produto: {str(e)}"}), 500

@app.route('/delete_product/<product_id>', methods=['DELETE'])
def delete_product(product_id):
    try:
        ref = ref_notas.child(product_id)
        # TODO Verifica se o produto existe.
        if not ref.get():
            return jsonify({"erro": f"Produto com ID '{product_id}' não encontrado"}), 404
            
        ref.delete()
        # TODO Retorna sucesso na exclusão.
        return jsonify({"success": True})
        
    except Exception as e:
        # TODO Captura e retorna erros internos do servidor.
        return jsonify({"erro": f"Erro interno ao deletar produto: {str(e)}"}), 500

# TODO --- INICIALIZAÇÃO DO SERVIDOR FLASK ---

if __name__ == '__main__':
    print("\n--- INICIANDO SERVIDOR FLASK ---")
    print(f"ACESSE: http://127.0.0.1:5000/")
    # TODO Roda o servidor na porta padrão 5000 com debug ativado para recarga automática.
    app.run(debug=True, host='0.0.0.0')