import json

with open('test.txt',  encoding="utf-8") as file:
    mass = file.readlines()


with open("data.json", 'r') as file_js:
    data = json.load(file_js)
    data["titles"] = [
        "Тоска", "Ожидание наказания", "Отношение к будущему", "Прошлые неудачи", "Отношение к себе",
        "Удовольствие от жизни", " Самокритичность",  "Чувство вины", "Суицидальные мысли", 
        "Беспокойство", " Желание плакать", "Потеря интересов", "Раздражительность",
        "Способность принимать решения",  "Аппетит",  "Собственная нужность", "Концентрация внимания", 
        "Оценка внутренней энергии", "Усталость", "Режим сна", "Интерес к сексу"
    ]

def make_data():
    for el in mass:

        if '.' in el:
            el = el.replace(' ', '').replace('.\n', '')
            key = el
            data['questions'][key] = []

        elif el != '\n':
            value = el.replace('\n', '')
            data['questions'][key].append(value)
    
    with open("data.json", 'w') as file_js:
        json.dump(data, file_js, indent=4)


if __name__ == "__main__":
    make_data()





