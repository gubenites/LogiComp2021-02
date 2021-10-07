import sys
import pyparsing
import re
import string

symbolTab = dict()

class Node:
    def __init__(self, value):
        self.value = value
        self.children = []

class BinOp(Node):
    def Evaluate(self):

        lChild = self.children[0].Evaluate()
        rChild = self.children[1].Evaluate()

        if self.value == "*":
            return lChild * rChild
        if self.value == "/":
            return int(lChild / rChild)
        if self.value == "+":
            return lChild + rChild
        if self.value == "-":
            return lChild - rChild
        else:
            raise Exception("Error")

class UnOp(Node):
    def Evaluate(self):
        child = self.children[0].Evaluate()

        if self.value == "+":
            return 1 * child
        if self.value == "-":
            return -1 * child
        else:
            raise Exception("Error")

class IntVal(Node):
    def Evaluate(self):
        return self.value

class NoOp(Node):
    def Evaluate(self):
        pass

class printOp(Node):
    def Evaluate(self):
        print(self.children[0].Evaluate())

class Token:
    def __init__(self, type:str , value):
        self.type = type
        self.value = value

class Operacoes(Node):
    def Evaluate(self):
        for item in self.children:
            item.Evaluate()

class attributionOp(Node):
    def Evaluate(self):
        var = SymbolTable(self.value)

        return var.getter()

class alocaOp(Node):
    def Evaluate(self):

        symbolTable = SymbolTable(self.children[0].value)
        symbolTable.setter(self.children[1].Evaluate())

class SymbolTable:
    def __init__(self,var):
        self.var = var

    def setter(self,valor):
        symbolTab[self.var] = valor

    def getter(self):
        if self.var in symbolTab:
            returned_stattement = symbolTab[self.var]

            return returned_stattement

        else:
            raise Exception("Variavel não existe na tabela de simbolos")

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

    def parToken(self,token):
        self.actual = Token("Parenteses",self.origin[self.position])
        self.position += 1

    def selectNext(self):
        numeros = [str(i + 1) for i in range(-1,9)]
        alphabet_string = list(string.ascii_lowercase)
        list_not_accepted = list(string.ascii_uppercase)
        concString = ""

        # print(self.actual.value)

        if self.position == (len(self.origin)):
            self.eofToken()
            return self.actual

        if self.position < (len(self.origin)):
            # print(self.origin[self.position])
            while self.origin[self.position] == " ":
                self.position += 1

            if self.origin[self.position] == "(" or self.origin[self.position] == ")":
                self.parToken(self.origin[self.position])

                return self.actual

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

            if self.origin[self.position] == "=":
                self.actual = Token("Equal", "=")
                self.position += 1

            if self.origin[self.position] in alphabet_string or self.origin[self.position] == "_" or self.origin[self.position] in list_not_accepted:
                while self.origin[self.position] in alphabet_string or self.origin[self.position] in numeros or self.origin[self.position] == "_" or self.origin[self.position] in list_not_accepted:
                    if self.origin[self.position] in list_not_accepted:
                        raise Exception("Variavel não pode ser maiuscula")

                    concString += self.origin[self.position]
                    self.position += 1


                if concString == "println":
                    self.actual = Token("PRINT", concString)

                    return self.actual
                else:
                    self.actual = Token("Variable", concString)

                    return self.actual

            if self.origin[self.position] == ";":
                self.actual = Token("ENDLINE",";")
                self.position += 1

            return self.actual

        if self.position >= (len(self.origin) - 1):
            self.eofToken()


