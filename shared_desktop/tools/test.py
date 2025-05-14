import requests
from openpyxl import load_workbook

# Загрузка Excel-файла
wb = load_workbook('адреса.xlsx')
ws = wb.active

# Добавим заголовок для результатов в столбец I
ws['I1'] = 'Статус UG405_OTU-1'

for row in ws.iter_rows(min_row=2, min_col=8, max_col=8):  # Столбец H (8)
    cell = row[0]
    ip = str(cell.value).strip()
    url = f"http://{ip}/hvi?file=cell9000.hvi&pos1=0&pos2=4"

    try:
        response = requests.get(url, timeout=5)
        text = response.text.strip()
    except Exception as e:
        ws.cell(row=cell.row, column=9).value = f"Ошибка: {e}"
        continue

    if not text.startswith(":TITLE"):
        ws.cell(row=cell.row, column=9).value = "Другой тип ДК"
        continue

    # Поиск строки с UG405_OTU-1
    status = "UG405_OTU-1 не найден"
    for line in text.splitlines():
        if line.startswith(":D") and "UG405_OTU-1" in line:
            parts = line.split(";")
            if len(parts) >= 6:
                status = parts[4]  # поле "OK", "FAULT" и т.п.
            break

    ws.cell(row=cell.row, column=9).value = status

# Сохраняем изменения
wb.save('адреса_результат.xlsx')
