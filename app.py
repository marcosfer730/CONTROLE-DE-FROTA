import os
from flask import Flask, render_template, request, redirect, url_for, flash, session
from models.estacionamento import Estacionamento
from models.veiculo import Veiculo
from pymongo import MongoClient
from functools import wraps
from flask import make_response
from werkzeug.security import generate_password_hash, check_password_hash
from bson.objectid import ObjectId
from datetime import datetime
from flask import make_response

def nocache(view):
    @wraps(view)
    def no_cache(*args, **kwargs):
        response = make_response(view(*args, **kwargs))
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "-1"
        return response
    return no_cache

def get_current_user():
    user_id = session.get('user_id')
    if user_id:
        usuario = usuarios_collection.find_one({'_id': ObjectId(user_id)})
        return usuario
    return None


# Conexão com o MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['estacionamento_db']
collection = db['veiculos']# Nome da coleção
usuarios_collection = db['usuarios']
pedidos_collection = db['pedidos']
administradores_collection = db['administradores']

app = Flask(__name__, template_folder='templates', static_folder='static')
app.secret_key = os.urandom(24)  # Gera uma chave secreta aleatória
estacionamento = Estacionamento()
administradores = db["administradores"]  # Define a coleção 'administradores'

@app.context_processor
def inject_usuario():
    usuario = get_current_user()
    return dict(usuario=usuario)

# Filtro personalizado para converter string para datetime
@app.template_filter('to_datetime')
def to_datetime(value, format='%d/%m/%Y %H:%M:%S'):
    if isinstance(value, str):
        return datetime.strptime(value, format)
    return value

# Rota para a página inicial
@app.route('/')
def index():
    return render_template('index.html')

#lista de usarios admin 
@app.route('/9876543210_usuarios')
def mostrar_usuarios_administradores():
    # Recupera todos os usuários administradores da coleção
    usuarios = administradores.find()
    return render_template('9399000288.html', usuarios=usuarios)

# rota pra area restrita
@app.route('/panneel_geraal', methods=['GET', 'POST'])
def painle_gerall():
    # Verifica se o usuário ja fez login
    if not session.get('logged_in'):  # se não estiver logado, redireciona
        flash('Acesso restrito. Login necessáreo', 'warnning')
        return redirect(url_for('login_usuario'))
    
    # Método POST pra cadastrar novo admin
    if request.method == 'POST':
        # pega o nome de usuario e senha do form
        user_aliaz = request.form['user_alias']
        acess_kay = request.form['access_key']
        
        # Checa se já existe esse usuario no bd
        if administradores.find_one({"nome": user_aliaz}):  # verifica no BD
            flash('User já exixtente!', 'danger')
        else:
            # insere o novo admin na colecao "administradores"
            administradores.insert_one({"nome": user_aliaz, "senha": acess_kay})
            flash('Novo user adcionado com sucesso!', 'succes')
            return redirect(url_for('listar_usuarios'))  # volta para listagem

    return render_template('painel_geral.html')  # renderiza o HTML de admin

#editar usuario
@app.route('/editar_usuario/<id>', methods=['GET', 'POST'])
def editar_usuario(id):
    # Aqui você deve buscar o usuário pelo id
    usuario = administradores.find_one({"_id": ObjectId(id)})  # Importante: use ObjectId se estiver usando MongoDB

    if request.method == 'POST':
        # Se o método for POST, você pode atualizar o usuário
        novo_nome = request.form['user_alias']
        nova_senha = request.form['access_key']
        
        # Atualiza o usuário no banco de dados
        administradores.update_one({"_id": ObjectId(id)}, {"$set": {"nome": novo_nome, "senha": nova_senha}})
        flash('Usuário atualizado com sucesso!', 'success')
        return redirect(url_for('listar_usuarios'))

    return render_template('editar_usuario.html', usuario=usuario)  # Renderiza o template de edição


