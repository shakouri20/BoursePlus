import requests

# request from web and return list of lists from csvFile
def getCsvData(url: str, splitters: list[str]= [';', ',']) -> list:
    """request from web and return list of lists from csvFile"""

    for _ in range(2):
        try:
            response = requests.get(url, timeout= 0.5)
            break
        except:
            pass
    else:
        return
    
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

