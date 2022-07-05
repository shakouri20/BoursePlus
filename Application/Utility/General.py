

def create_ID_dict(queryList: list) -> dict:
    '''returns a dict that its keys is IDs and values is a dict again with selected columns keys''' 
    ID_dict = {}

    # columns
    columns = list(queryList[0].keys())
    columns.remove('ID')
    previousID = 0

    # start process
    for row in queryList:

        thisID = row['ID']

        if thisID == previousID:
            for column in columns:
                ID_dict[thisID][column].append(row[column])

        else:
            if previousID in ID_dict:
                # reverse lists
                for column in columns:
                    ID_dict[previousID][column] = ID_dict[previousID][column][::-1]

            # start new ID calculation
            ID_dict[thisID] = {}
            for column in columns:
                ID_dict[thisID][column] = [row[column]]
                
        previousID = thisID

    # reverse last ID lists
    for column in columns:
        ID_dict[previousID][column] = ID_dict[previousID][column][::-1]
        
    return ID_dict     