# Rota de login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Consulta o banco de dados para verificar o usuário e senha
        administrador = administradores.find_one({"nome": username, "senha": password})
        
        if administrador:
            # Configura a sessão do usuário logado
            session['logged_in'] = True
            session['user_id'] = str(administrador['_id'])
            flash('Login realizado com sucesso!', 'success')
            
            # Redirecionamento com base no usuário
            if username == 'admin':
                return redirect(url_for('inserir_dados'))
            elif username == 'info':
                return redirect(url_for('cadastrar_usuario'))
        else:
            flash('Credenciais inválidas!', 'danger')
    
    return render_template('login.html')

@app.route('/registrar_entrada', methods=['GET', 'POST'])     
def registrar_entrada():
    mensagem_erro = None  # Inicializa a variável de erro

    # Organiza motoristas no banco de dados
    lista_motoristas = []
    for motorista in db['motoristas'].find():  # Coleção de motoristas
        nome_motorista = motorista['nome']  # Supondo que a chave seja 'nome'
        lista_motoristas.append(nome_motorista)  # Adiciona o nome do motorista à lista

    # Coleta setores disponíveis
    setores = list(db['setores'].find({}, {'_id': 0, 'setor': 1}))
    lista_setores = [setor['setor'] for setor in setores]

    # Coleta todas as viaturas disponíveis 
    viaturas = list(db['viaturas'].find({}, {'_id': 0, 'placa': 1, 'modelo': 1}))
    lista_viaturas = [{'placa': viatura['placa'], 'modelo': viatura['modelo']} for viatura in viaturas]

    if request.method == 'POST':
        motorista = request.form['motorista']
        placa = request.form['veiculo'].strip().upper()  # Corrigido para pegar da variável correta
        hodometro = request.form['hodometro']
        setor = request.form['setor']  # Coleta o setor do formulário

        # Captura a hora de entrada como objeto datetime
        hora_entrada = datetime.now().strftime('%d/%m/%Y %H:%M:%S')

        # Verifica se o veículo está na coleção 'viaturas'
        veiculo_dados = db['viaturas'].find_one({'placa': placa})

        if not veiculo_dados:
            mensagem_erro = f'Veículo com placa {placa} não encontrado.'
            return render_template('registrar_entrada.html', mensagem_erro=mensagem_erro, lista_motoristas=lista_motoristas, lista_setores=lista_setores, lista_viaturas=lista_viaturas)

        # Obtém o modelo da viatura
        modelo = veiculo_dados['modelo']

        # Verifica se o veículo já está com status ativo
        veiculo_existente = db['viaturas'].find_one({'placa': placa, 'status': 'ativo'})

        if veiculo_existente:
            mensagem_erro = f'O veículo com placa {placa} já está registrado como ativo.'
            return render_template('registrar_entrada.html', mensagem_erro=mensagem_erro, lista_motoristas=lista_motoristas, lista_setores=lista_setores, lista_viaturas=lista_viaturas)

        # Se o veículo não existe ou não está ativo, registra-o como ativo
        try:
            db['viaturas'].update_one(
                {'placa': placa},
                {
                    '$set': {
                        'hora_entrada': hora_entrada,
                        'status': 'ativo',
                        'hodometro': float(hodometro)
                    }
                },
                upsert=True  # Insere se não existir
            )

            # Registrar no relatorios.txt
            with open('relatorios.csv', 'a') as file:
                file.write(f"{placa}/{modelo},{motorista},{hodometro},{setor}," 
                           f"{hora_entrada},\n")  # Inclui o setor no registro
            
        except Exception as e:
            mensagem_erro = f'Erro ao registrar veículo no banco de dados: {str(e)}'
            return render_template('registrar_entrada.html', mensagem_erro=mensagem_erro, lista_motoristas=lista_motoristas, lista_setores=lista_setores, lista_viaturas=lista_viaturas)

        return redirect(url_for('listar_veiculos'))

    return render_template('registrar_entrada.html', mensagem_erro=mensagem_erro, lista_motoristas=lista_motoristas, lista_setores=lista_setores, lista_viaturas=lista_viaturas)

