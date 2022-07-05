import json
import os
    

def deserialize_json(fileName, targetClass):
    file = fileName + '.json'
    data = open(file,)
    data_dict = json.loads(data) 
    target_object = targetClass.get_from_json(**data_dict)

def get_setting_by_name(*settingsName):
    ''' Gets and returns the settings from settings.json file. provide the hierarchy of settings consequently.
        \nFor example get_setting_by_name('operation', 'realtime')'''

    cwd = os.getcwd()
    file = r'{0}\Settings.json'.format(cwd)
    data = open(file,'r')
    data_dict = json.loads(data.read()) 
    temp_data = data_dict.copy()
    
    try:
        for settingName in settingsName:
            setting = temp_data[settingName]
            try:
                temp_data = setting.copy()
            except:
                x = 1
    except Exception as e :
        raise Exception('settingName not found. Please check the inputs.')
    
    return setting