from Infrastructure.DbContext.SqlServerDbSession import database_session
from Infrastructure.Repository.DataBaseRepository import database_repo
import datetime

def delete_empty_tickers():

    rp = database_repo()
    rp.connect()
    db = database_session()
    db.connect()

    # ID generator
    IDs = rp.read_list_of_tickers()['ID']

    for ID in IDs:
        cmd = f'''
        select count(ID) as cnt from data where ID = {ID}
        '''
        db.execute(cmd)
        result= db.fetchall()
        thisCnt = result[0]['cnt']
        if thisCnt == 0:
            print(ID)
            cmd = f'''
            delete from tickers where ID = {ID}
            '''
            db.execute(cmd)
            db.commit()
    rp.close()
    db.close()

def delete_first_days():

    rp = database_repo()
    rp.connect()
    db = database_session()
    db.connect()

    # ID generator
    IDs = rp.read_list_of_tickers()['ID']

    for ID in IDs:
        print(ID)
        # select first date
        cmd = f'''
        select top 1 Date from data where ID = {ID} order by date asc
        '''
        db.execute(cmd)
        result = db.fetchall()
        if len(result) != 0:
            date = result[0]['Date']

            # delete first date
            cmd = f'''
            delete from data where ID = {ID} and date = '{date}'
            '''
            db.execute(cmd)
            db.commit()
            
    rp.close()
    db.close()

def delete_old_tickers():
    
    rp = database_repo()
    rp.connect()
    db = database_session()
    db.connect()

    # ID generator
    IDs = rp.read_list_of_tickers()['ID']

    for ID in IDs:
        cmd = f'''
        select max(Date) as maxDate from data where ID = {ID}
        '''
        db.execute(cmd)
        result= db.fetchall()
        maxDate = result[0]['maxDate']
        if maxDate < datetime.date(2018, 1, 1):
            print(ID)
            cmd = f'''
            delete from tickers where ID = {ID}
            '''
            db.execute(cmd)
            db.commit()
    rp.close()
    db.close()