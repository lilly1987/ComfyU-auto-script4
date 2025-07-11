from tinydb import TinyDB, Query
from tinydb.table import Table
from pathlib import *
from json_to_xlsx import *

from tinydb.storages import JSONStorage
class UTF8JSONStorage(JSONStorage):
    def __init__(self, path, **kwargs):
        super().__init__(path, encoding='utf-8', **kwargs)

# DB 파일 및 테이블 설정
class MyDB():
    def __init__(self):
        pass
    def init(self,path):
        self.path = Path(path,'count.db')
        self.db = TinyDB(Path(path,'count.db'), storage=UTF8JSONStorage)
        self.Combination: Table = self.db.table('Combination')
        self.CheckpointType: Table = self.db.table('CheckpointType')
        self.Checkpoint: Table = self.db.table('Checkpoint')
        self.Char: Table = self.db.table('Char')
        self.Loras: Table = self.db.table('Loras')
        self.Lora: Table = self.db.table('Lora')
        self.query = Query()

    def update(self,CheckpointType: str, Checkpoint: str, Char: str,Loras:set[str]):
        loras=list(Loras)

        for Lora in Loras:
            self._update(self.Lora,self.query.Lora == Lora,{'Lora': Lora,'count': 1})

        fields = {
            'CheckpointType': CheckpointType,
            'Checkpoint': Checkpoint,
            'Char': Char,
            'Loras': loras
        }

        for key, value in fields.items():
            self._update(getattr(self, key), getattr(self.query, key) == value, {key: value,'count': 1})

        self._update(
            self.Combination,
            (self.query.CheckpointType == CheckpointType) &
            (self.query.Checkpoint == Checkpoint) &
            (self.query.Char == Char) &
            (self.query.Loras == loras) ,
            {
                'CheckpointType': CheckpointType,
                'Checkpoint': Checkpoint,
                'Char': Char,
                'Loras': loras,   # 기본값으로 빈 리스트
                'count': 1
            }
        )

    def _update(self,table: Table,cond,new):
        # 3가지 조건 모두 일치하는 경우 검색
        result = table.get(cond)
        if result:
            # 단어가 존재하면 count 증가
            new_count = result['count'] + 1
            table.update({'count': new_count}, doc_ids=[result.doc_id])
        else:
            # 단어가 없으면 신규 추가
            table.insert(new)

    def json_to_xlsx(self):
        json_to_xlsx(self.path)