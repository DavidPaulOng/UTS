import streamlit as st
import joblib
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler


model = joblib.load('XGB.pkl')
top_surnames = joblib.load("top_surnames.pkl")
OneHot_Geography = joblib.load('OneHot_Geography.pkl')
OneHot_Gender = joblib.load('OneHot_Gender.pkl')
OneHot_HasCrCard = joblib.load('OneHot_HasCrCard.pkl')
OneHot_IsActiveMember = joblib.load('OneHot_IsActiveMember.pkl')
OneHot_Surname = joblib.load('OneHot_Surname.pkl')


def main():
    st.title('UTS Churn Model Deployment')

    surname=st.text_input("Surname")
    credit_score = st.number_input("Credit Score", 0, 1000)
    geography  = st.selectbox("Geographical Location", ["Germany", "Spain", "France"])
    gender=st.radio("Gender", ["Male","Female"])
    age = st.number_input("Age", 0, 100)
    tenure=st.number_input("How long have you been a customer (in years)", 0,15)
    balance = st.number_input('Balance Amount', 0.00, 1000000.00, step = 0.2)
    NumOfProducts = st.number_input("Number of bank products you hold", 0, 15)
    options = {"Yes": 1, "No": 0}
    HasCrCard = options[st.radio("Do you have a credit card from this bank?", options.keys())]
    IsActiveMember = options[st.radio("Do you have an active membership status with this bank?", options.keys())]
    EstimatedSalary=st.number_input("Estimation of your salary", 0.00,1000000.00,  step=0.2)
    
    
    data = {'Surname' : str(surname), 'Credit Score' : int(credit_score), 'Geography':str(geography),
            'Gender':str(gender), 'Age':int(age), 'Tenure':int(tenure), 'Balance':float(balance),
            'NumOfProducts':int(NumOfProducts), 'HasCrCard':int(HasCrCard), 'IsActiveMember':int(IsActiveMember),
            'EstimatedSalary':float(EstimatedSalary)}
    
    df=pd.DataFrame([list(data.values())], columns= list(data.keys()))

    # log transform
    df["Age"] = np.log(df["Age"]+ 1e-8)
    df["Balance"] = np.log(df["Balance"]+ 1e-8)
    # standard scaler
    ss = StandardScaler()
    df[["Credit Score", 'Age', 'Balance', 'EstimatedSalary', "Tenure"]]= ss.fit_transform(df[["Credit Score", 'Age', 'Balance', 'EstimatedSalary', "Tenure"]])
    # take top names
    df["Surname"] = df["Surname"].apply(lambda x: x if x in top_surnames else 'Other')
    # one hot encoding
    onehots = [OneHot_Geography, OneHot_Gender, OneHot_HasCrCard, OneHot_IsActiveMember, OneHot_Surname]
    columnshot = ["Geography", "Gender", "HasCrCard", "IsActiveMember", "Surname"]
    df=df.reset_index()

    for onehot,column in zip(onehots, columnshot):
        temp = pd.DataFrame(onehot.transform(df[[column]]).toarray(),columns=onehot.get_feature_names_out())
        df = pd.concat([df.drop(columns=[column]), temp], axis = 1)
    

    if st.button('Make Prediction'):
        data=df      
        result = make_prediction(data)
        if(result == 1):
            st.success('Will Churn')
        else:
            st.success('Will Not Churn')

def make_prediction(data):
    input_array = np.array(data).reshape(1, -1)
    prediction = model.predict(input_array)
    return prediction[0]

if __name__ == '__main__':
    main()
