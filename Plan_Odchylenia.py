import pandas as pd
import numpy as np
import streamlit as st
import altair as alt

def pad_index_column(df: pd.DataFrame, length: int = 30, fill_char: str = ' ') -> pd.DataFrame:
    df = df.copy()
    df.index = df.index.map(lambda x: str(x).ljust(length, fill_char))
    return df

def f_tabela(df,tytuł,kolumna):
    tabela=df
    tabela.index.name = tytuł
    tabela = pad_index_column(tabela, length=kolumna)
    styled_df = (
        tabela.style
        .format("{:,.2f}")
        .set_properties(**{"text-align": "right"}, subset=pd.IndexSlice[:, tabela.columns])
    )
    rows = len(tabela)
    st.dataframe(styled_df, height=rows * 36 + 40, use_container_width=True)


df_plan=pd.read_csv('Data/Raport_Plan.csv')

st.set_page_config(page_title='Raporty Medispace 2025',layout='centered')
st.title('Raport wyników sprzedaży Medispace 2025')
st.header('Odchylenia budżetowe',divider=True)

PLACE = st.sidebar.multiselect(
    'Wybierz placówkę',
    ['Spokojna', 'Brama Zachodnia'],
    ['Spokojna', 'Brama Zachodnia'])
M=st.sidebar.selectbox('Miesiąc analizy',(1,2,3,4,5,6,7,8,9,10,11,12))

r1,r2=st.tabs(['Raport miesięczny','Raport narastająco'])

with r1:

        # Wykres
    df_wykres_m=df_plan[df_plan['Lokalizacja'].isin(PLACE)]
    df_wykres_m=df_wykres_m.groupby(['M'],as_index=False)[['P_2025','W_2025']].sum()
    df_melted = df_wykres_m.melt(id_vars='M', value_vars=['P_2025', 'W_2025'],var_name='Typ', value_name='Wartość')
    df_melted['M'] = df_melted['M'].astype(str)
    order_M = [str(m) for m in range(1, 13)]
    chart = alt.Chart(df_melted).mark_bar().encode(
        x=alt.X('M:N', title='Miesiąc', sort=order_M),
        y=alt.Y('Wartość:Q', title='Wartość'),
        color=alt.Color('Typ:N',title='Typ danych',scale=alt.Scale(domain=['P_2025', 'W_2025'],range=['#003f5c', '#bfbfbf']),legend=alt.Legend(orient='bottom')),
        xOffset='Typ:N'
    ).properties(height=500,title='Porównanie planu i wykonania według miesięcy')
    st.altair_chart(chart,use_container_width=True)

    # Tabela
    df_plan_m=df_plan[(df_plan['Lokalizacja'].isin(PLACE))&(df_plan['M']==M)]
    df_plan_rm=df_plan_m.groupby(['Usługa'])[['P_2025','W_2025']].sum()
    df_plan_rm=df_plan_rm[(df_plan_rm['P_2025']>0)|(df_plan_rm['W_2025']>0)]
    df_plan_rm=df_plan_rm.sort_values(by='P_2025',ascending=False)
    total_row = pd.DataFrame(df_plan_rm.sum(numeric_only=True)).T
    total_row.index = ["Razem"]
    df_plan_rm = pd.concat([df_plan_rm, total_row])
    df_plan_rm['Odchylenie']=df_plan_rm['W_2025']-df_plan_rm['P_2025']
    df_plan_rm['Odchylenie']=df_plan_rm['Odchylenie'].fillna(0)
    df_plan_rm['Realizacja %']=(df_plan_rm['W_2025']/df_plan_rm['P_2025'])*100
    df_plan_rm['Realizacja %']=df_plan_rm['Realizacja %'].fillna(0)
    f_tabela(df_plan_rm,'Wykonanie miesięczne',60)

with r2:
    # Wykres
    df_wykres_ytd = df_plan[df_plan['Lokalizacja'].isin(PLACE)]
    df_wykres_ytd = df_wykres_ytd.groupby(['M'], as_index=False)[['P_2025', 'W_2025']].sum()
    df_wykres_ytd = df_wykres_m.sort_values('M')
    df_wykres_ytd['P_2025'] = df_wykres_ytd['P_2025'].cumsum()
    df_wykres_ytd['W_2025'] = df_wykres_ytd['W_2025'].cumsum()

    df_melted = df_wykres_ytd.melt(id_vars='M',value_vars=['P_2025', 'W_2025'],var_name='Typ',value_name='Wartość')
    df_melted['M'] = df_melted['M'].astype(str)
    df_melted['Typ'] = df_melted['Typ'].replace({'P_2025': 'Plan narastająco','W_2025': 'Wykonanie narastająco'})
    order_M = [str(m) for m in range(1, 13)]
    
    line_chart = alt.Chart(df_melted).mark_line(point=True).encode(
    x=alt.X('M:N', title='Miesiąc', sort=order_M),
    y=alt.Y('Wartość:Q', title='Wartość skumulowana'),
    color=alt.Color('Typ:N',title='Typ danych',scale=alt.Scale(domain=['Plan narastająco', 'Wykonanie narastająco'],range=['#003f5c', '#bfbfbf']),legend=alt.Legend(orient='bottom')),
    strokeDash=alt.StrokeDash('Typ:N',scale=alt.Scale(domain=['Plan narastająco', 'Wykonanie narastająco'],range=[[4, 4], [1, 0]]),legend=None)
    ).properties(
        width=700,
        height=500,
        title='Plan i wykonanie narastająco – wykres liniowy'
    )
    st.altair_chart(line_chart, use_container_width=True)


    df_plan_m=df_plan[(df_plan['Lokalizacja'].isin(PLACE))&(df_plan['M']<=M)]
    df_plan_rm=df_plan_m.groupby(['Usługa'])[['P_2025','W_2025']].sum()
    df_plan_rm=df_plan_rm[(df_plan_rm['P_2025']>0)|(df_plan_rm['W_2025']>0)]
    df_plan_rm=df_plan_rm.sort_values(by='P_2025',ascending=False)
    total_row = pd.DataFrame(df_plan_rm.sum(numeric_only=True)).T
    total_row.index = ["Razem"]
    df_plan_rm = pd.concat([df_plan_rm, total_row])
    df_plan_rm['Odchylenie']=df_plan_rm['W_2025']-df_plan_rm['P_2025']
    df_plan_rm['Odchylenie']=df_plan_rm['Odchylenie'].fillna(0)
    df_plan_rm['Realizacja %']=(df_plan_rm['W_2025']/df_plan_rm['P_2025'])*100
    df_plan_rm['Realizacja %']=df_plan_rm['Realizacja %'].fillna(0)
    f_tabela(df_plan_rm,'Wykonanie narastające',60)
