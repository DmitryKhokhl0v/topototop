import sys

class Node:
    def __init__(self, prob, symbol, left=None, right=None):
        # Шанс символа
        self.prob = prob

        # Символ (В верхних нодах будет суммой всех нижних)
        self.symbol = symbol

        # Дочерниий объект слева (Нода)
        self.left = left

        # Дочерниий объект справа (Нода)
        self.right = right

        # 1 или 0 
        self.code = ""


codes = dict()

def getCodes(node, value=''):
        newValue = value + str(node.code)

        if (node.left or node.right):
            getCodes(node.left, newValue)
            getCodes(node.right, newValue)
        else:
            codes[node.symbol] = newValue

        return codes

def probabilitiesToCodes(chances):
    nodes = []

    # converting symbols and probabilities into huffman tree nodes
    for i in range(len(chances)):
        symbol = chances[i][0]
        nodes.append(Node(chances[i][1], symbol))

    while len(nodes) > 1:
        # sort all the nodes in ascending order based on their probability
        nodes.sort(key=lambda x: x.prob)

        left = nodes[0]
        right = nodes[1]

        left.code = 1
        right.code = 0

        # combine the 2 smallest nodes to create new node
        newNode = Node(left.prob + right.prob, left.symbol + right.symbol, left, right)

        nodes.remove(left)
        nodes.remove(right)
        nodes.append(newNode)

    symbolDictionnary = getCodes(nodes[0])

    # print("The result:", symbolDictionnary)
    # new=[[item,symbolDictionnary[item]] for item in symbolDictionnary]
    # print(len(new))
    # for i in range(len(new)):
    #     print(new[i][0], new[i][1])

    print(symbolDictionnary)
    return symbolDictionnary




def encode(text):
    chances = []
    alphabet = []


    for character in text:
        if character not in alphabet:
            chance = text.count(character)
            chances.append([character, chance])
            alphabet.append(character)


    symbolDictionnary = probabilitiesToCodes(chances)
    result = ''
    for character in text:
        result += symbolDictionnary[character]
    

    print("Filesize before:", len(text) * 8, "bits")
    print("Filesize after:",  len(result), "bits (without the dictionnary)")

    return result, chances


def decode(text, chances):
    dictionnary = probabilitiesToCodes(chances)

    decodedText = symbol = ''
    for character in text:
        print(text)
        symbol += character
        if symbol in dictionnary:
            decodedText += dictionnary.get(symbol)
            symbol = ''
    return decodedText

def write_bytes(current_byte,output_file):    # Отдельный метод для записи строки длиннее 8 бит.
    while len(current_byte)>8:          # Переводим 8 символов в двоичный int и конвертируем в 1 байт, параметр "big"
        output_file.write(int(current_byte[0:8],2).to_bytes(1,"big")) # параметр "big" отвечает за то, с какой стороны начинается запись
                                                                      # нам он не важен, т.к. байт только один
        current_byte = current_byte[8:] # Отбрасываем записанную часть
    return current_byte                 # Возвращаем то, что не записали


if len(sys.argv) != 4:
    raise "Invalid agrument amount"

encodeOrDecode = sys.argv[1]


match encodeOrDecode:
    case '--encode':
        input_file = open(sys.argv[2], "r")
        output_file = open(sys.argv[3], "wb")

        textToEncode = input_file.readline()
        result, dictionnary = encode(textToEncode)

        currLine = str(len(codes))+"\n"    # Формируем первую строку
        output_file.write(currLine.encode("UTF-8"))   # Записываем в файл

        for key in dictionnary: # Записываем словарь количества вхождений в виде "<символ> <количство>"
            output_file.write((key[0] + " " + str(key[1]) + "\n").encode("UTF-8"))

        current_byte = ""   # Строка для побайтовой записи (содержит только "0" и "1", которые переводятся в int, а затем в byte)
        for line in input_file.readlines():
            for i in line:
                current_byte += dictionnary[i]       # Для каждого символа записываем в current_byte его код в виде строки
                current_byte = write_bytes(current_byte, output_file)  # Отправляем в метод для побайтовой записи

        extra_bits = 8-len(current_byte)                    # В конце у нас могут остаться недозаписанные биты
        current_byte = current_byte + "0"*extra_bits        # Дозаполняем строку нулями
        output_file.write(int(current_byte,2).to_bytes(1,"big"))  # Записываем это в файл
        output_file.write(extra_bits.to_bytes(1,"big"))           # Сохраняем то, сколько битов дописали



    case '--decode':
        input_file = open(sys.argv[2], "rb")
        output_file = open(sys.argv[3], "w")
        chances = []
        n = int(input_file.readline()) # Считываем размер словаря
        for i in range(n):
            line = input_file.readline().decode('utf-8')
            chances.append([line[0], int(line[2:])])
            
        
        current_byte = ""       # Строка из "0" и "1" для поиска в ней шифров
        current_code = ""       # Строка для обхода файла и проверки на соответствие с ключами словаря дешифрации

        for line in input_file.readlines():       # Переводим каждый байт входного файла в строку
            print(line)
            for i in line:
                print(bin(i))
                current_byte += "0"*(10 - len(str(bin(i)))) + str(bin(i))[2:]  #Если необходимо дописываем ведущие нули, т.к. int() их затирает

        extra_bits = int(current_byte[-8:], 2)  # Проверяем последний байт, в котором содержится кол-во "лишних" бит
        current_byte = current_byte[:-(8+extra_bits)]   # Удаляем бит с количеством и "лишние" биты
        codes_dict_new = {}
        for i in codes.keys():                     # Меняем местами ключ и значения словаря с кодами
            codes_dict_new.update({codes[i]:i})
        
        for i in current_byte:
            current_code += i               # Наращиваем current_code пока не станет соответствовать одному из шифров
            if current_code in codes_dict_new.keys():  # Когда соответствует - дешифруем
                output_file.write(codes_dict_new[current_code])
                current_code = ""                   # Сам current_code обнуляем


        encodedText = current_byte
        result = decode(encodedText, chances)
    
    case _:
        raise "First argument should be either --encode or --decode"

# output_file.write(result)
output_file.close()
input_file.close()
