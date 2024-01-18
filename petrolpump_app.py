import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

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

