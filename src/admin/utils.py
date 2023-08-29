from enum import Enum


class Sort(str, Enum):
    BY_REGISTER_DATE = "BY_REGISTER_DATE"
    BY_LATEST_DOWNLOADS = "BY_LATEST_DOWNLOADS"
    BY_SPACE = "BY_SPACE"
    BY_NOTACTIVE = "BY_NOTACTIVE"
    
