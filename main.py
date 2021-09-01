import sys

conta = ''.join(sys.argv[1:])

def operacao(x):
    lista_valores = []
    lista_todos_valores = []
    lista_operacoes = []
    valor_result = 0
    valor_result_final = 0


    for item in range(len(x)):
        if x[item] != "+" or x[item] != "-" and x[item] != " ":
            lista_valores.append(x[item])

        if x[item] == "+" or x[item] == "-":
            lista_valores = lista_valores[:-1]
            lista_operacoes.append(x[item])

            valor = int(''.join(lista_valores))
            lista_todos_valores.append(valor)

            lista_valores.clear()

        if item == (len(x) - 1):
            valor = int(''.join(lista_valores))
            lista_todos_valores.append(valor)

    for item in range(len(lista_operacoes)):
        if item == 0:
            if lista_operacoes[item] == "+":
                valor_result_final = lista_todos_valores[item] + lista_todos_valores[item + 1]

            if lista_operacoes[item] == "-":
                valor_result_final = lista_todos_valores[0] - lista_todos_valores[1]

        if item != 0 and item < (len(lista_todos_valores) - 1):
            if lista_operacoes[item] == "+":
                valor_result = valor_result_final + lista_todos_valores[item + 1]
                valor_result_final = valor_result

            if lista_operacoes[item] == "-":
                valor_result = valor_result_final - lista_todos_valores[item + 1]
                valor_result_final = valor_result

    return valor_result_final

print(operacao(conta))
