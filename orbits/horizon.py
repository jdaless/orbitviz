import requests
from datetime import datetime
import json

def getData(center: str, target: str, start: datetime, stop: datetime, step: int) -> str:
    MAKE_EPHEM="'YES'"
    EPHEM_TYPE="'VECTORS'"
    VEC_TABLE="'1'"
    REF_SYSTEM="'ICRF'"
    REF_PLANE="'ECLIPTIC'"
    VEC_CORR="'NONE'"
    CAL_TYPE="'M'"
    OUT_UNITS="'KM-S'"
    VEC_LABELS="'YES'"
    VEC_DELTA_T="'NO'"
    CSV_FORMAT="'YES'"
    OBJ_DATA="'NO'"
    t0 = start.strftime("'%Y-%b-%d %H:%M:%S.%f'")
    tn = stop.strftime("'%Y-%b-%d %H:%M:%S.%f'")
    r = requests.get((f'https://ssd.jpl.nasa.gov/api/horizons.api?'
                     f'MAKE_EPHEM={MAKE_EPHEM}&'
                     f'COMMAND={target}&'
                     f'EPHEM_TYPE={EPHEM_TYPE}&'
                     f'CENTER={center}&'
                     f'START_TIME={t0}&'
                     f'STOP_TIME={tn}&'
                     f"STEP_SIZE='{step}'&"
                     f'VEC_TABLE={VEC_TABLE}&'
                     f'REF_SYSTEM={REF_SYSTEM}&'
                     f'REF_PLANE={REF_PLANE}&'
                     f'VEC_CORR={VEC_CORR}&'
                     f'CAL_TYPE={CAL_TYPE}&'
                     f'OUT_UNITS={OUT_UNITS}&'
                     f'VEC_LABELS={VEC_LABELS}&'
                     f'VEC_DELTA_T={VEC_DELTA_T}&'
                     f'CSV_FORMAT={CSV_FORMAT}&'
                     f'OBJ_DATA={OBJ_DATA}'))
    return r.json()['result']

def getBodyInfo() -> list[dict]:
    r = requests.get('https://api.le-systeme-solaire.net/rest/bodies/')
    return r.json()['bodies']
