from text_base.combo import L2Searcher
from text_base.base import SearchAnswer
import pandas as pd


class SQE(L2Searcher):
    def __init__(self, path_to_csv: str):
        super().__init__('/home/tim0th/songs_csv_2/', 'cashe/')
        self.path = path_to_csv

    def get_SQE(self):
        k = 0
        fk = 0
        stk = 0
        ffk = 0
        mar = 0
        excel_data = pd.read_excel(self.path, sheet_name='Sheet1')
        query, result = excel_data['query'].tolist(), excel_data['result'].tolist()
        for j in range(0, len(query)):
            text = query[j]
            answer = result[j]
            ret = SearchAnswer
            ret = super().find(text)
            for i in range(5):
                if ret.documents[i] == answer:
                    mar += 1 / (1 + i)
                    k += 1
                    if i == 0:
                        fk += 1
                    elif i < 3:
                        stk += 1
                    else:
                        ffk += 1
                    # print(ret.documents[i])
        print(k / max(1, len(query)))
        print(fk / max(1, len(query)))
        print(stk / max(1, len(query)))
        print(ffk / max(1, len(query)))
        print(mar / max(1, len(query)))