# Rota para inserir dados (protegido por login)
@app.route('/inserir_dados', methods=['GET', 'POST'])
@nocache
def inserir_dados():
    # Verifica se o usuário está logado
    if 'logged_in' not in session:
        flash('Por favor, faça login primeiro.', 'warning')
        return redirect(url_for('login'))  # Redireciona para a página de login

    mensagem = ''  # Variável para armazenar a mensagem

    if request.method == 'POST':
        motorista = request.form.get('motorista')
        placa_modelo = request.form.get('placa_modelo')  # Campo único para placa/modelo
        setor = request.form.get('setor')  # Supondo que você tenha um campo para setor

        try:
            if motorista:
                # Registrar no MongoDB na coleção 'motoristas'
                db['motoristas'].insert_one({'nome': motorista})

            if placa_modelo:
                # Dividir a entrada em placa e modelo
                placa, modelo = placa_modelo.split('/', 1)  # Divide em até duas partes
                # Registrar no MongoDB na coleção 'veiculos' com placa e modelo
                db['veiculos'].insert_one({
                    'placa': placa.strip(),  # Remove espaços em branco
                    'modelo': modelo.strip()  # Remove espaços em branco
                })

            if setor:
                # Registrar no MongoDB na coleção 'setores'
                db['setores'].insert_one({'setor': setor})

            mensagem = 'Dados registrados com sucesso'  # Mensagem de sucesso

        except Exception as e:
            mensagem = f'Erro ao registrar dados: {str(e)}'  # Mensagem de erro

    return render_template('registro_dados.html', mensagem=mensagem)  # Página de inserção de dados com a mensagem

# Rota para listar veículos registrados
@app.route('/listar_veiculos')
def listar_veiculos():
    # Obtém os veículos registrados do MongoDB que estão ativos
    veiculos_ativos = list(db['viaturas'].find({'status': 'inativo'}))

    return render_template('veiculos.html', veiculos=veiculos_ativos)



@app.route('/registrar_saida', methods=['GET', 'POST'])     
def registrar_saida():
    # Coleta todas as placas e modelos das viaturas disponíveis
    viaturas = {}
    for viatura in db['viaturas'].find():
        placa = viatura['placa']
        modelo = viatura['modelo']
        viaturas[placa] = modelo

    # Coleta motoristas da coleção 'motoristas'
    motoristas = [motorista['nome'] for motorista in db['motoristas'].find()]
    mensagem_saida = None

    if request.method == 'POST':
        motorista = request.form['motorista'].strip()
        placa = request.form['placa'].strip().upper()
        modelo = viaturas.get(placa, "")
        hodometro_saida = request.form['hodometro_saida']

        # Validação do hodômetro
        try:
            hodometro_saida = int(float(hodometro_saida))
        except ValueError:
            mensagem_saida = "O valor do hodômetro de saída deve ser numérico."
            return render_template('registrar_saida.html', viaturas=viaturas, motoristas=motoristas, mensagem_saida=mensagem_saida)

        viatura_dados = db['viaturas'].find_one({'placa': placa})

        if not viatura_dados:
            mensagem_saida = f'Veículo com placa {placa} não encontrado.'
            return render_template('registrar_saida.html', viaturas=viaturas, motoristas=motoristas, mensagem_saida=mensagem_saida)

        if viatura_dados['status'] != 'ativo':
            mensagem_saida = f'A viatura {placa} já foi registrada como saída.'
            return render_template('registrar_saida.html', viaturas=viaturas, motoristas=motoristas, mensagem_saida=mensagem_saida)

        hodometro_entrada = viatura_dados.get('hodometro', None)
        if hodometro_entrada is not None and hodometro_saida < hodometro_entrada:
            mensagem_saida = f'O hodômetro de saída deve ser maior ou igual ao hodômetro de entrada: {hodometro_entrada} km.'
            return render_template('registrar_saida.html', viaturas=viaturas, motoristas=motoristas, mensagem_saida=mensagem_saida)

        # Atualiza o relatório
        linhas = []
        veiculo_encontrado = False
        with open('relatorios.csv', 'r') as file:
            linhas = file.readlines()

        for i in range(len(linhas) - 1, -1, -1):
            dados = linhas[i].strip().split(',')
            if dados[0] == f"{placa}/{modelo}" and dados[1] == motorista and len(dados) >= 5:
                linha_atualizada = f"{placa}/{modelo},{motorista},{dados[2]},{dados[3]}," \
                                   f"{dados[4]},{hodometro_saida}," \
                                   f"{datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n"
                linhas[i] = linha_atualizada
                veiculo_encontrado = True
                break

        if veiculo_encontrado:
            with open('relatorios.csv', 'w') as file:
                file.writelines(linhas)

        # Atualiza os dados no banco de dados
        result = db['viaturas'].update_one(
            {'placa': placa, 'status': 'ativo'},
            {'$set': {
                'hora_saida': datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
                'hodometro_saida': hodometro_saida,
                'status': 'inativo'
            }}
        )

        if result.modified_count > 0:
            mensagem_saida = f'Veículo {placa} registrado como saída com sucesso.'
        else:
            mensagem_saida = f'Não foi possível atualizar o status da viatura {placa}. Ela pode já estar inativa.'

        return render_template('registrar_saida.html', viaturas=viaturas, motoristas=motoristas, mensagem_saida=mensagem_saida)

    return render_template('registrar_saida.html', viaturas=viaturas, motoristas=motoristas)

