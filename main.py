import sys
import pyparsing
import re
import string
import pprint as pp

symbolTab = dict()
loop_number = 0

def get_loopNum():
    global loop_number
    loop_number += 4
    return loop_number


class P_Code:
    commands = []

    def AddCommand(command):
        P_Code.commands.append(command)

class Node:
    def __init__(self, value):
        self.value = value
        self.children = []

class BinOp(Node):
    def Evaluate(self):

        lChild = self.children[0].Evaluate()
        rChild = self.children[1].Evaluate()

        if self.value == "*":
            command = "opr 0 {0};\n".format(4)
            P_Code.AddCommand(command)
            return lChild * rChild
        if self.value == "/":
            command = "opr 0 {0};\n".format(5)
            P_Code.AddCommand(command)
            return int(lChild / rChild)
        if self.value == "+":
            command = "opr 0 {0};\n".format(2)
            P_Code.AddCommand(command)
            return lChild + rChild
        if self.value == "-":
            command = "opr 0 {0};\n".format(3)
            P_Code.AddCommand(command)
            return lChild - rChild
        if self.value == ">":
            command = "opr 0 {0};\n".format(12)
            P_Code.AddCommand(command)
            return lChild > rChild
        if self.value == "<":
            command = "opr 0 {0};\n".format(3)
            P_Code.AddCommand(command)
            return lChild < rChild
        if self.value == "&&":
            return lChild and rChild
        if self.value == "==":
            command = "opr 0 {0};\n".format(3)
            P_Code.AddCommand(command)
            return lChild == rChild
        if self.value == "||":
            return lChild or rChild
        else:
            raise Exception("Error")

class UnOp(Node):
    def Evaluate(self):
        child = self.children[0].Evaluate()

        if self.value == "+":
            return 1 * child
        if self.value == "-":
            command = "opr 0 {0};\n".format(1)
            P_Code.AddCommand(command)
            return -1 * child
        if self.value == "!":
            return (not child)
        else:
            raise Exception("Error")

class IntVal(Node):
    def Evaluate(self):
        command = "lit 0 {0};\n".format(self.value)
        P_Code.AddCommand(command)
        return self.value

class StrVal(Node):
    def Evaluate(self):
        return str(self.value)

class NoOp(Node):
    def Evaluate(self):
        pass

class printOp(Node):
    def Evaluate(self):
        print(self.children[0].Evaluate())

class ForOp(Node):
    def Evaluate(self):
        loop_number = get_loopNum()

        self.children[0].Evaluate()

        command = "cal 0 F_LOOP_{};\n".format(loop_number)
        P_Code.AddCommand(command)

        condition = self.children[1].Evaluate()

        command = "jpc 0 F_LOOP_EXIT_{};\n".format(loop_number)
        P_Code.AddCommand(command)

        self.children[3].Evaluate()
        self.children[2].Evaluate()

        command = "jmp 0 F_LOOP_{};\n".format(loop_number)
        P_Code.AddCommand(command)

        command = "cal 0 F_LOOP_EXIT_{};\n".format(loop_number)
        P_Code.AddCommand(command)

        # while(self.children[1].Evaluate()):
            # self.children[3].Evaluate()
            # self.children[2].Evaluate()


class WhileOp(Node):
    def Evaluate(self):
        loop_number = get_loopNum()

        command = "cal 0 W_LOOP_{};\n".format(loop_number)
        P_Code.AddCommand(command)

        condition = self.children[0].Evaluate()

        command = "jpc 0 W_LOOP_EXIT_{};\n".format(loop_number)
        P_Code.AddCommand(command)

        self.children[1].Evaluate()

        command = "jmp 0 W_LOOP_{};\n".format(loop_number)
        P_Code.AddCommand(command)

        command = "cal 0 W_LOOP_EXIT_{};\n".format(loop_number)
        P_Code.AddCommand(command)


        # while(condition):
        #     self.children[1].Evaluate()

