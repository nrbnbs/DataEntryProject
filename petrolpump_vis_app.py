import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px

# Display Title and Description
st.title("Petrol Pump Transaction Management Portal")

# Constants
Product = [
    "Petrol",
    "Diesel",
    "Luboil",
]
TransactionType = [
    "Cash",
    "Credit Card",
    "Debit Card",
    "UPI",
    "Other",
]

# Establishing a Google Sheets connection
conn = st.experimental_connection("gsheets", type=GSheetsConnection)

# Fetch existing vendors data
existing_data_p = conn.read(worksheet="PetrolPump", usecols=list(range(10)), ttl=2)
existing_data_p = existing_data_p.dropna(how="all")
#existing_data_p['SerialNumber'] = existing_data_p.reset_index().index + 1
# Convert to a Pandas DataFrame
#df = pd.DataFrame(existing_data_p[1:], columns=existing_data_p[0])  # Assuming the first row contains column headers

action = st.selectbox(
    "Choose an Action",
    [
        "New Data Entry",
        "View All Data",
        
    ],
)

if action == "New Data Entry":
    st.markdown("Enter the details of the new transaction below.")
    with st.form(key="data_form"):
        serial_number=existing_data_p.reset_index().index + 1
        entry_date = st.date_input(label="Date*")
        employee_code = st.text_input(label="EmployeeCode*")
        unit = st.text_input(label="WorkingUnit")
        product = st.selectbox(
            "Product*", options=Product, index=None
        )
        amount = st.number_input(label="Amount(Rs)*")
        rate = st.number_input(label="Rate(Rs)")
        transaction_type = st.selectbox(
            "Transaction Type*", options=TransactionType, index=None
        )
        additional_info = st.text_area(label="Additional Notes")


        st.markdown("**required*")
        submit_button = st.form_submit_button(label="Submit Entry Details")

        if submit_button:
            if not entry_date or not employee_code or not product or not transaction_type:
                st.warning("Ensure all mandatory fields are filled.")
            
            else:
                transaction_data = pd.DataFrame(
                    [
                        {
                            "SerialNumber": serial_number[len(serial_number)-1],
                            "Date": entry_date.strftime("%d/%m/%Y"),
                            "EmployeeCode": employee_code,
                            "WorkingUnit": unit,
                            "Product": product,
                            "Amount(Rs)": amount,
                            "Rate(Rs)": rate,
                            "Volume(lt)": amount/rate,
                            "TransactionType": transaction_type,
                            "AdditionalInfo": additional_info,
                        }
                    ]
                )
                updated_df = pd.concat([existing_data_p, transaction_data], ignore_index=True)
                conn.update(worksheet="PetrolPump", data=updated_df)
                st.success("Entry details successfully submitted!")


# View All Entries
elif action == "View All Data":
    st.dataframe(existing_data_p)


# ---- Set dataframe for visualisation ----
#st.set_page_config(page_title="Petrol Pump Transaction Dashboard", page_icon=":bar_chart:", layout="wide")
#df_vis=existing_data_p.drop(existing_data_p.index[[1]])
df_vis=existing_data_p   

# ---- SIDEBAR ----
st.sidebar.header("Please Filter Here:")
employee_code = st.sidebar.multiselect(
    "Select the Employee Code:",
    options=df_vis["EmployeeCode"].unique(),
    default=df_vis["EmployeeCode"].unique()
)

working_unit = st.sidebar.multiselect(
    "Select the Working Unit:",
    options=df_vis["WorkingUnit"].unique(),
    default=df_vis["WorkingUnit"].unique()
)
df_selection = df_vis.query(
    "EmployeeCode ==@employee_code & WorkingUnit ==@working_unit"
)

# Check if the dataframe is empty:
if df_selection.empty:
    st.warning("No data available based on the current filter settings!")
    st.stop() # This will halt the app from further execution.

# ---- MAINPAGE ----
st.title(":bar_chart: Petrol Pump Transaction Dashboard")
st.markdown("##")

# TOP KPI's
total_sales = int(df_selection["Amount(Rs)"].sum())

st.subheader("Total Amount of Transaction:")
st.subheader(f"INR {total_sales:,}")

st.markdown("""---""")

# SALES BY PRODUCT LINE [BAR CHART]
sales_by_product = df_selection.groupby(by=["Product"])[["Amount(Rs)"]].sum().sort_values(by="Amount(Rs)")
fig_product_sales = px.bar(
    sales_by_product,
    x=sales_by_product.index,
    y="Amount(Rs)",
    
    title="<b>Sales by Product</b>",
    color_discrete_sequence=["#0083B8"] * len(sales_by_product),
    template="plotly_white",
)
fig_product_sales.update_layout(
    plot_bgcolor="rgba(0,0,0,0)",
    xaxis=(dict(showgrid=False))
)

# SALES BY Transaction Type [BAR CHART]
sales_by_transaction = df_selection.groupby(by=["TransactionType"])[["Amount(Rs)"]].sum().sort_values(by="Amount(Rs)")
fig_transaction_sales = px.bar(
    sales_by_transaction,
    x=sales_by_transaction.index,
    y="Amount(Rs)",
    
    title="<b>Sales by Transaction Type</b>",
    color_discrete_sequence=["#0083B8"] * len(sales_by_transaction),
    template="plotly_white",
)
fig_transaction_sales.update_layout(
    plot_bgcolor="rgba(0,0,0,0)",
    xaxis=(dict(showgrid=False))
)

# SALES BY DAYs [BAR CHART]
sales_by_days = df_selection.groupby(by=["Date"])[["Amount(Rs)"]].sum()
fig_days_sales = px.bar(
    sales_by_days,
    x=sales_by_days.index,
    y="Amount(Rs)",
    title="<b>Sales by days</b>",
    color_discrete_sequence=["#0083B8"] * len(sales_by_days),
    template="plotly_white",
)
fig_days_sales.update_layout(
    xaxis=dict(tickmode="linear"),
    plot_bgcolor="rgba(0,0,0,0)",
    yaxis=(dict(showgrid=False)),
)

left_column, middle_column, right_column = st.columns(3)
left_column.plotly_chart(fig_days_sales, use_container_width=True)
middle_column.plotly_chart(fig_transaction_sales, use_container_width=True)
right_column.plotly_chart(fig_product_sales, use_container_width=True)


# ---- HIDE STREAMLIT STYLE ----
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)