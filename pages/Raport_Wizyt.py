import pandas as pd
import numpy as np
import streamlit as st

def pad_index_column(df: pd.DataFrame, length: int = 30, fill_char: str = ' ') -> pd.DataFrame:
    df = df.copy()
    df.index = df.index.map(lambda x: str(x).ljust(length, fill_char))
    return df

df_plan=pd.read_csv('Data/Raport_Plan.csv')