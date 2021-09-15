import sys
import pyparsing
import re

class Token:
    def __init__(self, type:str , value):
        self.type = type
        self.value = value

class Tokenizer:
    def __init__(self, origin: str, position: int):
        self.origin = origin
        self.position = position
        self.actual = Token(0,0)
        self.selectNext()

    #Metodo de retorno padronizado para token do tipo EOF

    def eofToken(self):
        self.actual = Token("EOF", '"')

    #Metodo de retorno padronizado para token do tipo OPERAÇÃO

    def opToken(self):
        self.actual = Token("Operacao", self.origin[self.position])
        self.position += 1

    #Metodo de retorno padronizado para token do tipo INT

    def intToken(self, concInt):
        self.actual = Token("Inteiro", int(concInt))

    def selectNext(self):
        numeros = [str(i + 1) for i in range(-1,9)]
        concString = ""

        # print(self.actual.value)

        if self.position == (len(self.origin)):
            self.eofToken()
            return self.actual

        if self.position < (len(self.origin)):
            # print(self.origin[self.position])
            while self.origin[self.position] == " ":
                self.position += 1


            if self.origin[self.position] == "+" or self.origin[self.position] == "-" or self.origin[self.position] == "*" or self.origin[self.position] == "/":
                self.opToken()
                return self.actual

            if self.origin[self.position] in numeros:
                while self.origin[self.position] in numeros:
                    # print(self.position)
                    concString += self.origin[self.position]

                    self.position += 1

                    if self.position == (len(self.origin)):
                        break

                self.intToken(concString)
                return self.actual

            return self.actual

        if self.position >= (len(self.origin) - 1):
            self.eofToken()


class Parser:
    def __init__(self):
        self.tokens = None

    def parseTerm(self):
        actToken = self.tokens.actual

        if actToken.type == "Inteiro":
            resultado = actToken.value
            actToken = self.tokens.selectNext()

            while actToken.value == "*" or actToken.value == "/":
                if actToken.value == "*":
                    actToken = self.tokens.selectNext()
                    if actToken.type == "Inteiro":
                        resultado *= actToken.value
                    else:
                        raise Exception("Erro")

                if actToken.value == "/":
                    actToken = self.tokens.selectNext()
                    if actToken.type == "Inteiro":
                        resultado /= actToken.value

                    else:
                        raise Exception("Erro")

                actToken = self.tokens.selectNext()
            return resultado
        else:
            raise Exception("Error")

    def parseExpression(self):
        actToken = self.tokens.actual
        resultado = 0

        if actToken.type == "Inteiro":
            resultado += Parser.parseTerm(self)
            # print(self.tokens.actual.value)
            actToken = self.tokens.actual
            # print(actToken.value)

            # print(actToken.type)
            while actToken.type == "Operacao":
                # print(actToken.value)
                if actToken.value == "+":
                    actToken = self.tokens.selectNext()

                    if actToken.type == "Inteiro":
                        resultado += Parser.parseTerm(self)
                        # print(resultado)
                        actToken = self.tokens.actual
                        # print(actToken.value)
                    else: raise Exception("ERRO")
                # print(actToken.value)
                if actToken.value == "-":
                    # print(actToken.value)
                    actToken = self.tokens.selectNext()

                    if actToken.type == "Inteiro":
                        resultado -= Parser.parseTerm(self)

                        actToken = self.tokens.actual
                    else: raise Exception("Erro")

                # print(self.tokens.actual.value)
                # actToken = self.tokens.selectNext()
                # print(actToken.value)
            return resultado
        else: raise Exception("Error")



    def run(self,strCodigo):
        strCodigo = PreProcessing.process(strCodigo)
        self.tokens = Tokenizer(strCodigo,0)
        resultadoFinal = self.parseExpression()

        return resultadoFinal

class PreProcessing():
    def process(codigo):
        filtroT = pyparsing.nestedExpr("/*", "*/").suppress()

        varFiltered = filtroT.transformString(codigo)

        if "*" not in varFiltered and "/" not in varFiltered and "+" not in varFiltered and "-" not in varFiltered:
            if len(varFiltered.replace(" ", "")) > 1:
                raise Exception("Error")

        # filtered = re.sub("[/*@*&?].*[*/@*&?]" ,"" ,codigo).replace(" ", "")
        filtered = re.sub(re.compile("/\*([^*]|[\r\n]|(\*+([^*/]|[\r\n])))*\*+/",re.DOTALL ) ,"" ,codigo).replace(" ", "")

        return filtered


operacao = ''.join(sys.argv[1:])
pars = Parser()
print(int(pars.run(operacao)))
