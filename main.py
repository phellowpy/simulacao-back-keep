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
FIREBASE_KEY_PATH = "notas-keep-inventory-firebase-adminsdk-fbsvc-ae6fa3346d.json" 

# TODO 2. URL do Realtime Database
DATABASE_URL = "https://notas-keep-inventory-default-rtdb.firebaseio.com/"

# TODO 3. Credenciais
FIREBASE_KEY_DATA = {
    "type": "service_account",
    "project_id": "notas-keep-inventory",
    "private_key_id": "ae6fa3346dcc5027f4072668758d7bc015253229",
    "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvwIBADANBgkqhkiG9w0BAQEFAASCBKkwggSlAgEAAoIBAQDSDYiuTSPY0mdh\noUZR1MNh7WTntQt0VKXObcKHFRqYJYOVAnXJ6kFTaPkROfp3uGGt0fsGKniA+1yO\nRSMq/JoLV/jOhiOkrHEl6gBWmKG4wChnC7/53CEge1MtIKr39WHvA/gNihW1VCD1\n6XNdSTqELUC0cTa1V3PKO9ouVZNWxLGFT1ZcFdcMgttPzfqh/8blxMuYwdJOhOI7\nQc+/bSatQfSUiqfsX31F2C72JsNJWTJcY2y9gLJIetZbRb7MNz2xY3++cKXjO8iO\nVZrx8T5L3ctJ04h21LshoCLaLuR9lThJljTyPQKcExgBzAPDBRfjj8OydlkP53tj\nbZb91h87AgMBAAECggEAKYLKMaQGAwnlq1obUv2olRg8mjvhpR47XDW9vUNS66Fy\nRQbk7z/PpCO5IQnjsTgreZXnNVs8UEUcj/Mi1ZJxAO/kODAzKA56F+OMKJDmWOQE\nuASO7lpt44TrtZ3gm7sPHRScn1TEIH8dOmvlxBg+K7PjtyUuihzbwaodXo3D3eAK\ndjpB6ns7Uztu70gQAaLOdhjCWgllrylKjw+A+oPcIFemOHH2np4m1yEngaRXchkN\nu6A7hNiDPpHHWN9Hnxiy9/iyF7DqA7ES05XXmgmLwlSAMHRFRgTdsVHH5dDWwVYi\nAOpacAeAtnfxMT+z6oqu7TECVGnP7YjsUKWuC9AoUQKBgQDx+E0P98qnAb4Bsxs7\nTyNixh6F5j1AaljF+CpTvHN4amNnyoDltbeWTfKLYNuJE3pfZv/CdS3gpuizFV7y\nl+FPYKlLsaoijJTan66oQW88Tg+DpphlwdZPJAGgnfpCh0S9KgkPdqO/gNVE8eqB\nAPoVxuNGloIslKHKXEm/f9cV6wKBgQDeO3g3Vc/pH0fvaOlGtRJ9JhFT6re63Xtj\nPrFLDP1xfwk/L5KbjKwfg3II2UMuTXYRPOJBBFFauhIGmXM8T16Jqco48bm4aIJK\n7akWw9D8r8s+0B7Yif/6qxOgz7R/cnofDVHrnDGu3ThvXkFfc3ODEXUz4KSZSWpS\nK1Jlma838QKBgQDgoq2YR2jhxqJJHagIVZ36Uwd/M5JlvNURZSSWfHuOrO5bJQqp\nNxxq845ait8E0Qpoi0yhkPu4dfvOVebBvPK1KH3DAft6+5wtotUY6zaDe8y3YfBV\nd7Cn5DuGi2MMZFwSaXXj3zaB0O8thJE6lleV5ACXRZ8wGARjw23L1LkvZQKBgQCf\nyOCR4MhBlLUzJRp9NVoa05En5h6+Y9sAq6XsEWX1AeMTJFBkOQvVCLyoMhaEpztZ\n/42qM8GO2zR0vEZHucV+c68rrFndhn8QArtN2/Nai8c13YwgI3ECuZi+Sjk8XYIC\n65/YKRDr81IZeQrF54vJVHcRmtaeRFQGypFO7eY28QKBgQCWYVL/3+mZ1+vdEtJo\nEkNXOknRReht64E2A1nc9Ra2j6TILye/boBmgNHT3hx277H0VsgjbVA6iRfIddjA\nti+p0V97nVf7xhdMM+z/rG5wmONTeuMgKjxg/I2MLO2CkNcFESYJHCUZsiHzPWt+\nDdjMmwMBKdN3cXtrqzZOEx62kQ==\n-----END PRIVATE KEY-----\n",
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
            return credentials.Certificate(FIREBASE_KEY_DATA)
    except Exception:
        raise

try:
    cred = init_credentials()
    # TODO Inicializa o Firebase, evitando reinicialização se já estiver rodando.
    if not firebase_admin._apps: 
        firebase_admin.initialize_app(cred, {"databaseURL": DATABASE_URL})
    
    # TODO Referência principal para o nó /produtos
    ref_notas = db.reference("/produtos") 
    print("✅ Conectado ao Realtime Database com sucesso!")
except Exception as e:
    # TODO Em caso de falha na conexão, exibe o erro e encerra.
    print("❌ ERRO FATAL: Falha na inicialização do Firebase. Verifique a chave e a URL.")
    traceback.print_exc()
    raise SystemExit(1)


app = Flask(__name__)
# TODO Habilita CORS para permitir comunicação com o frontend.
CORS(app) 


def validar_texto(texto, min_len, max_len, nome_campo):
    # TODO Valida campos de texto 
    # TODO Checa se o campo é obrigatório
    if not texto:
        return f"O campo '{nome_campo}' é obrigatório."
        
    # TODO Checa o tamanho do texto
    if len(texto) < min_len or len(texto) > max_len:
        return f"O campo '{nome_campo}' deve ter entre {min_len} e {max_len} caracteres."
    
    # TODO Restringe a apenas letras, números, espaços e acentos comuns
    if not re.fullmatch(r"^[a-zA-Z0-9áàâãéèêíïóôõúüçÁÀÂÃÉÈÊÍÏÓÔÕÚÜÇ\s]+$", texto):
        return f"O campo '{nome_campo}' contém caracteres inválidos (somente letras, números e espaços)."
    
    # TODO Checagem de Palavrões com a biblioteca Better-Profanity
    if profanity.contains_profanity(texto):
        return f"O campo '{nome_campo}' contém termos proibidos."
            
    return None # TODO Validação OK

# TODO --- ROTAS ESTÁTICAS ---
@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/style.css')
def css():
    return send_from_directory('.', 'style.css')

@app.route('/logo.png')
def logo():
    return send_from_directory('.', 'logo.png')


# TODO --- ROTAS DA API ---

@app.route('/create_product', methods=['POST'])
def create_product():
    try:
        data = request.json or {}
        
        # TODO 1. Obtenção e Normalização de Campos
        nome_produto = data.get("nome_produto", "").strip()
        marca = data.get("marca", "").strip()
        categoria = data.get("categoria", "").strip()
        prateleira = data.get("prateleira", "").strip()
        # TODO Preço pode vir com vírgula ou ponto. 
        preco_str = str(data.get("preco", "")).replace(',', '.') 
        
        # TODO 2. Validação de Texto
        erro = (
            validar_texto(nome_produto, 3, 100, "Nome do Produto") or
            validar_texto(marca, 2, 50, "Marca") or
            validar_texto(categoria, 3, 50, "Categoria") or
            validar_texto(prateleira, 1, 20, "Prateleira")
        )
        if erro:
            # TODO Retorna erro de validação, impedindo o cadastro.
            return jsonify({"erro": erro}), 400 
            
        # TODO 3. Validação de Preço e garante apenas dígitos e um ponto decimal opcional
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
        return jsonify(product), 201 # TODO Retorna o produto criado com status 201
        
    except Exception as e:
        # TODO Captura e retorna erros internos do servidor.
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
        
        # TODO Validação de Nome do Produto 
        if "nome_produto" in data:
            nome = data["nome_produto"].strip()
            erro = validar_texto(nome, 3, 100, "Nome do Produto")
            if erro: return jsonify({"erro": erro}), 400
            updates["nome_produto"] = nome
            
        # TODO Validação de Marca 
        if "marca" in data:
            marca = data["marca"].strip()
            erro = validar_texto(marca, 2, 50, "Marca")
            if erro: return jsonify({"erro": erro}), 400
            updates["marca"] = marca

        # TODO Validação de Categoria 
        if "categoria" in data:
            categoria = data["categoria"].strip()
            erro = validar_texto(categoria, 3, 50, "Categoria")
            if erro: return jsonify({"erro": erro}), 400
            updates["categoria"] = categoria

        # TODO Validação de Prateleira 
        if "prateleira" in data:
            prateleira = data["prateleira"].strip()
            erro = validar_texto(prateleira, 1, 20, "Prateleira")
            if erro: return jsonify({"erro": erro}), 400
            updates["prateleira"] = prateleira
            
        # TODO Validação de Preço 
        if "preco" in data:
            preco_str = str(data["preco"]).replace(',', '.')
            
            # Garante apenas dígitos e ponto
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
        # TODO Verifica se o produto existe.
        if not ref.get():
            return jsonify({"erro": f"Produto com ID '{product_id}' não encontrado"}), 404

        # TODO A atualização só ocorre se todas as validações acima passarem.
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

# TODO --- INICIALIZAÇÃO DO SERVIDOR ---

if __name__ == '__main__':
    print("\n--- INICIANDO SERVIDOR FLASK ---")
    print(f"ACESSE: http://127.0.0.1:5000/")
    app.run(debug=True, host='0.0.0.0')