class ifOp(Node):
    def Evaluate(self):
        loop_number = get_loopNum()

        condition = self.children[0].Evaluate()

        if len(self.children) == 3:
            command = "jpc 0 ELSE_{};\n".format(loop_number)
            P_Code.AddCommand(command)

        self.children[1].Evaluate()

        command = "jmp 0 EXIT_{};\n".format(loop_number)
        P_Code.AddCommand(command)

        if len(self.children) == 3:
            command = "cal 0 ELSE_{};\n".format(loop_number)
            P_Code.AddCommand(command)

            self.children[2].Evaluate()
            command = "jmp 0 EXIT_{};\n".format(loop_number)
            P_Code.AddCommand(command)

        command = "cal 0 EXIT_{};\n".format(loop_number)
        P_Code.AddCommand(command)

        # if(condition):
        #     self.children[1].Evaluate()
        # elif(len(self.children) == 3):
        #     self.children[2].Evaluate()


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
        command = "lod 0 {};\n".format(self.value)
        P_Code.AddCommand(command)

        return var.getter()

class alocaOp(Node):
    def Evaluate(self):
        if len(self.children) == 2:
            if self.children[0] == "int" or self.children[0] == "str":
                symbolTable = SymbolTable(self.children[1].value)
                symbolTable.setter(1, self.children[0])

            else:
                symbolTable = SymbolTable(self.children[0].value)
                symbolTable.setter(self.children[1].Evaluate(), None)

                command = "sto 0 {};\n".format(self.children[0].value)
                P_Code.AddCommand(command)


        if len(self.children) == 3:
            symbolTable = SymbolTable(self.children[1].value)
            symbolTable.setter(self.children[2].Evaluate(), self.children[0])

            command = "sto 0 {};\n".format(self.children[1].value)
            P_Code.AddCommand(command)



class readOp(Node):
    def Evaluate(self):
        return int(input())

