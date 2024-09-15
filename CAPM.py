# importing libraries
import streamlit as st
import pandas_datareader.data as web
import datetime
import pandas as pd
import yfinance as yf
import capm_functions

# setting page config
st.set_page_config(
        page_title="CAPM Calculator",
        page_icon="chart_with_upwards_trend",
        layout="wide",
    )

st.title('Capital Asset Pricing Calculator 📈')

# getting input from user
col1, col2= st.columns([1,1])
with col1:
    stocks_list = st.multiselect("Choose Stocks" , ('TSLA', 'AAPL','NFLX','MGM','MSFT','AMZN','NVDA','GOOGL'),['TSLA', 'AAPL','MSFT','NFLX'], key = "stock_list",)
with col2:
    year = st.number_input("Duration(in Years)",1,10)

try:
    # downloading data for SP500
    end = datetime.date.today()
    start = datetime.date(datetime.date.today().year - year, datetime.date.today().month, datetime.date.today().day)
    SP500 = web.DataReader(['sp500'], 'fred', start, end)

    # downloading data for the stock
    stocks_df = pd.DataFrame()
    for stock in stocks_list:
        data = yf.download(stock, period = f'{year}y')
        stocks_df[f'{stock}'] = data['Close']
    stocks_df.reset_index(inplace = True)
    SP500.reset_index(inplace = True)
    SP500.columns = ['Date','sp500']
    stocks_df['Date'] = stocks_df['Date'].astype('datetime64[ns]')
    stocks_df['Date'] = stocks_df['Date'].apply(lambda x:str(x)[:10])
    stocks_df['Date'] = pd.to_datetime(stocks_df['Date'])
    stocks_df = pd.merge(stocks_df, SP500, on = 'Date', how = 'inner')

    col1, col2 = st.columns([1,1])
    with col1:
        st.markdown('### Dataframe head')
        st.dataframe(stocks_df.head(), use_container_width = True)
    with col2:
        st.markdown('### Dataframe tail')
        st.dataframe(stocks_df.tail(), use_container_width = True)

    col1, col2 = st.columns([1,1])
    with col1:
        st.markdown('### Price of all the Stocks')
        # Plot interactive chart
        st.plotly_chart(capm_functions.interactive_plot(stocks_df))

    with col2:
        st.markdown('### Price of all the Stocks (After Normalizing)')
        # Plot normalized interactive chart
        st.plotly_chart(capm_functions.interactive_plot(capm_functions.normalize(stocks_df)))

    # calculating daily return 
    stocks_daily_return = capm_functions.daily_return(stocks_df)

    beta = {}
    alpha = {}

    for i in stocks_daily_return.columns:
        # Ignoring the date and S&P500 Columns 
        if i != 'Date' and i != 'sp500':
                # calculate beta and alpha for all stocks
                b, a = capm_functions.calculate_beta(stocks_daily_return, i)
                beta[i] = b
                alpha[i] = a

    col1, col2 = st.columns([1,1])

    beta_df = pd.DataFrame(columns = ['Stock','Beta Value'])
    beta_df['Stock'] = beta.keys()
    beta_df['Beta Value'] = [str(round(i,2)) for i in beta.values()]


    with col1:
        st.markdown('### Calculated Beta Value ')
        st.dataframe(beta_df, use_container_width = True)

    # Calculate return for any security using CAPM  
    rf = 0 # risk free rate of return
    rm = stocks_daily_return['sp500'].mean()*252 # market potfolio return
    return_df = pd.DataFrame()
    stock_list = []
    return_value = []
    for stock, value in beta.items():
        stock_list.append(stock)
        # calculate return
        return_value.append(str(round(rf+(value*(rm-rf)),2)))
    return_df['Stock'] = stock_list
    return_df['Return Value'] = return_value

    with col2:
        st.markdown('### Calculated Return')
        st.dataframe(return_df, use_container_width = True)

except:
    st.write("Please select valid stocks and years")