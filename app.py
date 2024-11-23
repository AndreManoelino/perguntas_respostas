from flask import Flask, render_template, request, redirect, session, flash
import sqlite3
import random
from flask import Flask, render_template, request, redirect, url_for, flash, session
app = Flask(__name__)
app.secret_key = 'segredo123'

# Configuração do SQLite
DATABASE = 'jogo_perguntas.db'

# Função para conectar ao banco de dados SQLite
def get_db_connection():
    try:
        conexao = sqlite3.connect(DATABASE)
        conexao.row_factory = sqlite3.Row  # Para que as colunas sejam acessadas como dicionários
        return conexao
    except sqlite3.Error as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
        return None

# Criação do banco de dados SQLite (se não existir)
def create_db():
    conexao = get_db_connection()
    if conexao:
        try:
            cursor = conexao.cursor()

            # Criação da tabela 'usuarios'
            cursor.execute(''' 
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                password TEXT NOT NULL
            )
            ''')

            # Criação da tabela 'ranking'
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS ranking (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                pontuacao INTEGER NOT NULL
            )
            ''')

            conexao.commit()
            print("Banco de dados e tabelas criados com sucesso!")

        except sqlite3.Error as e:
            print(f"Erro ao criar as tabelas: {e}")
        finally:
            conexao.close()
    else:
        print("Falha ao conectar ao banco de dados.")


# Perguntas e respostas
# Perguntas e respostas por idade
PERGUNTAS = {
    "6-8": [
        {"pergunta": "Quantos lados tem um quadrado?", "opcoes": ["2", "3", "4", "5"], "correta": "4"},
        {"pergunta": "Complete corretamente a sequência A _ B _ C _ D ...", "opcoes": ["G", "K", "E", "Z"], "correta": "E"},
        {"pergunta": "Quanto é 2 + 2?", "opcoes": ["5", "8", "4", "25"], "correta": "4"},
        {"pergunta": "Complete a Palavra corretamente CACH_RRO", "opcoes": ["E", "D", "O", "A"], "correta": "O"},
        {"pergunta": "Quanto é 4 - 3?", "opcoes": ["1", "5", "2", "4"], "correta": "1"},
        {"pergunta": "Qual nome do irmão do Gru do Meu Malvado Favorito?", "opcoes": ["Gruz", "Dru", "Kevin", "Toto"], "correta": "Dru"},
        {"pergunta": "Quanto é 3 + 3?", "opcoes": ["5", "6", "8", "10"], "correta": "6"},
        {"pergunta": "Quanto é 8 - 2?", "opcoes": ["5", "8", "6", "2"], "correta": "6"},
        {"pergunta": "O que cai em pé e corre deitado?", "opcoes": ["Chuva", "Terra", "Pedra", "Mato"], "correta": "Chuva"},
        {"pergunta": "O que é o que é tem dente mais não é boca?", "opcoes": ["ALHO", "CAMELO", "PASSARO", "ALFACE"], "correta": "ALHO"},
        {"pergunta": "Quanto é 10 + 6?", "opcoes": ["16", "9", "23", "10"], "correta": "16"},
        {"pergunta": "Qual cor é o céu?", "opcoes": ["Verde", "Azul", "Amarelo", "Preto"], "correta": "Azul"},
        {"pergunta": "Qual é o nome do cachorro que aparece no desenho que tem a Velma, Salsicha, Fred e Daphne?", "opcoes": ["Tom", "Jerry", "Scooby-Doo", "Bugs Bunny"], "correta": "Scooby-Doo"},
        {"pergunta": "Quanto é 1 + 1?", "opcoes": ["3", "5", "8", "2"], "correta": "2"},
        {"pergunta": "Quantas sílabas tem a palavra DADO?", "opcoes": ["5", "8", "2", "15"], "correta": "2"},
        {"pergunta":"Quanto é 3 -3", "opcoes":["8","9","0","7"], "correta":"0"},
    ],
    "9-13": [
        {"pergunta": "Quantas pernas tem uma aranha?", "opcoes": ["4", "6", "8", "10"], "correta": "8"},
        {"pergunta": "Qual é o maior planeta do sistema solar?", "opcoes": ["Terra", "Júpiter", "Saturno", "Marte"], "correta": "Júpiter"},
        {"pergunta": "Quem foi Albert Einstein?", "opcoes": ["Médico", "Físico", "Astronauta", "Político"], "correta": "Físico"}
    ],
    
    "14-17": [
        {"pergunta": "Qual é a fórmula da água?", "opcoes": ["H2O", "O2H", "HO2", "H2"], "correta": "H2O"},
        {"pergunta": "Qual é o maior país do mundo?", "opcoes": ["China", "Rússia", "Brasil", "Canadá"], "correta": "Rússia"},
        {"pergunta": "Quem escreveu 'Dom Casmurro'?", "opcoes": ["Machado de Assis", "Clarice Lispector", "Carlos Drummond de Andrade", "Jorge Amado"], "correta": "Machado de Assis"}
    ],

    "18+": [
        {"pergunta": "Qual é o valor de π?", "opcoes": ["3.14", "3.141", "3.1415", "3.14159"], "correta": "3.14159"},
        {"pergunta": "Quem foi o primeiro presidente do Brasil?", "opcoes": ["Dom Pedro I", "Getúlio Vargas", "Deodoro da Fonseca", "Juscelino Kubitschek"], "correta": "Deodoro da Fonseca"},
        {"pergunta": "O que é a teoria da relatividade?", "opcoes": ["Física Quântica", "Evolução", "Teoria da Gravidade", "Teoria da Relatividade"], "correta": "Teoria da Relatividade"},
        {"pergunta": "Quem foi o primeiro presidente dos Estados Unidos?", "opcoes": ["George Washington", "Thomas Jefferson", "Abraham Lincoln", "John Adams"], "correta": "George Washington"},
        {"pergunta": "Quem escreveu 'Dom Quixote'?", "opcoes": ["Miguel de Cervantes", "William Shakespeare", "Jorge Luis Borges", "Gabriel García Márquez"], "correta": "Miguel de Cervantes"},
        {"pergunta": "Em que ano o homem pisou pela primeira vez na Lua?", "opcoes": ["1967", "1969", "1972", "1974"], "correta": "1969"},
        {"pergunta": "Qual é o maior continente em termos de área?", "opcoes": ["África", "Ásia", "América", "Antártida"], "correta": "Ásia"},
        {"pergunta": "Quem pintou a Mona Lisa?", "opcoes": ["Pablo Picasso", "Leonardo da Vinci", "Vincent van Gogh", "Claude Monet"], "correta": "Leonardo da Vinci"},
        {"pergunta": "Qual é a fórmula química da água?", "opcoes": ["CO2", "H2O", "O2", "H2SO4"], "correta": "H2O"},
        {"pergunta": "Qual é o maior planeta do nosso sistema solar?", "opcoes": ["Júpiter", "Saturno", "Terra", "Urano"], "correta": "Júpiter"},
        {"pergunta": "Qual foi o primeiro filme da saga Star Wars?", "opcoes": ["O Império Contra-Ataca", "O Retorno de Jedi", "Uma Nova Esperança", "A Ameaça Fantasma"], "correta": "Uma Nova Esperança"},
        {"pergunta": "Em que cidade nasceu Albert Einstein?", "opcoes": ["Berlim", "Zurique", "Ulm", "Paris"], "correta": "Ulm"},
        {"pergunta": "Quem descobriu a teoria da relatividade?", "opcoes": ["Isaac Newton", "Galileu Galilei", "Albert Einstein", "Nikola Tesla"], "correta": "Albert Einstein"},
        {"pergunta": "Em que ano o Brasil proclamou a sua independência?", "opcoes": ["1808", "1822", "1889", "1914"], "correta": "1822"},
        {"pergunta": "Qual é o órgão responsável pela produção de insulina no corpo humano?", "opcoes": ["Fígado", "Pâncreas", "Rim", "Coração"], "correta": "Pâncreas"},
        {"pergunta": "Quem foi o vencedor da Copa do Mundo de Futebol de 1998?", "opcoes": ["Brasil", "França", "Alemanha", "Argentina"], "correta": "França"},
        {"pergunta": "Quem é considerado o pai da teoria da evolução?", "opcoes": ["Isaac Newton", "Galileu Galilei", "Charles Darwin", "Gregor Mendel"], "correta": "Charles Darwin"},
        {"pergunta": "Em que ano a primeira guerra mundial começou?", "opcoes": ["1912", "1914", "1916", "1918"], "correta": "1914"},
        {"pergunta": "Quem foi o líder da revolução russa de 1917?", "opcoes": ["Vladimir Lenin", "Joseph Stalin", "Mikhail Gorbachev", "Leon Trotsky"], "correta": "Vladimir Lenin"}
    ]
}


@app.route('/')
def index():
    top_players = get_top_players()  # Obtém os melhores jogadores
    return render_template('index.html', top_players=top_players)


@app.route('/login', methods=['POST'])
def login():
    """Autenticação do usuário."""
    username = request.form['username']
    password = request.form['password']
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE username = ? AND password = ?", (username, password))
        user = cursor.fetchone()
        if user:
            session['user'] = user['username']
            conn.close()
            return redirect('/jogo')
        else:
            return render_template('index.html', error="Usuário ou senha inválidos!")
    except Exception as e:
        return f"Erro ao autenticar: {str(e)}"

@app.route('/cadastro', methods=['POST', 'GET'])
def cadastro():
    """Cadastro de novos usuários."""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM usuarios WHERE username = ?", (username,))
            existing_user = cursor.fetchone()
            if existing_user:
                return render_template('index.html', error="Usuário já existe!")

            # Inserindo o novo usuário na tabela de usuários
            cursor.execute("INSERT INTO usuarios (username, password) VALUES (?, ?)", (username, password))
            conn.commit()

            # Inserindo o usuário no ranking com uma pontuação inicial de 0
            cursor.execute("INSERT INTO ranking (username, pontuacao) VALUES (?, ?)", (username, 0))
            conn.commit()

            conn.close()
            return redirect('/ranking')  # Redireciona para a página de ranking
        except Exception as e:
            return f"Erro ao cadastrar: {str(e)}"
    return render_template('cadastro.html')


from werkzeug.security import generate_password_hash, check_password_hash

@app.route('/perfil', methods=['GET', 'POST'])
def perfil():
    """Página do perfil do usuário."""
    if 'user' not in session:
        return redirect('/')

    if request.method == 'POST':
        senha_atual = request.form['senha_atual']
        nova_senha = request.form['nova_senha']
        confirmacao = request.form['confirmacao']

        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            # Obtém a senha atual armazenada
            cursor.execute("SELECT password FROM usuarios WHERE username = ?", (session['user'],))
            registro = cursor.fetchone()

            if not registro or not check_password_hash(registro[0], senha_atual):
                flash("Senha atual incorreta.", "danger")
                return render_template('perfil.html', usuario=session['user'])

            # Valida a nova senha
            if nova_senha != confirmacao:
                flash("As novas senhas não coincidem.", "danger")
                return render_template('perfil.html', usuario=session['user'])

            if len(nova_senha) < 8 or not any(char.isdigit() for char in nova_senha) or not any(char.isupper() for char in nova_senha):
                flash("A nova senha deve ter pelo menos 8 caracteres, incluir números e letras maiúsculas.", "danger")
                return render_template('perfil.html', usuario=session['user'])

            # Atualiza a senha no banco de dados
            nova_senha_hash = generate_password_hash(nova_senha)
            cursor.execute("UPDATE usuarios SET password = ? WHERE username = ?", (nova_senha_hash, session['user']))
            conn.commit()
            flash("Senha atualizada com sucesso!", "success")

        except Exception as e:
            flash("Erro ao atualizar senha. Tente novamente.", "danger")
        finally:
            conn.close()

    return render_template('perfil.html', usuario=session['user'])



@app.route('/jogo')
def jogo():
    """Inicializa o jogo com base na idade selecionada."""
    if 'user' not in session:
        return redirect('/')

    if 'faixa_etaria' not in session:
        return redirect('/escolher_idade')  # Caso a faixa etária não tenha sido selecionada ainda

    faixa_etaria = session['faixa_etaria']
    perguntas = PERGUNTAS.get(faixa_etaria, [])

    # Embaralha as perguntas para que a ordem não seja fixa
    random.shuffle(perguntas)

    session['pontuacao'] = 0
    session['pergunta_atual'] = 0
    session['perguntas_selecionadas'] = perguntas
    return redirect('/pergunta')


@app.route('/pergunta', methods=['GET', 'POST'])
def pergunta():
    """Ponto para escolher a faixa de idade para perguntas."""
    if 'user' not in session:
        return redirect('/')

    if 'faixa_etaria' not in session:
        return redirect('/escolher_idade')

    perguntas = session['perguntas_selecionadas']
    index = session['pergunta_atual']

    if request.method == 'POST':
        resposta = request.form['resposta']
        pergunta = perguntas[index]
        if resposta != pergunta['correta']:
            # Se errar o  jogo acaba e vai para logout
            return redirect('/gameover')

        # Se acertar, soma 1 à pontuação
        session['pontuacao'] += 1
        session['pergunta_atual'] += 1

    if session['pergunta_atual'] < len(perguntas):
        pergunta = perguntas[session['pergunta_atual']]
        return render_template('jogo.html', pergunta=pergunta, index=session['pergunta_atual'] + 1,
                               total=len(perguntas))
    else:
        return redirect('/gameover')


@app.route('/gameover')
def gameover():
    """Tela final do jogo."""
    if 'user' not in session:
        return redirect('/')

    # Atualizar o ranking
    username = session['user']
    pontuacao = session['pontuacao']
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO ranking (username, pontuacao) VALUES (?, ?)", (username, pontuacao))
        conn.commit()

        # Obter ranking
        cursor.execute("SELECT * FROM ranking ORDER BY pontuacao DESC LIMIT 5")
        ranking = cursor.fetchall()

        conn.close()
    except Exception as e:
        return f"Erro ao atualizar ranking: {str(e)}"

    return render_template('gameover.html', pontuacao=pontuacao, usuario=username, ranking=ranking)

@app.route('/logout')
def logout():
    """Finaliza a sessão do usuário."""
    session.clear()
    return redirect('/')

@app.route('/escolher_idade', methods=['GET', 'POST'])
def escolher_idade():
    """Tela para o usuário escolher a faixa etária das perguntas."""
    if 'user' not in session:
        return redirect('/')

    if request.method == 'POST':
        idade = request.form['idade']
        session['faixa_etaria'] = idade
        return redirect('/jogo')

    return render_template('escolher_idade.html')

@app.route('/ranking')
def ranking():
    """Exibe o ranking dos 3 melhores jogadores."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Recuperando os 3 melhores jogadores (ordenados por pontuação)
        cursor.execute("SELECT username, pontuacao FROM ranking ORDER BY pontuacao DESC LIMIT 3")
        top_players = cursor.fetchall()

        conn.close()

        # Adicionando a imagem troféu.jpg para cada jogador
        top_players_with_images = []
        for player in top_players:
            player_data = {
                'username': player[0],
                'pontuacao': player[1],
                'imagem': 'trofeu.png'  # imagem padrão do troféu
            }
            top_players_with_images.append(player_data)

        # Passando os dados dos melhores jogadores para o template
        return render_template('index.html', top_players=top_players_with_images)
    except Exception as e:
        return f"Erro ao buscar ranking: {str(e)}"

def get_top_players():
    """Obtém os melhores jogadores do ranking ordenados por pontuação."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT username, pontuacao FROM ranking ORDER BY pontuacao DESC LIMIT 5")
        top_players = cursor.fetchall()
        conn.close()
        return top_players
    except sqlite3.Error as e:
        print(f"Erro ao obter jogadores do ranking: {e}")
        return []


if __name__ == '__main__':
    create_db()  # Chama a função para criar o banco de dados caso ele não exista
    app.run(app.run(host='0.0.0.0', port=1000))
