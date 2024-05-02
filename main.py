import pandas as pd
import re
import numpy as np
import math
from math import log, log10
from config import *

def record_reading(lines):
    records = []
    for line in lines:
        if line[0]=="#":
            s = line.split(" ")
            y,d,m,h = s[1], s[2], s[3], s[4]
        else:
            if y in ['2022', '2023']:
                date = " ".join([y,d,m])
                hour = h
                data = [0]*13
                line = re.sub(' +',' ',line)
                #print(line)
                r = line.split(" ")
                #print(r)
                if len(r) <= 8:
                    continue
                #break
                data[0], data[1] = r[0][0], r[0][1]
                data[2] = r[1]
                data[3], data[4] = (r[2][:-1], r[2][-1])  if r[2] and r[2][-1] in ['A', 'B'] else (r[2], np.nan)
                data[5], data[6] = (r[3][:-1], r[3][-1])  if r[3] and r[3][-1] in ['A', 'B'] else (r[3], np.nan)
                data[7], data[8] = (r[4][:-1], r[4][-1])  if r[4] and r[4][-1] in ['A', 'B'] else (r[4], np.nan)
                data[9] = r[5] if r[5] else np.nan
                data[10] = r[6] if r[6] else np.nan
                data[11] = r[7] if r[7] else np.nan
                data[12] = r[8] if r[8] else np.nan
                l = []
                l.append(date)
                l.append(hour)
                l.extend(data)
                records.append(l)
    return records

def preprocess(df):
    df.replace('-9999', np.nan, inplace=True)
    df.replace('-8888', np.nan, inplace=True)
    pattern = r'[^-0-9]'
    df['TEMP'] = df['TEMP'].replace({pattern: np.nan}, regex=True)
    df['TEMP'].replace('', np.nan, inplace=True)
    df['TEMP'] = pd.to_numeric(df['TEMP'], errors='coerce')
    pattern = r'[^-0-9]'
    df['PRESS'] = df['PRESS'].replace({pattern: np.nan}, regex=True)
    df['PRESS'].replace('', np.nan, inplace=True)
    df['PRESS'] = pd.to_numeric(df['PRESS'], errors='coerce')
    
    df['GPH'] = df['GPH'].replace({pattern: np.nan}, regex=True)
    df['GPH'].replace('', np.nan, inplace=True)
    df['GPH'] = pd.to_numeric(df['GPH'], errors='coerce')
    
    df['DPDP'] = df['DPDP'].replace({pattern: np.nan}, regex=True)
    df['DPDP'].replace('', np.nan, inplace=True)
    df['DPDP'] = pd.to_numeric(df['DPDP'], errors='coerce')
    
    df['WDIR'] = df['WDIR'].replace({pattern: np.nan}, regex=True)
    df['WDIR'].replace('', np.nan, inplace=True)
    df['WDIR'] = pd.to_numeric(df['WDIR'], errors='coerce')
    
    df['WSPD'] = df['WSPD'].replace({pattern: np.nan}, regex=True)
    df['WSPD'].replace('', np.nan, inplace=True)
    df['WSPD'] = pd.to_numeric(df['WSPD'], errors='coerce')
    
    return df
def process_convention(df):
    df['RH'] = df['RH'].astype(float)/10.0
    df['TEMP'] = df['TEMP'].astype(float)/10.0
    df['PRESS'] = df['PRESS'].astype(float)/100
    df['GPH'] = df['GPH'].fillna(0)
    df['GPH'] = df['GPH'].astype(int)
    df['DPDP'] = df['DPDP'].fillna(0.0)
    df['DPDP'] = df['DPDP'].astype(float)/10.0
    df['WDIR'] = df['WDIR'].fillna(0.0)
    df['WDIR'] = df['WDIR'].astype(float)/10.0
    df['WSPD'] = df['WSPD'].fillna(0.0)
    df['WSPD'] = df['WSPD'].astype(float)/10.0

    return df
    
def convert_RH(RH_water, T):
        est = 1013.25 #hpa
        eio = 6.1173 #hpa
        e_w = -7.90298*((372.15/T)-1) + (5.02808)*log10((372.15/T)) - (1.3816* math.pow(10, -7))*(math.pow(10, 11.344*(1-(T/372.15)))-1) \
        + (8.1328 * math.pow(10, -3))*(math.pow(10, -3.49149*((372.15/T)-1)-1)) + log10(est)

        ew = math.pow(10,e_w)
        e_i = -9.09718*((273.16/T)-1) - (3.56654 * log10(273.16/T)) + 0.876793*(1-(T/273.16)) + log10(eio)
        ei = math.pow(10,e_i)

        ei = 100.0 * np.exp(  # type: ignore[return-value]
        (-6024.5282 / T)
        + 24.7219
        + (0.010613868 * T)
        - (1.3198825e-5 * (T**2))
        - 0.49382577 * np.log(T)
    )
        ew = 100.0 * np.exp(  # type: ignore[return-value]
        -6096.9385 / T + 16.635794 - 0.02711193 * T + 1.673952 * 1e-5 * T**2 + 2.433502 * np.log(T)
    )
    
        
        return (ew/ei)*RH_water

def calculate_pressure_altitude(press):
    press_alt_feet = (1-math.pow((press/1013.25), 0.190284))*145366.45
    #press_alt_mts = 0.3048 * press_alt_feet
    return press_alt_feet

def data_loading(station_name):
    file = open(data_path+"/"+station_codes[station_name]+"-data 2.txt", 'r')
    lines = file.readlines()
    records = record_reading(lines)
    header = ['Date', 'Hour','LVLTYP1', 'LVLTYP2', 'ETIME', 'PRESS', 'PFLAG', 'GPH', 'ZFLAG', 'TEMP', 'TFLAG', 'RH', 'DPDP', 'WDIR', 'WSPD']
    df = pd.DataFrame(records , columns= header)
    return df

def add_new_features(df):
    df['TEMP_K'] = df['TEMP'] + 273.15
    df['TEMP_F'] = (df['TEMP'] * 9/5) + 32
    df['PRESS_ALT'] = df['PRESS'].apply(calculate_pressure_altitude)
    df['RH_ice'] = df.apply(lambda row: convert_RH(row['RH'], row['TEMP_K']), axis=1)
    df['GPH_ft'] = df['GPH'] * 3.28084
    #print(df['Date'].dtype)
    df['Year']= df['Date'].str.split(' ').str[0]
    df['Month'] = df['Date'].str.split(' ').str[1]
    df['Day'] = df['Date'].str.split(' ').str[2]
    df['Date'] = pd.to_datetime(df['Date'])

    return df




