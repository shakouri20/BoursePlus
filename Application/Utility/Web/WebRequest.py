import requests, time
from Colors import bcolors
import logging
import datetime
logging.getLogger("requests").setLevel(logging.ERROR)
logging.getLogger("urllib3").setLevel(logging.ERROR)

# request from web and return list of lists from csvFile
def getCsvData(url: str, splitters: list[str]= [';', ',']) -> list:
    """request from web and return list of lists from csvFile"""
    cnt = 0
    while True:
        try:
            response = requests.get(url, timeout=2, verify=False)
            break
        except:
            time.sleep(0.5)
            cnt += 1
            if cnt == 1:
                print(f'{bcolors.WARNING}Web Error{bcolors.ENDC}')
            if cnt == 20:
                cnt = 0
    
    text: str = response.text
    if len(splitters) == 1:
        dataList = text.split(splitters[0])
    elif len(splitters) == 2:
        dataList = text.split(splitters[0])
        dataList = [row.split(splitters[1]) for row in dataList]
    elif len(splitters) == 3:
        dataList = text.split(splitters[0])
        dataList = [row.split(splitters[1]) for row in dataList]
        for i in range(len(dataList)):
            for j in range(len(dataList[i])):
                dataList[i][j] = dataList[i][j].split(splitters[2])

    return dataList

