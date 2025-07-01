import streamlit as st
import pandas as pd

def format_prod_data(prod_data):
    #format dictionary Data
    consolidated_report = {}
    for i, v in prod_data.items():
        if i != 'ROE (Return on Equity)':
            consolidated_report[i] = f"{v:.0f}"
        else: 
            consolidated_report[i] = f"{v:.2f}%"
    
    return consolidated_report

def consolidate_report(products, selected_products):
    #generate consolidated report data
    consolidated_prod = {}
    #iterate over the items of one product
    for prod_items in products.get(selected_products[0]).keys():
        #reset total for a selected item to 0
        item_total = 0
        #get amount for each product and update the total
        for prod_label in selected_products:
            item_total += products.get(prod_label).get(prod_items, 0)
        consolidated_prod[prod_items] = int(round(item_total,0))

    #Update the Gross Lending Margin
    consolidated_prod['Gross Lending Margin'] = int(round(consolidated_prod.get("Interest received", 0) + consolidated_prod.get("Cost of Funds incl liquids", 0),0))

    #Update the Lending margin after Credit Premium
    consolidated_prod['Lending margin after Credit Premium'] = int(round(consolidated_prod.get("Gross Lending Margin", 0) + consolidated_prod.get('Return on Capital Invested', 0) + consolidated_prod.get('Credit Premium', 0),0))

    #Update Lending Income Before Tax (LIBT)
    consolidated_prod['Lending Income Before Tax (LIBT)'] = int(round(consolidated_prod.get('Lending margin after Credit Premium',0) + consolidated_prod.get('Other credit based fee income',0) + consolidated_prod.get('Overheads related to lending business',0) + consolidated_prod.get('Additional Tier 1 Cost of Capital',0) + consolidated_prod.get('Tier 2 Cost of Capital',0), 0))

    #update Taxation
    consolidated_prod['Taxation'] = int(round(-1 * (consolidated_prod.get('Lending Income Before Tax (LIBT)', 0) * taxation_rate),0))

    #update LIACC
    consolidated_prod['LIACC'] = int(round(consolidated_prod.get('Lending Income Before Tax (LIBT)',0) + consolidated_prod.get('Taxation',0) + consolidated_prod.get('Core Equity Tier 1 Cost Of Capital', 0), 0))

    #update ROE (Return on Equity)
    consolidated_prod['ROE (Return on Equity)'] = round(((consolidated_prod.get('Lending Income Before Tax (LIBT)', 0) - (consolidated_prod.get('Taxation',0) * -1)) / consolidated_prod.get('Core equity capital holding', 1)) * 100,2)

    #remove Core equity capital holding
    consolidated_prod.pop('Core equity capital holding', '')

    return consolidated_prod

#product data elements
products = {
    "Credit Card": {
        "Interest received": 70500,
        "Cost of Funds incl liquids": -48740,
        "Gross Lending Margin": 21760,
        "Return on Capital Invested": 2056,
        "Credit Premium": -2176,
        "Lending margin after Credit Premium": 21639,
        "Other credit based fee income": 10000,
        "Overheads related to lending business": -13500,
        "Additional Tier 1 Cost of Capital": -91,
        "Tier 2 Cost of Capital": -111,
        "Lending Income Before Tax (LIBT)": 17937,
        "Taxation": -4843,
        "Core Equity Tier 1 Cost Of Capital": -4154,
        "LIACC": 8940,
        "Core equity capital holding": 28355
    },
    "Overdraft": {
        "Interest received": 42707,
        "Cost of Funds incl liquids": -32200,
        "Gross Lending Margin": 10507,
        "Return on Capital Invested": 1956,
        "Credit Premium": -2061,
        "Lending margin after Credit Premium": 10402,
        "Other credit based fee income": 10000,
        "Overheads related to lending business": -4100,
        "Additional Tier 1 Cost of Capital": -86,
        "Tier 2 Cost of Capital": -106,
        "Lending Income Before Tax (LIBT)": 16110,
        "Taxation": -4350,
        "Core Equity Tier 1 Cost Of Capital": -3953,
        "LIACC": 7807,
        "Core equity capital holding": 26984
    },
     "Guarantee": {
        "Interest received": 0,
        "Cost of Funds incl liquids": 0,
        "Gross Lending Margin": 0,
        "Return on Capital Invested": 1730,
        "Credit Premium": -1250,
        "Lending margin after Credit Premium": 480,
        "Other credit based fee income": 17991,
        "Overheads related to lending business": -8927,
        "Additional Tier 1 Cost of Capital": -76,
        "Tier 2 Cost of Capital": -94,
        "Lending Income Before Tax (LIBT)": 9374,
        "Taxation": -2531,
        "Core Equity Tier 1 Cost Of Capital": -3496,
        "LIACC": 3347,
        "Core equity capital holding": 23865
    }
}
taxation_rate = 0.27

#creating checkboxes of the items
st.title("Select Products to Consolidate")
prod_checkboxes = [(st.checkbox(prod_label), prod_label) for prod_label in products.keys()]

# Store selections in a list
selected_products = []
#map selected product with the label
for selected_prod, selected_label in prod_checkboxes:
    if selected_prod:
        selected_products.append(selected_label)

# Display result
if selected_products:
    #prepare the data to that I can show it using dictionary
    df = pd.DataFrame(list(format_prod_data(consolidate_report(products, selected_products)).items()), columns=["Item", "Amount"])
    
    st.write("Consolidated Statement Report")
    #display the report in a table format
    st.table(df)
else:
    st.warning("Please select at least one product.")
