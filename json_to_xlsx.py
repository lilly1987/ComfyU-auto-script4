import sys, os
import pandas as pd
from tinydb import TinyDB
from pathlib import *
sys.path.append(os.getcwd())

from libPrintLog import *

from tinydb.storages import JSONStorage
class UTF8JSONStorage(JSONStorage):
    def __init__(self, path, **kwargs):
        super().__init__(path, encoding='utf-8', **kwargs)

def json_to_xlsx(file):
    # print("f : ",file)
    db = TinyDB(file, storage=UTF8JSONStorage)
    table_names = db.tables()
    new_file = Path(file).with_suffix('.xlsx')
    if new_file.exists():
        new_file.unlink()
    with pd.ExcelWriter(new_file, engine='openpyxl') as writer:
        for table_name in table_names:
            table = db.table(table_name)
            data = table.all()
            for row in data:
                for col, value in row.items():
                    if isinstance(value, list):
                        row[col] = ', '.join(map(str, value))
            df = pd.DataFrame(data)
            sheet_name = str(table_name)[:31]
            df.to_excel(writer, sheet_name=sheet_name, index=False)
            for i, col in enumerate(df.columns):
                max_len = max(
                    df[col].astype(str).map(len).max(),
                    len(str(col))
                )
                max_len = min(max_len, 200)  # 최대 열 너비 제한 (예: 50)
                writer.sheets[sheet_name].column_dimensions[
                    chr(65 + i)
                ].width = max_len + 2  # 약간 여유를 둠
    print("count file : ",new_file)

# 명령줄 실행용
if __name__ == '__main__' or len(sys.argv) < 1:
    for file in sys.argv[1:]:
        json_to_xlsx(file)
