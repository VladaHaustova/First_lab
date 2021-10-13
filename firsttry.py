import os
import zipfile
import hashlib
import requests
import re
import csv

# 1 распаковываем архив и извлекаем содержимое
directory_to_extract_to = 'D:\\PythonProjects\\directory_to_extract_to'
os.mkdir(directory_to_extract_to)

test_zip = zipfile.ZipFile('D:\\PythonProjects\\_lab1.zip')
test_zip.extractall(directory_to_extract_to)
test_zip.close()

# 2 создаем список всех txt файлов и получаем значения MD5 хеша для каждого файла
txt_files = []
for r, d, f in os.walk(directory_to_extract_to):
    for file in f:
        if file.endswith(".txt"):
            target_file = os.path.join(r, file)
            txt_files.append(target_file)
print("Список файлов с расширением txt: ")
for file in txt_files:
    print(file)

result = " "
print("Значения хэша файлов: ")
for file in txt_files:
    target_file_data = open(file, "rb")
    tmp = target_file_data.read()
    result = hashlib.md5(tmp).hexdigest()
    target_file_data.close()
    print(result)

# 3 ищем файл с определенным хешем, распечатываем путь к файлу и содержимое файла
target_hash = "4636f9ae9fef12ebd56cd39586d33cfb"
target_file = ''
target_file_data = ''

for r, d, f in os.walk(directory_to_extract_to):
    for file in f:
        temp = os.path.join(r, file)
        file_data = open(temp, "rb")
        tmp = file_data.read()
        if hashlib.md5(tmp).hexdigest() == target_hash:
            target_file = r + "\\" + file
            target_file_data = tmp
        file_data.close()

print("Путь к исходному файлу: ")
print(target_file)
print("Содержимое искомого файла: ")
print(target_file_data)

# 4 парсинг HTML страницы
r = requests.get(target_file_data)
result_dct = {}  # словарь для записи содержимого таблицы
counter = 0
headers = " "
lines = re.findall(r'<div class="Table-module_row__3TH83">.*?</div>.*?</div>.*?</div>.*?</div>.*?</div>', r.text)
for line in lines:
    if counter == 0:
        headers = re.sub(r'\<[^>]*\>', " ", line)  # Удаление тегов
        headers = re.findall("Заболели|Умерли|Вылечились|Активные случаи", headers)  # Извлечение списка заголовков
    temp = re.sub(r'\<[^>]*\>', ";", line)
    temp = re.sub(r'\xa0', '', temp)  # заменяем пробел \xa0 на обычный пробел
    temp = re.sub(r'[*]', '', temp)  # где *,заменяем на пробел
    temp = re.sub(r'^\W+', '', temp)  # убираем вначале строк буквенные коды стран
    temp = re.sub(r'\(.*?\)', '', temp)  # удаляем скобки и все что в них
    temp = re.sub('_', '-1', temp)  # заменяем нижнее подчеркиваие на -1
    temp = re.sub(';+', ';', temp)  # заменяем где много';' на одиночный символ ';'
    temp = re.sub(';', "|", temp)  # ; заменяем на |
    temp = re.sub(r'\|+$', '', temp)

    tmp_split = re.split(r'\|', temp)  # разбиваем строку на подстроки
    if tmp_split != headers:
        country_name = tmp_split[0]  # извлекаем и обрабатываем данные
        col1_val = tmp_split[1]
        col2_val = tmp_split[2]
        col3_val = tmp_split[3]
        col4_val = tmp_split[4]

        result_dct[country_name] = [0, 0, 0, 0]  # записываем извлеченные данные в словарь
        result_dct[country_name][0] = int(col1_val)
        result_dct[country_name][1] = int(col2_val)
        result_dct[country_name][2] = int(col3_val)
        result_dct[country_name][3] = int(col4_val)
    counter += 1

# 5 записываем данные из словаря в файл
output = open('data.csv', 'w')
fw = csv.writer(output, delimiter=";")
fw.writerow(headers)  # запись headers в файловый объект

for key in result_dct.keys():
    fw.writerow([key, result_dct[key][0], result_dct[key][1], result_dct[key][2], result_dct[key][3]])
output.close()

# 6 выводим данные указанной страны
target_country = input("Введите название страны: ")
print(result_dct[target_country])