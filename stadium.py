import urllib
import pandas as pd
from sqlalchemy import create_engine

"""Генерация мест в БД и их ИД. ВЫПОЛНЯЕТСЯ ЕДИНОРАЗОВО"""

stadium = {'A1': [20, 20], 'A2': [10, 20], 'A3': [10, 20], 'A4': [20, 20], 'B1': [20, 20], 'B2': [20, 10],
           'C1': [20, 20], 'C2': [20, 20], 'C3': [20, 20], 'C4': [20, 20], 'D1': [20, 20], 'D2': [20, 20]}

id_list = []
sector_list = []
row_list = []
place_list = []

for el, counts in stadium.items():
    for rows in range(counts[0]):
        for places in range(counts[1]):
            # location_code = f"{el}{str((rows+1)).rjust(2,'0')}{str((places+1)).rjust(2,'0')}"
            # print(location_code)
            id_list.append(f"{el}{str((rows+1)).rjust(2,'0')}{str((places+1)).rjust(2,'0')}")
            sector_list.append(el)
            row_list.append(rows+1)
            place_list.append(places+1)


data = {'place_id': id_list,
        'sector': sector_list,
        'row': row_list,
        'place': place_list}

params = urllib.parse.quote_plus('DRIVER={SQL Server};SERVER=.\sqlexpress;DATABASE=coursework;Trusted_Connection=yes;')
conn = create_engine("mssql+pyodbc:///?odbc_connect=%s" % params)

frame = pd.DataFrame(data)
frame.to_sql('places', if_exists='append', index=False, con=conn)
print(frame)
