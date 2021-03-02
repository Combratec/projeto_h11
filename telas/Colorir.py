from threading import Thread
from tkinter import END
from copy import deepcopy
from re import finditer
from re import search
from time import time


class Colorir():
    def __init__(self): 
        self.__tx_editor_codigo = None
        self.__historico_coloracao = []
        self.__lista_todos_coloracao = []

    def alterar_cor_comando(self, novo_cor_do_comando):
        self.cor_do_comando = novo_cor_do_comando

    def __realiza_coloracao(self, palavra, linha, valor1, valor2, cor):
        linha1 = '{}.{}'.format(linha, valor1)
        linha2 = '{}.{}'.format(linha, valor2)

        self.__tx_editor_codigo.tag_add(palavra, linha1, linha2)
        self.__tx_editor_codigo.tag_config(palavra, foreground=cor)

    def __marcar_coloracao(self, regex, lista, linha, palavra, cor):

        for valor in finditer(regex, lista[linha]):

            inici_regex = valor.start()
            final_regex = valor.end()

            usado = cor + str(palavra) + str(regex) + str(inici_regex) + str(final_regex) + str(linha+1)

            self.__historico_coloracao.append(usado)
            Colorir.__realiza_coloracao(self, str(usado), str(linha + 1), inici_regex, final_regex, cor)

            if usado not in self.__lista_todos_coloracao:
                self.__lista_todos_coloracao.append(usado)

    def __filtrar_palavras(palavra):
        palavra_comando = palavra.replace('+', '\\+')
        palavra_comando = palavra_comando.replace('/', '\\/')
        palavra_comando = palavra_comando.replace('*', '\\*')
        palavra_comando = palavra_comando.replace(' ', '[\\s{1,}|_]')
        return palavra_comando

    def __colorir_comandos(self, lista_linhas):

        # Obtem uma cópia do código para análise mais rápida do interpretador
        texto = ""
        for linha in lista_linhas:
            texto += linha
        texto = texto.replace(' ', '')
        texto = texto.lower()
        texto = texto.replace('_', '')

        for chave_comando, dicionario_comandos in self.dic_comandos.items():
            cor = self.cor_do_comando[dicionario_comandos["cor"]]["foreground"]

            for comando in dicionario_comandos["comando"]:

                palavra_analise = comando[0].strip()

                if palavra_analise == "":
                    continue

                # Verifica se o comando está no código
                comando_teste = palavra_analise.replace(' ', '')
                if comando_teste not in texto:
                    continue

                palavra_comando = Colorir.__filtrar_palavras(palavra_analise)

                regex = '(^|\\s){}(\\s|$)'.format(palavra_comando)

                for linha in range(len(lista_linhas)):
                    Colorir.__marcar_coloracao(self, regex, lista_linhas, linha, palavra_comando, cor)

    def __colorir_especial(self, lista):

        for linha in range(len(lista)):

            regex_comentario = '(#|\\/\\/).*$'
            regex_numerico = '(^|\\s|\\,)([0-9\\.]\\s*){1,}($|\\s|\\,)'
            regex_string = """\"[^"]*\""""
            regex_chave = "{|}"
            regex_cor = "na\\s*cor\\s*\"(.*?)\""


            cor_comentario = self.cor_do_comando["comentario"]["foreground"]
            cor_numerico = self.cor_do_comando["numerico"]["foreground"]
            cor_chave = self.cor_do_comando["logico"]["foreground"]
            cor_string = self.cor_do_comando["string"]["foreground"]

            cor_cor = search(regex_cor, str(lista[linha]))

            Colorir.__marcar_coloracao(self, regex_numerico, lista, linha, 'numerico', cor_numerico)
            Colorir.__marcar_coloracao(self, regex_chave, lista, linha, 'chave', cor_chave)
            Colorir.__marcar_coloracao(self, regex_string, lista, linha, '"', cor_string)

            if "#" in lista[linha]:
                Colorir.__marcar_coloracao(self, regex_comentario, lista, linha, 'comentario', cor_comentario)

            if cor_cor is not None:
                cor_cor = str(cor_cor.group(1))
                Colorir.__marcar_coloracao(self, regex_cor, lista, linha, 'corcor', cor_cor)


    def coordena_coloracao(self, event, tx_editor_codigo):
        self.__tx_editor_codigo = tx_editor_codigo

        lista_linhas = self.__tx_editor_codigo.get(1.0, END).lower().split('\n')

        self.__historico_coloracao = []

        Colorir.__colorir_comandos(self, lista_linhas)
        Colorir.__colorir_especial(self, lista_linhas)

        for palavra_nao_colorida in self.__lista_todos_coloracao:
            if palavra_nao_colorida not in self.__historico_coloracao:
                self.__tx_editor_codigo.tag_delete(palavra_nao_colorida)
                self.__lista_todos_coloracao.remove(palavra_nao_colorida)

        if self.master is not None:
            self.master.update()

        return 0





