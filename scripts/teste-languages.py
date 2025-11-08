qnt = int(input())

for i in range(0, qnt):
    valores = input().split()

    porc_cdb = int(valores[0])
    porc_lca = int(valores[1])
    qnt_dias = int(valores[2])

    if (qnt_dias <= 180):
        valor_cdb = porc_cdb * 0.775
    elif (qnt_dias <= 360):
        valor_cdb = porc_cdb * 0.80
    elif (qnt_dias <= 720):
        valor_cdb = porc_cdb * 0.825
    else:
        valor_cdb = porc_cdb * 0.85

    valor_lca = porc_lca * 0.95

    if valor_lca > valor_cdb:
        print('LCA')
    elif valor_cdb > valor_lca:
        print('CDB')
    else:
        print('IGUAL')