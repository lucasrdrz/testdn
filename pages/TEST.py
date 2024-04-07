import pandas as pd
import streamlit as st
import pip

pip.main(["install","openpyxl"])

df = pd.read_excel("intento70-30-05-04.xlsx")

pdescripciones=pd.read_excel("FormatoNsPartes.xlsx")

daily = pd.read_excel("Daily.xlsx")



