import streamlit as st
import numpy as np
import pandas as pd
import altair as alt

# Streamlit UI
st.title('Farm Size vs Income Simulator')

# Introduction and Equation
introduction = """
This app simulates the income for smallholder cocoa farms by considering various input parameters that affect farm productivity and profitability. By adjusting these parameters, users can visualize how changes in farming practices or market conditions might influence the income of smallholder farms. The model incorporates several key components:

1. **Farm Size:** The total area of the farm measured in hectares. Larger farms may yield more produce but also require more labor and materials.

2. **Yield per Hectare (YH):** The amount of cocoa produced per hectare. This can vary based on factors like farming practices, soil fertility, and climate.

3. **Material Costs per Hectare (MCH):** The expenses incurred for materials such as fertilizers and pesticides for each hectare. Efficient use of materials can reduce costs and increase profitability.

4. **Labor Time per Hectare (LTH):** The number of labor days required per hectare. This reflects the labor intensity of the farm and can vary based on the farming methods used.

5. **Cocoa Market Price (CMP):** The selling price of cocoa per unit. Market prices can fluctuate based on global supply and demand.

6. **Maximum Labor Time (MLT):** The maximum number of days a single farmer can work in a year. This reflects the physical and time limitations of individual farmers.

7. **Labor Cost (LC):** The daily cost of hiring additional labor. This cost is incurred only when the labor requirements exceed what the farm owner can manage alone.

8. **Standard Labor Time per Hectare (standard_LTH):** Represents the average or standard labor time required per hectare. It's used to estimate the area a single farmer can manage without hiring additional labor.

The calculations in the app are broken down as follows:

1. **Revenue Calculation:**
   $$
   \\text{Revenue} = \\text{Yield per Hectare} \\times \\text{Farm Size} \\times \\text{Cocoa Market Price}
   $$
   Revenue represents the total income from selling the cocoa produced on the farm.

2. **Material Costs Calculation:**
   $$
   \\text{Material Costs} = \\text{Farm Size} \\times \\text{Material Costs per Hectare}
   $$
   Material Costs account for the expenses on materials required to maintain the farm.

3. **Labor Costs Calculation:**
   $$
   \\text{Labor Costs} = \\max(0, (\\text{Labor Time per Hectare} \\times \\text{Farm Size} - \\text{Maximum Labor Time})) \\times \\text{Labor Cost}
   $$
   Labor Costs are incurred for hired labor when the required labor time for the farm size exceeds what the farm owner can manage alone.

4. **Income Calculation:**
   $$
   \\text{Income} = \\text{Revenue} - \\text{Material Costs} - \\text{Labor Costs}
   $$
   Income is the profit realized after subtracting material and labor costs from the revenue.

By inputting different values for these parameters, users can explore various scenarios and understand how changes in farm size, productivity, and costs impact the income of smallholder cocoa farms.
"""
st.markdown(introduction)


# Function to simulate the income based on input parameters
def simulate_income(farm_sizes, YH, MCH, LTH, CMP=2.5, MLT=2000, LC=10):
    incomes = []
    for size in farm_sizes:
        yield_total = YH * size
        material_cost_total = MCH * size
        farm_owner_labor_time = min(LTH * size, MLT)
        hired_labor_hours = max(0, (LTH * size) - MLT)
        income = (yield_total * CMP) - (material_cost_total) - (hired_labor_hours * LC)
        incomes.append(income)
    return incomes


# Input boxes for constants
CMP = st.number_input('Cocoa Market Price ($/kg)', value=2.5, step=0.10)
standard_LTH = st.number_input('Standard Labor Time per Hectare (days/year)', value=100, step=1)
MLT = st.number_input('Maximum Labor Time (days/year)', value=200)
LC = st.number_input('Labor Cost ($/day)', value=10)

# Calculate and display the area one farmer can manage alone
area_one_farmer_can_manage = MLT / standard_LTH
st.metric(label="Area one farmer can manage alone (in hectares)", value=f"{area_one_farmer_can_manage:.2f} hectares")

# Initialize a DataFrame to store all farm data and farmers data
all_farm_data = pd.DataFrame()
all_farmers_data = pd.DataFrame()