class Parser:
    def __init__(self):
        self.tokens = None

    def parseFactor(self):
        actToken = self.tokens.actual

        if actToken.type == "Inteiro":
            return IntVal(actToken.value)

        if actToken.value == "+":
            resultado = UnOp(actToken.value)
            actToken = self.tokens.selectNext()
            resultado.children.append(Parser.parseFactor(self))

            return resultado
        if actToken.value == "-":
            resultado = UnOp(actToken.value)
            actToken = self.tokens.selectNext()
            resultado.children.append(Parser.parseFactor(self))
            # print(resultado.children)

            return resultado

        if actToken.value == "(":
            actToken = self.tokens.selectNext()
            resultado = Parser.parseExpression(self)
            # print(resultado.children[1].value)
            actToken = self.tokens.actual

            if actToken.value == ")":
                return resultado
            else:
                raise Exception("ERRO")

        if actToken.type == "Variable":
            resultado = attributionOp(actToken.value)
            # actToken = self.tokens.selectNext()

            return resultado

    def parseTerm(self):
        actToken = self.tokens.actual

        resultado = Parser.parseFactor(self)
        actToken = self.tokens.selectNext()
        while actToken.value == "*" or actToken.value == "/":
            if actToken.value == "*":
                BinaryOp = BinOp(actToken.value)
                BinaryOp.children.append(resultado)

                actToken = self.tokens.selectNext()

                BinaryOp.children.append(Parser.parseFactor(self))
                resultado = BinaryOp

            if actToken.value == "/":
                BinaryOp = BinOp(actToken.value)
                BinaryOp.children.append(resultado)

                actToken = self.tokens.selectNext()

                BinaryOp.children.append(Parser.parseFactor(self))
                resultado = BinaryOp

            actToken = self.tokens.selectNext()

        return resultado

    def parseExpression(self):
        actToken = self.tokens.actual
        resultado = 0

        resultado = Parser.parseTerm(self)
        actToken = self.tokens.actual

        while actToken.type == "Operacao":

            if actToken.value == "+":
                BinaryOp = BinOp(actToken.value)
                BinaryOp.children.append(resultado)

                actToken = self.tokens.selectNext()

                BinaryOp.children.append(Parser.parseTerm(self))
                resultado = BinaryOp
                actToken = self.tokens.actual

            if actToken.value == "-":
                BinaryOp = BinOp(actToken.value)
                BinaryOp.children.append(resultado)

                actToken = self.tokens.selectNext()

                BinaryOp.children.append(Parser.parseTerm(self))
                resultado = BinaryOp
                actToken = self.tokens.actual

        return resultado

    def parseCommand(self):
        actToken = self.tokens.actual
        resultado = NoOp(None)

        if actToken.type == "Variable":
            varToAlocate = alocaOp(None)

            varName = alocaOp(self.tokens.actual.value)

            actToken = self.tokens.selectNext()

            varToAlocate.children.append(varName)

            if actToken.type != "Variable":
                actToken = self.tokens.selectNext()

            resultado_alocate = Parser.parseExpression(self)
            varToAlocate.children.append(resultado_alocate)

            actToken = self.tokens.actual

            resultado = varToAlocate

        if actToken.type == "PRINT":
            printEmpty = printOp(None)

            actToken = self.tokens.selectNext()

            if actToken.value == "(":
                actToken = self.tokens.selectNext()

                resultado_print = Parser.parseExpression(self)

                printEmpty.children.append(resultado_print)

                resultado = printEmpty

                actToken = self.tokens.actual


                if actToken.value != ")":
                    raise Exception("Não fechou parenteses")
                else:
                    actToken = self.tokens.selectNext()
            else:
                raise Exception("Parenteses não abriu")

        actToken = self.tokens.actual

        if actToken.value == ";":
            actToken = self.tokens.selectNext()
        else:
            raise Exception("Linha não condiz com sintaxe da linguagem")

        return resultado

    def parseBlock(self):
        actToken = self.tokens.actual
        resultsNodes = Operacoes(None)

        while self.tokens.actual.type != "EOF":
            resultado = Parser.parseCommand(self)
            resultsNodes.children.append(resultado)

        return resultsNodes

    def run(self,strCodigo):
        strCodigo = PreProcessing.process(strCodigo)
        self.tokens = Tokenizer(strCodigo,0)
        resultadoFinal = self.parseBlock()

        return resultadoFinal

class PreProcessing():
    def process(codigo):
        filtroT = pyparsing.nestedExpr("/*", "*/").suppress()
        somaa_p = 0
        somaf_p = 0
        varFiltered = filtroT.transformString(codigo)

        # if "*" not in varFiltered and "/" not in varFiltered and "+" not in varFiltered and "-" not in varFiltered:
        #     if len(varFiltered.replace(" ", "")) > 1:
        #         raise Exception("Error")

        # filtered = re.sub("[/*@*&?].*[*/@*&?]" ,"" ,codigo).replace(" ", "")
        filtered = re.sub(re.compile("/\*([^*]|[\r\n]|(\*+([^*/]|[\r\n])))*\*+/",re.DOTALL ) ,"" ,codigo).replace(" ", "")
        filtered = filtered.replace('\n', "")
        filtered = filtered.replace('\t', "")

        for item in range(len(filtered)):
            if (filtered[item] == "/" and filtered[item + 1] == "*") or filtered[item] == "*" and filtered[item + 1] == "/":
                raise Exception("Erro - comentario não esta fechando")

        for item in filtered:
            if item == "(":
                somaa_p += 1
            if item == ")":
                somaf_p += 1
        somaf = somaa_p + somaf_p
        if (somaf % 2) != 0:
            raise Exception("Error - parenteses não esta fechando")

        return filtered

cFile = open(sys.argv[1], 'r')
operacao = ''.join(cFile.read()).strip()
# print(operacao)
# operacao = ''.join(sys.argv[1:])
pars = Parser()
resultado = pars.run(operacao)
resultado.Evaluate()
