import DefaultParams
import pymssql 


class database_session:
    def __init__(self) -> None:
        self.conn = None
        self.cursor = None

    def connect(self):
        # self.conn = pymssql.connect(host= DefaultParams.host, user=DefaultParams.user, password= DefaultParams.password, database= DefaultParams.database) 
        self.conn = pymssql.connect(server= DefaultParams.server, database= DefaultParams.database) 
        self.cursor = self.conn.cursor(as_dict= True) 

    def execute(self, cmd: str):
        self.cursor.execute(cmd)

    def executemany(self, cmd: str, DataList: list):
        self.cursor.executemany(cmd, DataList)

    def commit(self):
        self.conn.commit()

    def close(self):
        self.cursor.close()
        self.conn.close()

    def fetchall(self):
        return self.cursor.fetchall()