class SymbolTable:
    def __init__(self,var):
        self.var = var

    def setter(self, valor, tipo):
        if tipo == None:
            try:
                symbolTab[self.var] = int(valor)
            except:
                try:
                    symbolTab[self.var] = str(valor)
                except:
                    raise Exception("Não foi possivel declarar a variavel")

        if tipo != None:
            if tipo == "int":
                try:
                    symbolTab[self.var] = int(valor)
                except:
                    raise Exception("Error - variavel não é numero inteiro")

            if tipo == "str":
                try:
                    symbolTab[self.var] = str(valor)
                except:
                    raise Exception("Error - variavel não é string")

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

    def strToken(self, concString):
        self.actual = Token("STR", str(concString))

    def parToken(self,token):
        self.actual = Token("Parenteses",self.origin[self.position])
        self.position += 1

    def selectNext(self):
        numeros = [str(i + 1) for i in range(-1,9)]
        alphabet_string = list(string.ascii_lowercase)
        list_not_accepted = list(string.ascii_uppercase)
        list_reserved_words = ["if","else","while","println","readln", "int", "str"]
        list_symbols = ["&","|","_"]
        concString = ""
        concSymbols = ""
        flag_ = False

        # print(self.actual.value)

        if self.position == (len(self.origin)):
            self.eofToken()
            return self.actual

        if self.position < (len(self.origin)):
            # print(self.origin[self.position])
            while self.origin[self.position] == " ":
                self.position += 1

            if self.origin[self.position] == "{" or self.origin[self.position] == "}":
                self.actual = Token("Chaves", self.origin[self.position])

                self.position += 1

                return self.actual

            if self.origin[self.position] == "(" or self.origin[self.position] == ")":
                self.parToken(self.origin[self.position])

                return self.actual

            if self.origin[self.position] == "+" or self.origin[self.position] == "-" or self.origin[self.position] == "*" or self.origin[self.position] == "/" or self.origin[self.position] == ">" or self.origin[self.position] == "<" or self.origin[self.position] == "!":
                self.opToken()

                return self.actual

            # try:

            # if self.origin[self.position] == "=":
            #     self.position += 1

            # print(self.origin[self.position])
            if self.origin[self.position] == "'":
                self.position += 1
                concString = ""

                while self.origin[self.position] != "'":
                    concString += self.origin[self.position]
                    self.position += 1

                self.actual = Token("String", concString)
                self.position += 1

                return self.actual

            if self.origin[self.position] in numeros:
                while self.origin[self.position] in numeros:
                    if flag_:
                        break
                    concString += self.origin[self.position]

                    self.position += 1
                    if (str(self.origin[self.position]) in alphabet_string and str(self.origin[self.position]) != "="):
                        print(str(self.origin[self.position]))
                        raise Exception("Não pode ser letra")

                    if self.position == (len(self.origin)) or self.origin[self.position] == ";":
                        break

                self.intToken(concString)

                return self.actual
            # except:
            #     pass

            if self.origin[self.position] == "=":
                self.position += 1
                if self.origin[self.position] != "=":
                    self.actual = Token("Equal", "=")
                else:
                    self.actual = Token("Operacao", "==")

            if self.origin[self.position] in list_symbols:
                while self.origin[self.position] in list_symbols:
                    concSymbols += self.origin[self.position]
                    self.position += 1

                    if concSymbols == "&&":
                        self.actual = Token("Operacao", concSymbols)

                        return self.actual
                    if concSymbols == "||":
                        self.actual = Token("Operacao", concSymbols)

                        return self.actual


            if self.origin[self.position] in alphabet_string or self.origin[self.position] in list_not_accepted or self.origin[self.position] == "_" or self.origin[self.position] in numeros:
                while self.origin[self.position] in alphabet_string or self.origin[self.position] in list_not_accepted or self.origin[self.position] == "_" or self.origin[self.position] in numeros:
                    if self.origin[self.position] in list_not_accepted:
                        raise Exception("Variavel não pode ser maiuscula")
                    if concString in list_reserved_words:
                        break
                    try:
                        int(concString[0])
                        raise Exception("Primeira letra não pode ser numero")
                    except:
                        pass

                    concString += self.origin[self.position]
                    self.position += 1

                if concString == "int":
                    self.actual = Token("INT", concString)

                    return self.actual

                if concString == "str":
                    self.actual = Token("STR", concString)

                    return self.actual

                if concString == "for":
                    self.actual = Token("FOR", concString)

                    return self.actual

                if concString == "while":
                    self.actual = Token("WHILE",concString)

                    return self.actual

                if concString == "if":
                    self.actual = Token("IF", concString)

                    return self.actual

                if concString == "else":
                    self.actual = Token("ELSE", concString)

                    return self.actual

                if concString == "readln":
                    self.actual = Token("READ", concString)

                    return self.actual

                if concString == "println":
                    self.actual = Token("PRINT", concString)

                    return self.actual

                try:
                    self.actual = Token("Inteiro", int(concString))

                    return self.actual
                except:
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

    def orExpr(self):
        actToken = self.tokens.actual

        resultado = Parser.andExpr(self)
        actToken = self.tokens.actual

        if actToken.value == "||":
            BinaryOp = BinOp(actToken.value)
            BinaryOp.children.append(resultado)

            actToken = self.tokens.selectNext()

            BinaryOp.children.append(Parser.orExpr(self))
            resultado = BinaryOp

        return resultado

    def andExpr(self):
        actToken = self.tokens.actual

        resultado = Parser.eqExpr(self)
        actToken = self.tokens.actual

        if actToken.value == "&&":
            BinaryOp = BinOp(actToken.value)
            BinaryOp.children.append(resultado)

            actToken = self.tokens.selectNext()

            BinaryOp.children.append(Parser.andExpr(self))
            resultado = BinaryOp

        return resultado

    def eqExpr(self):
        actToken = self.tokens.actual

        resultado = Parser.relExpr(self)
        actToken = self.tokens.actual

        if actToken.value == "==":
            BinaryOp = BinOp(actToken.value)
            BinaryOp.children.append(resultado)

            actToken = self.tokens.selectNext()

            BinaryOp.children.append(Parser.eqExpr(self))
            resultado = BinaryOp

        return resultado

    def relExpr(self):
        actToken = self.tokens.actual

        resultado = Parser.parseExpression(self)
        actToken = self.tokens.actual

        if actToken.value == ">" or actToken.value == "<":
            BinaryOp = BinOp(actToken.value)
            BinaryOp.children.append(resultado)

            actToken = self.tokens.selectNext()

            BinaryOp.children.append(Parser.relExpr(self))
            resultado = BinaryOp

        return resultado

    def parseFactor(self):
        actToken = self.tokens.actual

        if actToken.type == "READ":
            actToken = self.tokens.selectNext()

            if actToken.value == "(":
                resultado = readOp(actToken.value)
                actToken = self.tokens.selectNext()

                if actToken.value != ")":
                    raise Exception("Não fecha parenteses")

                return resultado

        if actToken.type == "Inteiro":
            return IntVal(actToken.value)

        if actToken.type == "String":
            return StrVal(actToken.value)

        if actToken.value == "+":
            resultado = UnOp(actToken.value)
            actToken = self.tokens.selectNext()
            resultado.children.append(Parser.parseFactor(self))

            return resultado

        if actToken.value == "!":
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
            resultado = Parser.orExpr(self)

            actToken = self.tokens.actual

            if actToken.value == ")":
                return resultado
            else:
                # print("entrei")
                raise Exception("ERRO")

        if actToken.type == "Variable":
            resultado = attributionOp(actToken.value)

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

        while actToken.value == "+" or actToken.value == "-":
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

        if actToken.type == "INT" or actToken.type == "STR":
            varToAlocate = alocaOp(None)

            varToAlocate.children.append(actToken.value)

            actToken = self.tokens.selectNext()
            varName = alocaOp(self.tokens.actual.value)

            actToken = self.tokens.selectNext()

            varToAlocate.children.append(varName)

            if actToken.type != "Variable" and actToken.type != "READ" and actToken.type != "Inteiro" and actToken.type != "String" and actToken.value != ";":
                actToken = self.tokens.selectNext()

            if actToken.value != ";":
                resultado_alocate = Parser.orExpr(self)

                varToAlocate.children.append(resultado_alocate)

            actToken = self.tokens.actual
            resultado = varToAlocate

            return resultado

        if actToken.type == "Variable" or actToken.type == "PRINT" or actToken.value == ";":
            if actToken.type == "Variable":
                varToAlocate = alocaOp(None)

                varName = alocaOp(self.tokens.actual.value)

                actToken = self.tokens.selectNext()

                varToAlocate.children.append(varName)

                if actToken.type != "Variable" and actToken.type != "READ" and actToken.type != "Inteiro":
                    actToken = self.tokens.selectNext()

                resultado_alocate = Parser.orExpr(self)

                varToAlocate.children.append(resultado_alocate)

                actToken = self.tokens.actual

                resultado = varToAlocate

                return resultado

            if actToken.type == "PRINT":
                printEmpty = printOp(None)

                actToken = self.tokens.selectNext()

                if actToken.value == "(":
                    actToken = self.tokens.selectNext()

                    resultado_print = Parser.orExpr(self)

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

        if actToken.type == "FOR":
            forNode =  ForOp(None)

            actToken = self.tokens.selectNext()

            if actToken.value == "(":
                actToken = self.tokens.selectNext()
                resultado_aloca_for = Parser.parseCommand(self)
                forNode.children.append(resultado_aloca_for)

                actToken = self.tokens.actual
                actToken = self.tokens.selectNext()

                resultado_op_for = Parser.orExpr(self)
                forNode.children.append(resultado_op_for)

                actToken = self.tokens.actual
                actToken = self.tokens.selectNext()

                resultado_sum_for = Parser.parseCommand(self)
                forNode.children.append(resultado_sum_for)

                actToken = self.tokens.actual

                if actToken.value != ")":
                    raise Exception("Erro")
                else:
                    actToken = self.tokens.selectNext()

                    if actToken.value != "{":
                        raise Exception("Não abre chaves")

                resultado_for_block = Parser.parseCommand(self)
                forNode.children.append(resultado_for_block)

                resultado = forNode
                actToken = self.tokens.actual

                return resultado

            else:
                raise Exception("Error - Não abre parenteses")

        if actToken.type == "WHILE":
            whileNode = WhileOp(None)

            actToken = self.tokens.selectNext()

            if actToken.value == "(":
                actToken = self.tokens.selectNext()
                resultado_condition_while = Parser.orExpr(self)

                whileNode.children.append(resultado_condition_while)

                actToken = self.tokens.actual
                if actToken.value != ")":
                    raise Exception("Erro")
                else:
                    actToken = self.tokens.selectNext()

                    if actToken.value != "{":
                        raise Exception("Não abre chaves")

                resultado_while_block = Parser.parseCommand(self)

                whileNode.children.append(resultado_while_block)

                resultado = whileNode

                actToken = self.tokens.actual

                return resultado

            else:
                raise Exception("Não abre parenteses")

        if actToken.type == "IF":
            ifNode = ifOp(None)

            actToken = self.tokens.selectNext()

            if actToken.value == "(":
                actToken = self.tokens.selectNext()

                resultado_if_condition = Parser.orExpr(self)

                ifNode.children.append(resultado_if_condition)

                actToken = self.tokens.actual

                if actToken.value != ")":

                    raise Exception("ERRO")
                else:
                    actToken = self.tokens.selectNext()

                    # if actToken.value != "{":
                    #     raise Exception("Não abre chaves")

                resultado_if_block = Parser.parseCommand(self)
                # print(resultado_if_block)
                ifNode.children.append(resultado_if_block)
                resultado = ifNode
                actToken = self.tokens.actual

                if actToken.type == "ELSE":
                    actToken = self.tokens.selectNext()

                    if actToken.value != "{":
                        raise Exception("Não abriu chaves")
                    else:
                        actToken = self.tokens.selectNext()

                    resultado_else_block = Parser.parseCommand(self)

                    ifNode.children.append(resultado_else_block)

                    resultado = ifNode

                    actToken = self.tokens.selectNext()

                    if actToken.value == "else":
                        raise Exception("Mais de um else para o mesmo if")
                    # print(actToken.value)
            else:
                raise Exception("Não abriu parenteses")

            return resultado

        resultado = Parser.parseBlock(self)

        return resultado

    def parseBlock(self):
        actToken = self.tokens.actual
        resultsNodes = Operacoes(None)

        if actToken.value == "{":

            actToken = self.tokens.selectNext()

            while self.tokens.actual.value != "}":
                resultado = Parser.parseCommand(self)
                resultsNodes.children.append(resultado)
                actToken = self.tokens.actual
                # print(actToken.value)
            actToken = self.tokens.selectNext()

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

        somaa_c = 0
        somaf_c = 0

        varFiltered = filtroT.transformString(codigo)
        new_filtered = ''

        for item in range(len(varFiltered)):
            if varFiltered[item] == "\\" and varFiltered[item + 1] == "n" or varFiltered[item] == "n" and varFiltered[item - 1] == "\\":
                pass
            else:
                new_filtered += varFiltered[item]

        # if "*" not in varFiltered and "/" not in varFiltered and "+" not in varFiltered and "-" not in varFiltered:
        #     if len(varFiltered.replace(" ", "")) > 1:
        #         raise Exception("Error")

        # filtered = re.sub("[/*@*&?].*[*/@*&?]" ,"" ,codigo).replace(" ", "")
        filtered = re.sub(re.compile("/\*([^*]|[\r\n]|(\*+([^*/]|[\r\n])))*\*+/",re.DOTALL ) ,"" ,new_filtered).replace(" ", "").replace("\n", "")
        filtered = filtered.replace('\t', "")

        if 'else' in filtered and 'if' not in filtered:
            raise Exception("Error - Else without If")

        for item in range(len(filtered)):
            if (filtered[item] == "/" and filtered[item + 1] == "*") or filtered[item] == "*" and filtered[item + 1] == "/":
                raise Exception("Erro - comentario não esta fechando")

        for item in filtered:
            if item == "(":
                somaa_p += 1
            if item == ")":
                somaf_p += 1
            if item == "{":
                somaa_c += 1
            if item == "}":
                somaf_c += 1
        somaf = somaa_p + somaf_p
        somac = somaf_c + somaa_c
        if (somac % 2) != 0:
            raise Exception("Error - chave não esta fechando")
        if (somaf % 2) != 0:
            raise Exception("Error - parenteses não esta fechando")

        return filtered

# cFile = open(sys.argv[1], 'r')
# operacao = ''.join(cFile.read()).strip()
# print(operacao)
operacao = ''.join(sys.argv[1:])
pars = Parser()
resultado = pars.run(operacao)
resultado.Evaluate()
list_output = P_Code.commands
# pp.pprint(''.join(list(P_Code.commands)))
string_output = ''.join(list_output)
print(string_output)