@app.route('/registros_anteriores', methods=['GET', 'POST'])
def registros_anteriores():
    registros = []
    log_file = 'relatorios.csv'
    
    # Inicializa as variáveis de data
    data_inicial = None
    data_final = None

    # Listas para os dropdowns
    placas = set()
    motoristas = set()
    setores = set()

    if request.method == 'POST':
        data_inicial = request.form.get('data_inicial')
        data_final = request.form.get('data_final')
        placa_selecionada = request.form.get('placa')  # Adicionado
        motorista_selecionado = request.form.get('motorista')  # Adicionado
        setor_selecionado = request.form.get('setor')  # Adicionado

        # Converte as datas se ambas estiverem presentes
        if data_inicial and data_final:
            try:
                data_inicial = datetime.strptime(data_inicial, '%Y-%m-%d')
                data_final = datetime.strptime(data_final, '%Y-%m-%d')
            except ValueError:
                flash('Formato de data inválido. Use AAAA-MM-DD.', 'danger')
                return redirect(url_for('registros_anteriores'))

    try:
        if os.path.exists(log_file):
            with open(log_file, 'r') as file:
                linhas = file.readlines()
                for linha in linhas:
                    linha = linha.strip()
                    dados = linha.split(',')

                    if len(dados) >= 7:  # Garantindo que tenhamos pelo menos 7 campos
                        try:
                            # Extraindo os dados
                            placa_modelo = dados[0].strip()  # SSL1C40/COROLLA
                            motorista = dados[1].strip()  # Sd Breno
                            hodometro_entrada = dados[2].strip()  # 12
                            setor = dados[3].strip()  # TIC
                            hora_entrada = datetime.strptime(dados[4].strip(), '%d/%m/%Y %H:%M:%S')  # 01/11/2024 15:10:09
                            hodometro_saida = dados[5].strip() if dados[5].strip() != '-' else None  # 12
                            hora_saida = datetime.strptime(dados[6].strip(), '%d/%m/%Y %H:%M:%S') if len(dados) > 6 and dados[6].strip() != '-' else None  # 01/11/2024 15:10:51
                            
                            # Separando placa e modelo
                            placa, modelo = placa_modelo.split('/')

                            # Adicionando valores aos dropdowns
                            placas.add(placa.strip())
                            motoristas.add(motorista)
                            setores.add(setor)

                            # Verifica se a hora_entrada está dentro do intervalo fornecido
                            if data_inicial and data_final:
                                if data_inicial.date() <= hora_entrada.date() <= data_final.date():
                                    # Verificando se a placa, motorista e setor estão selecionados
                                    if (placa_selecionada == '' or placa.strip() == placa_selecionada) and \
                                       (motorista_selecionado == '' or motorista == motorista_selecionado) and \
                                       (setor_selecionado == '' or setor == setor_selecionado):
                                        registros.append({
                                            'placa': placa.strip(),
                                            'modelo': modelo.strip(),
                                            'motorista': motorista,
                                            'hodometro_entrada': hodometro_entrada,
                                            'setor': setor,
                                            'hora_entrada': hora_entrada,
                                            'hodometro_saida': hodometro_saida,
                                            'hora_saida': hora_saida,
                                            'km_dif': (int(hodometro_saida) - int(hodometro_entrada)) if hodometro_saida and hodometro_entrada else None
                                        })
                            else:
                                # Se não houver filtro, exibe apenas registros do dia atual
                                if hora_entrada.date() == datetime.now().date():  # Adicionado
                                    registros.append({
                                        'placa': placa.strip(),
                                        'modelo': modelo.strip(),
                                        'motorista': motorista,
                                        'hodometro_entrada': hodometro_entrada,
                                        'setor': setor,
                                        'hora_entrada': hora_entrada,
                                        'hodometro_saida': hodometro_saida,
                                        'hora_saida': hora_saida,
                                        'km_dif': (int(hodometro_saida) - int(hodometro_entrada)) if hodometro_saida and hodometro_entrada else None
                                    })
                        except Exception as e:
                            flash(f'Erro ao processar a linha: {linha}. Detalhes: {str(e)}', 'danger')
    except Exception as e:
        flash(f'Erro ao ler os registros: {str(e)}', 'danger')

    return render_template('registros_anteriores.html', registros=registros, placas=sorted(placas), motoristas=sorted(motoristas), setores=sorted(setores))

