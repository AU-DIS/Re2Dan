import streamlit as st
import json

# Load the filters JSON
@st.cache_data()
def load_filters(filters_path):
    codes = json.load(open(filters_path))
    return codes

# Obtain units from filters dictionary
@st.cache_data()
def load_units(filters):
    units = list(filters.keys())
    units.insert(0, "All")
    return units

# Obtain departments for a unit from filters dictionary
@st.cache_data()
def load_departments(filters, unit):
    if not unit or unit == "All": return []
    departments = list(filters[unit]['depts'].keys())
    departments.insert(0, "All")
    return departments