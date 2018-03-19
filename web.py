from firebase import firebase
import math
from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin
import os


# urlFilipe : https://recomendafilmes-6d180.firebaseio.com/
firebase = firebase.FirebaseApplication('https://recomendafilmes-6d180.firebaseio.com/', authentication=None)
avaliacoesFirebase = firebase.get('/Avaliacoes', None)

#print(filmes[0]["ano"])
avaliacoes = {}

def euclidiana(usuario1, usuario2):
    s1 = {}
    for item in avaliacoes[usuario1]:
        if item in avaliacoes[usuario2]: s1[item] = 1

    if len(s1) == 0 : return 0

    soma = sum([pow(avaliacoes[usuario1][item] - avaliacoes[usuario2][item],2) for item in avaliacoes[usuario1] if item in avaliacoes[usuario2]])
    return 1/(1 + math.sqrt(soma))

def getSimilares(usuario):
    similiaridade = [(euclidiana(usuario, outro), outro) 
                    for outro in avaliacoes if outro != usuario]
    similiaridade.sort()
    similiaridade.reverse()
    return similiaridade

def getRecomendacoes(usuario):
    atualiza()
    totais = {}
    somaSimilaridade = {}
    for outro in avaliacoes:
        if outro == usuario: continue
        similaridade = euclidiana(usuario, outro)
        if similaridade <= 0: continue
        for item in avaliacoes[outro]:
            if item not in avaliacoes[usuario]:
                totais.setdefault(item, 0.0)
                totais[item] += float(avaliacoes[outro][item]) * similaridade
                somaSimilaridade.setdefault(item,0.0)
                somaSimilaridade[item] += similaridade
    rankings =  [(total/somaSimilaridade[item], item) for item, total in totais.items()]
    rankings.sort()
    rankings.reverse()
    return rankings

def atualiza():
    global  avaliacoesFirebase
    avaliacoesFirebase = firebase.get('/Avaliacoes', None)
    global avaliacoes
    avaliacoes = {}
    for usuario in avaliacoesFirebase:
        idUsuario = usuario
        avaliacoesUserX = {}
        dic = avaliacoesFirebase[usuario]
        for avaliacao in dic:
            idFilme = avaliacao
            notaFilme = dic[idFilme]["avaliacao"]
            avaliacoesUserX[idFilme] = int(notaFilme)
        avaliacoes[idUsuario] = avaliacoesUserX

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

@app.route('/atualizaBanco', methods=['GET'])
def atualizaBanco():
    return "ok"


@app.route('/indicados/<id>', methods=['GET'])
@cross_origin()
def getIndicados(id):
	indicados = getRecomendacoes(id)
	indicacoes = []
	for filme in indicados:
		indicado = {"idFilme": filme[1], "possivelNotaFilme":filme[0]}
		indicacoes = indicacoes + [indicado]
	return jsonify(indicacoes)



if __name__ == '__main__':
  port = int(os.environ.get('PORT', 5000))
  app.run(host='0.0.0.0', port=port)

            