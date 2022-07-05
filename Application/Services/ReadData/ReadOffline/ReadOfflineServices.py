from Application.Services.ReadData.ReadOffline.VolumeServices import averge_services
from Application.Services.ReadData.ReadOffline.IndicatorServices import indicator_services
from Application.Services.ReadData.ReadOffline.StaticLevelsServices import staticLevels_service

class read_offline_services():
    
    average = averge_services
    indicator = indicator_services
    staticLevels = staticLevels_service