# Define the number of farms
num_farms = 2

# Create columns for each farm's input parameters
cols = st.columns(num_farms)

# Farm specific default values
default_values = {
    1: {'YH': 500, 'MCH': 200, 'LTH': 100},
    2: {'YH': 1500, 'MCH': 600, 'LTH': 160}
}

for i in range(num_farms):  # Loop for each farm
    with cols[i]:  # Use the column created for this farm
        st.subheader(f'Farm {i + 1} Parameters')
        
        # Input parameters for each farm
        YH = st.slider(f'Yield per Hectare (kg/year) for Farm {i + 1}', 
                       min_value=0, max_value=3000, 
                       value=default_values[i + 1]['YH'], 
                       step=10, key=f'YH{i + 1}')
        MCH = st.slider(f'Material Costs per Hectare ($) for Farm {i + 1}', 
                        min_value=0, max_value=1000, 
                        value=default_values[i + 1]['MCH'], 
                        step=10, key=f'MCH{i + 1}')
        LTH = st.slider(f'Labor Time per Hectare (days/year) for Farm {i + 1}', 
                        min_value=0, max_value=500, 
                        value=default_values[i + 1]['LTH'], 
                        step=1, key=f'LTH{i + 1}')
        
    # Farm sizes
    farm_sizes = np.arange(1, 11, 1)
    
    # Calculate incomes
    incomes = simulate_income(farm_sizes, YH, MCH, LTH, CMP, MLT, LC)
    
    # Calculate labor time and transform to number of full-time farmers
    labor_times = LTH * farm_sizes
    full_time_farmers = np.ceil(labor_times / MLT)  # This already includes the farm owner since it's rounded up
    
    # Store farm data in the DataFrame
    farm_data = pd.DataFrame({
        'Farm Size': farm_sizes,
        f'Farm {i + 1} Income': incomes,
        f'Farm {i + 1} Full-Time Farmers': full_time_farmers
    })
    
    # Combine data for all farms
    if all_farm_data.empty:
        all_farm_data = farm_data
    else:
        all_farm_data = all_farm_data.merge(farm_data, on='Farm Size')

# Melt the DataFrame for Altair
all_farm_data_melted = all_farm_data.melt('Farm Size', var_name='Farm', value_name='Income')

# Plotting the Income vs. Farm Size results using Altair
chart = alt.Chart(all_farm_data_melted).mark_line(point=True).encode(
    x=alt.X('Farm Size:Q', title='Farm Size'),
    y=alt.Y('Income:Q', title='Income'),
    color=alt.Color('Farm:N', scale=alt.Scale(domain=[f'Farm {i + 1} Income' for i in range(num_farms)], range=['#1f77b4', '#ff7f0e'])),
    tooltip=['Farm Size', 'Income', 'Farm']
).interactive().properties(
    width=700,
    height=400
)

st.altair_chart(chart, use_container_width=True)


# Melt the Full-Time Farmers DataFrame for Altair
all_farmers_data_melted = all_farm_data.melt('Farm Size', var_name='Farm', value_name='Full-Time Farmers', value_vars=[f'Farm {i + 1} Full-Time Farmers' for i in range(num_farms)])

# Plotting the Full-Time Farmers vs. Farm Size results using Altair
farmers_chart = alt.Chart(all_farmers_data_melted).mark_line(point=True).encode(
    x=alt.X('Farm Size:Q', title='Farm Size'),
    y=alt.Y('Full-Time Farmers:Q', title='Number of Full-Time Farmers'),
    color=alt.Color('Farm:N', scale=alt.Scale(domain=[f'Farm {i + 1} Full-Time Farmers' for i in range(num_farms)], range=['#1f77b4', '#ff7f0e'])),
    tooltip=['Farm Size', 'Full-Time Farmers', 'Farm']
).interactive().properties(
    width=700,
    height=400
)

st.altair_chart(farmers_chart, use_container_width=True)

# Display the combined data as a table
st.write('Combined Income and Full-Time Farmers Data Table')
st.dataframe(all_farm_data)