# Rota para logout
@app.route('/logout')
def logout():
    session.pop('logged_in', None)  # Remove o status de login da sessão
    flash('Você saiu com sucesso.', 'success')
    return redirect(url_for('login'))  # Redireciona para a página de login

#SEGUNDA PARTE DO CODIGO #SEGUNDA PARTE DO CODIGO #SEGUNDA PARTE DO CODIGO #SEGUNDA PARTE DO CODIGO #SEGUNDA PARTE DO CODIGO #SEGUNDA PARTE DO CODIGO 
#SEGUNDA PARTE DO CODIGO #SEGUNDA PARTE DO CODIGO #SEGUNDA PARTE DO CODIGO #SEGUNDA PARTE DO CODIGO #SEGUNDA PARTE DO CODIGO #SEGUNDA PARTE DO CODIGO 
#SEGUNDA PARTE DO CODIGO #SEGUNDA PARTE DO CODIGO #SEGUNDA PARTE DO CODIGO #SEGUNDA PARTE DO CODIGO #SEGUNDA PARTE DO CODIGO #SEGUNDA PARTE DO CODIGO 
#SEGUNDA PARTE DO CODIGO #SEGUNDA PARTE DO CODIGO #SEGUNDA PARTE DO CODIGO #SEGUNDA PARTE DO CODIGO #SEGUNDA PARTE DO CODIGO #SEGUNDA PARTE DO CODIGO 

# Rota para cadastrar um novo usuário
@app.route('/cadastrar_usuario', methods=['GET', 'POST'])
def cadastrar_usuario():
    if 'logged_in' in session:
        if request.method == 'POST':
            nome = request.form['nome']
            setor = request.form['setor']
            email = request.form['email']
            senha = request.form['senha']
            confirmar_senha = request.form['confirmar_senha']

            if senha != confirmar_senha:
                flash('As senhas não coincidem. Tente novamente.', 'danger')
                return redirect(url_for('cadastrar_usuario'))
            
            if usuarios_collection.find_one({'email': email}):
                flash('Este e-mail já está cadastrado. Tente outro.', 'danger')
                return redirect(url_for('cadastrar_usuario'))

            senha_criptografada = generate_password_hash(senha)
            usuarios_collection.insert_one({
                'nome': nome,
                'setor': setor,
                'email': email,
                'senha': senha_criptografada
            })
            flash('Usuário cadastrado com sucesso!', 'success')
            return redirect(url_for('lista_usuarios'))

        return render_template('cadastrar_usuario.html')
    else:
        flash('Você precisa estar logado para cadastrar um usuário.', 'danger')
        return redirect(url_for('login_usuario'))


