def converter_para_decimal(numero, base_origem):

    try:
        if base_origem == 2:
            return int(numero, 2)
        elif base_origem == 8:
            return int(numero, 8)
        elif base_origem == 10:
            return int(numero, 10)
        elif base_origem == 16:
            return int(numero, 16)
        else:
            return None  # Base inválida
    except ValueError:
        return None  # Número inválido na base de origem


def converter_de_decimal(numero_decimal, base_destino):

    if base_destino == 2:
        return bin(numero_decimal)[2:]  # Remove o prefixo '0b'
    elif base_destino == 8:
        return oct(numero_decimal)[2:]  # Remove o prefixo '0o'
    elif base_destino == 16:
        return hex(numero_decimal)[2:]  # Remove o prefixo '0x'
    elif base_destino == 10:
        return str(numero_decimal)
    else:
        return "Base inválida!"  # Mensagem de erro para base inválida
