
import wikipedia
import json
a = [
    'covid-19 đến từ động vật nào?',
    'coronavirus là từ dơi',
    'có đúng là Covid lây lan qua việc ăn thịt dơi?',
    'dơi có thực sự là nguyên nhân gây ra virus ở Trung Quốc?',
    'virus corona Covid19 ở loài dơi.',
    'virus Corona có thực sự bắt đầu từ loài dơi?',
    'có phải coronavirus đến từ một con dơi',
    'có phải coronavirus đến từ phòng thí nghiệm',
    'coronavirus có đến từ động vật không',
    'có phải coronavirus đến từ động vật',
    'có phải coronavirus đến từ súp dơi',
    'có phải coronavirus đến từ dơi',
    'có phải coronavirus đến từ gà',
    'có phải coronavirus đến từ trung quốc',
    'có phải coronavirus đến từ việc ăn dơi',
    'có phải coronavirus đến từ tê tê',
    'có phải coronavirus đến từ rắn',
    'có phải coronavirus đến từ phòng thí nghiệm vũ hán',
    'có phải coronavirus bắt đầu từ một con dơi',
    'có phải coronavirus bắt đầu từ dơi',
    'có phải coronavirus bắt đầu từ việc ăn dơi',
    'có phải coronavirus bắt đầu từ dơi',
    'có phải covid-19 đến từ những người ăn thịt dơi?',
    'có phải virus corona đến từ động vật?',
    'có phải virus đến từ động vật?',
    'có phải coronavirus đến từ dơi',
    'có thật virus corona bắt nguồn từ dơi ở Trung Quốc?',
    'có phải virus thực sự từ một con dơi đã được ăn ở Trung Quốc?',
    'phác thảo cách thức virus corona xuất hiện.'
]

d = {}

for loc in a:
    try:
        result = wikipedia.summary(loc, sentences=3)
        if result:
                d[loc] = result
    except:
        resultSearch = wikipedia.search(loc, results=1)
        if len(resultSearch):
            result = wikipedia.summary(resultSearch[0], sentences=3)
            d[loc] = result
        else: 
            d[loc] = ''

f = open("test.json", 'w')

print("{", file = f)
for loc in a:
    print('"{}" : "{}",'.format(loc, d[loc]), file = f);

print("}", file = f)