@app.route('/pedido_viatura', methods=['GET', 'POST'])
def pedido_viatura():
    # Verifica se o usuário está logado
    if 'user_id' not in session:
        flash('Você precisa estar logado para fazer um pedido.', 'warning')
        return redirect(url_for('login_usuario'))

    if request.method == 'POST':
        try:
            # Captura os dados do formulário
            usuario_id = session['user_id']
            nome_solicitante = request.form.get('nome_solicitante')
            motorista = request.form.get('motorista')
            motivo_pedido = request.form.get('motivo_pedido')
            tipo_viatura = request.form.get('tipo_viatura')
            numero_passageiros = request.form.get('numero_passageiros')
            itinerario = request.form.get('itinerario')
            observacoes = request.form.get('observacoes', '')

            # Verifica se o usuário optou por usar a data e hora atual
            if request.form.get('usar_data_atual'):
                data_hora_pedido = datetime.now()
            else:
                data_hora_pedido_str = request.form.get('data_hora_solicitacao')
                if data_hora_pedido_str:
                    data_hora_pedido = datetime.strptime(data_hora_pedido_str, '%Y-%m-%dT%H:%M')
                else:
                    data_hora_pedido = datetime.now()

            # Criação do pedido a ser inserido no banco de dados
            pedido_data = {
                'usuario_id': usuario_id,
                'nome_solicitante': nome_solicitante,
                'motorista': motorista,
                'motivo_pedido': motivo_pedido,
                'tipo_viatura': tipo_viatura,  # Confirma o nome do campo para 'tipo_viatura'
                'numero_passageiros': numero_passageiros,
                'itinerario': itinerario,
                'observacoes': observacoes,
                'data_hora_pedido': data_hora_pedido,
                'status': 'pendente'
            }

            pedidos_collection.insert_one(pedido_data)

            # Registrar no relapedido.csv
            with open('relapedido.csv', 'a') as file:
                file.write(f"{nome_solicitante},{motorista},{motivo_pedido},{tipo_viatura},{numero_passageiros},"
                           f"{itinerario},{observacoes},{data_hora_pedido.strftime('%d/%m/%Y %H:%M:%S')}\n")

            flash('Pedido de viatura enviado com sucesso!', 'success')

        except Exception as e:
            flash(f'Ocorreu um erro ao processar seu pedido: {str(e)}', 'danger')
            return redirect(url_for('pedido_viatura'))

        # Redireciona para o dashboard após o envio bem-sucedido
        return redirect(url_for('dashboard'))

  
    return render_template('dashboard.html')

# Rota para atender o pedido e registrar o retorno à garagem
@app.route('/retorno_garagem', methods=['GET', 'POST'])
@app.route('/retorno_garagem/<pedido_id>', methods=['GET', 'POST'])
def retorno_garagem(pedido_id=None):
    if request.method == 'POST':
        pedido_id = request.form.get('pedido_id') or pedido_id
        motorista = request.form.get('motorista')
        viatura = request.form.get('viatura')
        data_hora_atendimento = datetime.now()

        if not pedido_id:
            flash('ID do pedido não foi fornecido.', 'danger')
            return redirect(url_for('listar_pedidos'))

        result = pedidos_collection.update_one(
            {'_id': ObjectId(pedido_id)},
            {'$set': {
                'status': 'Atendido',
                'data_hora_atendimento': data_hora_atendimento,
                'motorista': motorista,
                'tipo_viatura': viatura
            }}
        )

        with open('relapedido.csv', 'a') as file:
            file.write(f"{data_hora_atendimento},{motorista},{viatura}\n")

        if result.modified_count == 0:
            flash('Nenhum pedido foi atualizado. Verifique se o ID está correto.', 'danger')
            return redirect(url_for('dash'))

        flash('Pedido atendido com sucesso!', 'success')
        return redirect(url_for('dash'))

    if pedido_id:
        pedido = pedidos_collection.find_one({'_id': ObjectId(pedido_id)})
        if pedido:
            return render_template('retorno_garagem.html', pedido=pedido)

    flash('Pedido não encontrado.', 'danger')
    return redirect(url_for('dash', pedido=pedido))

