import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pickle

# Streamlit setup
st.title('Stock Trading Signals and Strategy Simulation')

# Upload CSV file
uploaded_file = st.file_uploader("Upload CSV file", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.write("DataFrame preview:", df.head())
    
    # Calculate signals
    count = int(np.ceil(len(df) * 0.1))
    signals = pd.DataFrame(index=df.index)
    signals['signal'] = 0.0
    signals['trend'] = df['Close']
    signals['RollingMax'] = signals['trend'].shift(1).rolling(count).max()
    signals['RollingMin'] = signals['trend'].shift(1).rolling(count).min()
    signals.loc[signals['RollingMax'] < signals['trend'], 'signal'] = -1
    signals.loc[signals['RollingMin'] > signals['trend'], 'signal'] = 1

    def buy_stock(real_movement, signal, initial_money=10000, max_buy=1, max_sell=1):
        starting_money = initial_money
        states_sell = []
        states_buy = []
        current_inventory = 0

        def buy(i, initial_money, current_inventory):
            shares = initial_money // real_movement[i]
            if shares < 1:
                st.write(
                    f'day {i}: total balances {initial_money}, not enough money to buy a unit price {real_movement[i]}'
                )
            else:
                if shares > max_buy:
                    buy_units = max_buy
                else:
                    buy_units = shares
                initial_money -= buy_units * real_movement[i]
                current_inventory += buy_units
                st.write(
                    f'day {i}: buy {buy_units} units at price {real_movement[i]}, total balance {initial_money}'
                )
                states_buy.append(0)
            return initial_money, current_inventory

        for i in range(real_movement.shape[0] - int(0.025 * len(df))):
            state = signal[i]
            if state == 1:
                initial_money, current_inventory = buy(i, initial_money, current_inventory)
                states_buy.append(i)
            elif state == -1:
                if current_inventory == 0:
                    st.write(f'day {i}: cannot sell anything, inventory 0')
                else:
                    if current_inventory > max_sell:
                        sell_units = max_sell
                    else:
                        sell_units = current_inventory
                    current_inventory -= sell_units
                    total_sell = sell_units * real_movement[i]
                    initial_money += total_sell
                    try:
                        invest = (
                            (real_movement[i] - real_movement[states_buy[-1]]) / real_movement[states_buy[-1]]
                        ) * 100
                    except:
                        invest = 0
                    st.write(
                        f'day {i}, sell {sell_units} units at price {total_sell}, investment {invest} %, total balance {initial_money},'
                    )
                states_sell.append(i)

        invest = ((initial_money - starting_money) / starting_money) * 100
        total_gains = initial_money - starting_money
        return states_buy, states_sell, total_gains, invest

    states_buy, states_sell, total_gains, invest = buy_stock(df['Close'], signals['signal'])

    # Plotting
    fig = plt.figure(figsize=(15, 5))
    plt.plot(df['Close'], color='r', lw=2.)
    plt.plot(df['Close'], '^', markersize=10, color='m', label='buying signal', markevery=states_buy)
    plt.plot(df['Close'], 'v', markersize=10, color='k', label='selling signal', markevery=states_sell)
    plt.title(f'total gains {total_gains}, total investment {invest}%')
    plt.legend()
    st.pyplot(fig)

    # Save model
    if st.button('Save Model'):
        # Assuming your trained model is stored in the variable 'model'
        model = None  # Replace with actual model
        with open('model.pkl', 'wb') as file:
            pickle.dump(model, file)
        st.success('Model saved as model.pkl')
else:
    st.write("Please upload a CSV file to proceed.")