# Rota para gerar relatório dos pedidos por solicitante
@app.route('/relatorios', methods=['GET'])
def relatorios():
    relatorios = db.pedidos.aggregate([
        {
            '$group': {
                '_id': '$nome_solicitante',
                'total_pedidos': {'$sum': 1}
            }
        }
    ])
    return render_template('dash.html', relatorios=relatorios)

# Rota para listar pedidos pendentes
@app.route('/listar_pedidos')
def listar_pedidos():
    pedidos_pendentes = list(pedidos_collection.find({'status': 'pendente'}))

    for pedido in pedidos_pendentes:
        data_hora_pedido = pedido.get('data_hora_pedido')
        if isinstance(data_hora_pedido, datetime):
            pedido['data_hora_pedido'] = data_hora_pedido.strftime('%d/%m/%Y %H:%M')
        else:
            pedido['data_hora_pedido'] = "Data não disponível"

    return render_template('dash.html', pedidos=pedidos_pendentes)


#AREA USUARIO#AREA USUARIO#AREA USUARIO#AREA USUARIO#AREA USUARIO#AREA USUARIO#AREA USUARIO#AREA USUARIO#AREA USUARIO#AREA USUARIO
#AREA USUARIO#AREA USUARIO#AREA USUARIO#AREA USUARIO#AREA USUARIO#AREA USUARIO#AREA USUARIO#AREA USUARIO#AREA USUARIO#AREA USUARIO
#AREA USUARIO#AREA USUARIO#AREA USUARIO#AREA USUARIO#AREA USUARIO#AREA USUARIO#AREA USUARIO#AREA USUARIO#AREA USUARIO#AREA USUARIO
#AREA USUARIO#AREA USUARIO#AREA USUARIO#AREA USUARIO#AREA USUARIO#AREA USUARIO#AREA USUARIO#AREA USUARIO#AREA USUARIO#AREA USUARIO
#AREA USUARIO#AREA USUARIO#AREA USUARIO#AREA USUARIO#AREA USUARIO#AREA USUARIO#AREA USUARIO#AREA USUARIO#AREA USUARIO#AREA USUARIO#

# Rota para login de usuário ou administrador
@app.route('/login_usuario', methods=['GET', 'POST'])
def login_usuario():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Verificar se é um usuário comum
        usuario = usuarios_collection.find_one({"nome": username})
        if usuario and check_password_hash(usuario['senha'], password):
            session['user_id'] = str(usuario['_id'])
            session['logged_in'] = True
            session['user_role'] = 'usuario'
            flash('Login realizado com sucesso!', 'success')
            return redirect(url_for('dashboard'))

        # Verificar se é um administrador
        administrador = administradores_collection.find_one({"nome": username})
        if administrador and check_password_hash(administrador['senha'], password):
            session['user_id'] = str(administrador['_id'])
            session['logged_in'] = True
            session['user_role'] = 'administrador'
            flash('Login de administrador realizado com sucesso!', 'success')
            return redirect(url_for('dash'))

        # Caso as credenciais estejam incorretas
        flash('Nome de usuário ou senha incorretos.', 'danger')
    return render_template('login_usuario.html')

# Rota para o dashboard principal
@app.route('/dash')
def dash():
    if 'user_id' not in session or session.get('user_role') != 'administrador':
        flash('Faça login como administrador para acessar esta página.', 'warning')
        return redirect(url_for('login_usuario'))
    
    administrador =db.usuario.find_one({'_id':ObjectId(session['user_id'])})
    administrador = administradores_collection.find_one({'_id': ObjectId(session['user_id'])})
    if not administrador:
        flash('Administrador não encontrado.', 'danger')
        return redirect(url_for('login_usuario'))
    
    return render_template('dash.html', usuario=administrador)


@app.route('/dashboard', methods=['GET', 'POST'])  
def dashboard():
    # Verifica se o usuário está logado
    if 'user_id' not in session:
        flash('Faça login para acessar esta página.', 'warning')
        return redirect(url_for('login_usuario'))
    
    # Obtém as informações do usuário a partir do ID da sessão
    usuario = db.usuarios.find_one({'_id': ObjectId(session['user_id'])})
    if not usuario:
        flash('Usuário não encontrado.', 'danger')
        return redirect(url_for('login_usuario'))

    # Lógica para processar o pedido
    if request.method == 'POST':
        pedido = request.form['pedido']
        
        # Lógica para processar o pedido e definir o status
        status_pedido = "Atendido"  # Aqui você pode colocar sua lógica real para definir o status

        # Armazena o pedido e o status no banco de dados
        db.pedidos.insert_one({
            'usuario_id': str(usuario['_id']),  # Use o ID do usuário como string
            'data_hora_pedido': datetime.datetime.utcnow(),  # Armazena a data e hora atual
            'itinerario': pedido,
            'status': status_pedido
        })
        
        flash(f"Pedido '{pedido}' foi {status_pedido.lower()}.", 'info')
    
    return render_template('dashboard.html', usuario=usuario)  # Retorna o template do dashboard

@app.route('/meus_pedidos') 
def meus_pedidos():
    # Verifica se o usuário está logado
    usuario_id = session.get('user_id')
    if not usuario_id:
        flash('Você precisa estar logado para acessar seus pedidos.', 'warning')
        return redirect(url_for('login_usuario'))  # Redireciona para o login se não estiver logado

    # Busca os pedidos do usuário logado no MongoDB
    pedidos = pedidos_collection.find({"usuario_id": usuario_id})
    
    # Converte os pedidos para uma lista com dicionários, incluindo todos os campos necessários
    pedidos_list = [
        {
            "id": str(pedido["_id"]),
            "nome_solicitante": pedido.get("nome_solicitante"),  # Nome do solicitante
            "motorista": pedido.get("motorista"),               # Nome do motorista
            "tipo_viatura": pedido.get("tipo_viatura"),         # Tipo da viatura
            "data_hora_pedido": pedido.get("data_hora_pedido"), # Data e hora do pedido
            "itinerario": pedido.get("itinerario"),             # Itinerário
            "status": pedido.get("status")                      # Status do pedido
        }
        for pedido in pedidos
    ]
    
    # Renderiza a página com os pedidos do usuário, incluindo os novos campos
    return render_template('dashboard.html', pedidos=pedidos_list)

# Rota para cancelar um pedido
@app.route('/cancelar_pedido/<pedido_id>', methods=['POST'])
def cancelar_pedido(pedido_id):
    if not pedido_id:
        flash('ID do pedido não foi fornecido.', 'danger')
        return redirect(url_for('listar_pedidos'))

    result = pedidos_collection.update_one(
        {'_id': ObjectId(pedido_id)},
        {'$set': {
            'status': 'Cancelado',
            'data_hora_cancelamento': datetime.now()
        }}
    )

    if result.modified_count == 0:
        flash('Nenhum pedido foi cancelado. Verifique se o ID está correto.', 'danger')
        return redirect(url_for('listar_pedidos'))

    flash('Pedido cancelado com sucesso!', 'success')
    return redirect(url_for('listar_pedidos'))

# Rota de logout
@app.route('/logout_usuario')
def logout_usuario():
    session.pop('user_id', None)
    session.pop('logged_in', None)
    flash('Você saiu com sucesso.', 'success')
    return redirect(url_for('login_usuario'))

if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0')
