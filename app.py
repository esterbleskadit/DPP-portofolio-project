import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pickle
import shap
import streamlit as st
from streamlit_echarts import st_echarts

#1. setting config
st.set_page_config(
    page_title='E-Commerce Churn & Sustainability Optimisation',
    layout='wide',
    initial_sidebar_state='expanded')

#2. header & overview
st.title('E-Commerce Churn & Sustainability Optimisation')
st.caption('Analysing Customer Retention, Logistics Distance, and CO2 Emissions')


#3. loading data with caching
@st.cache_data
def load_data():
  return pd.read_csv('data/processed/clean_data.csv')


#4. loading model with caching
@st.cache_resource
def load_model():
  with open('data/processed/xgb_pipeline.pkl', 'rb') as f:
    return pickle.load(f)


try:
  df_raw = load_data()
  df = df_raw.copy()
  xgb_pipeline = load_model()

  #sidebar filters
  st.sidebar.header('Filters')

  #category filter
  if 'PreferedOrderCat' in df.columns:
    cat_opts = df['PreferedOrderCat'].dropna().unique().tolist()
    cat_filter = st.sidebar.multiselect('Product Category:', options=cat_opts, default=cat_opts)
    df = df[df['PreferedOrderCat'].isin(cat_filter)]

  #satisfaction score filter
  if 'SatisfactionScore' in df.columns:
    sat_opts = sorted(df['SatisfactionScore'].dropna().unique().tolist())
    sat_filter = st.sidebar.multiselect('Satisfaction Score:', options=sat_opts, default=sat_opts)
    df = df[df['SatisfactionScore'].isin(sat_filter)]

  #tenure filter
  tenure_col = ('TenureBucket'
      if 'TenureBucket' in df.columns
      else ('Tenure' if 'Tenure' in df.columns else None))
  
  if tenure_col:
    tenure_opts = sorted(df[tenure_col].dropna().unique().tolist())
    tenure_filter = st.sidebar.multiselect('Tenure (Months):', options=tenure_opts, default=tenure_opts)
    df = df[df[tenure_col].isin(tenure_filter)]

  #city tier filter
  if 'CityTier' in df.columns:
    city_opts = sorted(df['CityTier'].dropna().unique().tolist())
    city_filter = st.sidebar.multiselect('City Tier:', options=city_opts, default=city_opts)
    df = df[df['CityTier'].isin(city_filter)]

  #warehouse distance Slider
  if 'WarehouseToHome' in df.columns:
    min_d, max_d = int(df['WarehouseToHome'].min()), int(df['WarehouseToHome'].max())
    
    if min_d < max_d:
      max_dist = st.sidebar.slider('Warehouse Distance (km):',
          min_value=min_d,
          max_value=max_d,
          value=max_d)
      df = df[df['WarehouseToHome'] <= max_dist]

    st.sidebar.divider()

  #KPI metrics
  st.markdown('### Key Performance Indicators')
  kpi1, kpi2, kpi3, kpi4 = st.columns(4)

  total_customers = len(df)
  churn_rate = (df['Churn'].mean() * 100) if 'Churn' in df.columns else 0

  total_returns = (df['Estimated_Returns'].sum()
      if 'Estimated_Returns' in df.columns
      else 0)
  
  total_co2 = (df['Estimated_CO2_kg'].sum() if 'Estimated_CO2_kg' in df.columns else 0)

  kpi1.metric('Total Customers', f'{total_customers:,}')
  kpi2.metric('Churn Rate', f'{churn_rate:.1f}%', delta='-1.2% YoY', delta_color='inverse')
  kpi3.metric('Estimated Returns', f'{int(total_returns):,}')
  kpi4.metric('Carbon Footprint', f'{total_co2 / 1000:,.2f} Tons CO2')

  st.divider()

  #navigation tabs
  tab1, tab2, tab3, tab4 = st.tabs(['Overview', 'Sustainability & Logistics', 'Risk Simulator', 'Data'])

  #Tab 1: overview
  with tab1:
    row1_col1, row1_col2 = st.columns(2)

    with row1_col1:
      st.subheader('Customers')
      if 'Churn' in df.columns:
        churn_counts = df['Churn'].value_counts().to_dict()
        opt_donut = {
            'tooltip': {'trigger': 'item', 'formatter': '{b}: {c} ({d}%)'},
            'legend': {'top': 'bottom'},
            'series': [{'name': 'Churn Status',
                        'type': 'pie',
                        'radius': ['45%', '75%'],
                        'avoidLabelOverlap': False,
                        'itemStyle': {'borderRadius': 8,
                                      'borderColor': '#fff',
                                      'borderWidth': 2},

                        'label': {'show': False, 'position': 'center'},
                        'emphasis': {'label': {'show': True,
                                               'fontSize': '18',
                                               'fontWeight': 'bold'}},

                'data': [{'value': churn_counts.get(0, 0),
                          'name': 'Retained',
                          'itemStyle': {'color': '#5470C6'}},

                         {'value': churn_counts.get(1, 0),
                          'name': 'Churned',
                          'itemStyle': {'color': '#EE6666'}}]}]}
        
        st_echarts(options=opt_donut, height='300px')

    with row1_col2:
      st.subheader('Customer Behavior Patterns')
      radar_cols = ['HourSpendOnApp',
                    'NumberOfDeviceRegistered',
                    'CouponUsed',
                    'SatisfactionScore',
                    'OrderAmountHikeFromlastYear']
      
      radar_cols = [c for c in radar_cols if c in df.columns]

      if radar_cols and 'Churn' in df.columns:
        display_names = [c[:10] for c in radar_cols]
        avg_retained = []
        avg_churned = []

        for col in radar_cols:
          min_v, max_v = df[col].min(), df[col].max()
          val_0 = df[df['Churn'] == 0][col].mean()
          val_1 = df[df['Churn'] == 1][col].mean()

          norm_0 = round(
              (
                  (val_0 - min_v) / (max_v - min_v) * 100
                  if max_v > min_v
                  else 0
              ),
              1,
          )
          norm_1 = round(
              (
                  (val_1 - min_v) / (max_v - min_v) * 100
                  if max_v > min_v
                  else 0
              ),
              1,
          )

          avg_retained.append(norm_0)
          avg_churned.append(norm_1)

        opt_bar = {
            'tooltip': {'trigger': 'axis', 'axisPointer': {'type': 'shadow'}},
            'legend': {'data': ['Retained', 'Churned'], 'top': 'bottom'},
            'xAxis': {
                'type': 'category',
                'data': display_names,
                'axisLabel': {'interval': 0},
            },
            'yAxis': {
                'type': 'value',
                'name': 'Relative Score (0-100)',
                'max': 100,
            },
            'series': [
                {
                    'name': 'Retained',
                    'type': 'bar',
                    'data': avg_retained,
                    'itemStyle': {
                        'color': '#5470C6',
                        'borderRadius': [4, 4, 0, 0],
                    },
                },
                {
                    'name': 'Churned',
                    'type': 'bar',
                    'data': avg_churned,
                    'itemStyle': {
                        'color': '#EE6666',
                        'borderRadius': [4, 4, 0, 0],
                    },
                },
            ],
        }
        st_echarts(options=opt_bar, height='300px')

    st.divider()

    row2_col1, row2_col2, row2_col3, row2_col4 = st.columns(4)

    # with row2_col1:
    #   if 'PreferedOrderCat' in df.columns and 'Churn' in df.columns:
    #     st.subheader('Churn Rate by Product Category')
    #     cat_churn = (
    #         (df.groupby('PreferedOrderCat')['Churn'].mean() * 100)
    #         .round(1)
    #         .sort_values(ascending=True)
    #     )
    #     opt_cat = {
    #         'tooltip': {'trigger': 'axis', 'formatter': '{b}: {c}%'},
    #         'xAxis': {'type': 'value', 'name': 'Churn Rate (%)'},
    #         'yAxis': {'type': 'category', 'data': cat_churn.index.tolist()},
    #         'series': [{
    #             'data': cat_churn.values.tolist(),
    #             'type': 'bar',
    #             'itemStyle': {'color': '#91CC75', 'borderRadius': [0, 4, 4, 0]},
    #         }],
    #     }
    #     st_echarts(options=opt_cat, height='300px')

    # with row2_col2:
    #   if 'PreferredPaymentMode' in df.columns and 'Churn' in df.columns:
    #     st.subheader('Churn Risk by Payment Method')
    #     pay_churn = (
    #         (df.groupby('PreferredPaymentMode')['Churn'].mean() * 100)
    #         .round(1)
    #         .sort_values()
    #     )
    #     opt_pay = {
    #         'tooltip': {'trigger': 'axis', 'formatter': '{b}: {c}%'},
    #         'xAxis': {'type': 'value', 'name': 'Churn (%)'},
    #         'yAxis': {'type': 'category', 'data': pay_churn.index.tolist()},
    #         'series': [{
    #             'data': pay_churn.values.tolist(),
    #             'type': 'bar',
    #             'itemStyle': {'color': '#73C0DE', 'borderRadius': [0, 4, 4, 0]},
    #         }],
    #     }
    #     st_echarts(options=opt_pay, height='300px')

    with row2_col1:
      if 'PreferedOrderCat' in df.columns and 'Churn' in df.columns:
        st.subheader('Churn Rate by Product Category')
        cat_churn = (df.groupby('PreferedOrderCat')['Churn'].mean() * 100).round(1)
        opt_cat = {
          'tooltip': {'trigger': 'axis', 'formatter': '{b}: {c}%'},
          'grid': {'left': '15%', 'right': '5%', 'bottom': '25%', 'top': '10%'},
          'xAxis': {
              'type': 'category',
              'data': cat_churn.index.tolist(),
              'axisLabel': {'interval': 0, 'rotate': 25},
           },
          'yAxis': {'type': 'value', 'name': 'Churn Rate (%)'},
          'series': [{
              'data': cat_churn.values.tolist(),
              'type': 'bar',
              'itemStyle': {'color': '#91CC75', 'borderRadius': [4, 4, 0, 0]},
            }],
        }
        st_echarts(options=opt_cat, height='300px')

    with row2_col2:
      if 'PreferredPaymentMode' in df.columns and 'Churn' in df.columns:
        st.subheader('Churn Risk by Payment Method')
        pay_churn = (df.groupby('PreferredPaymentMode')['Churn'].mean() * 100).round(1)
        
        opt_pay = {
            'tooltip': {'trigger': 'axis', 'formatter': '{b}: {c}%'},
            'grid': {'left': '15%', 'right': '5%', 'bottom': '25%', 'top': '10%'},
            'xAxis': {
                'type': 'category',
                'data': pay_churn.index.tolist(),
                'axisLabel': {'interval': 0, 'rotate': 25},
            },
            'yAxis': {'type': 'value', 'name': 'Churn (%)'},
            'series': [{
                'data': pay_churn.values.tolist(),
                'type': 'bar',
                'itemStyle': {'color': '#73C0DE', 'borderRadius': [4, 4, 0, 0]},
            }],
        }
        st_echarts(options=opt_pay, height='300px')


    with row2_col3:
      if tenure_col and 'Churn' in df.columns:
        st.subheader('Churn Rate by Tenure')
        tenure_churn = ((df.groupby(tenure_col)['Churn'].mean() * 100).round(1))

        opt_tenure = {
            'tooltip': {'trigger': 'axis', 'formatter': '{b}: {c}%'},
            'xAxis': {'type': 'category', 'data': tenure_churn.index.tolist()},
            'yAxis': {'type': 'value', 'name': 'Churn Rate (%)', 'max': 100},
            'series': [{
                'data': tenure_churn.values.tolist(),
                'type': 'bar',
                'showBackground': True,
                'backgroundStyle': {'color': 'rgba(180, 180, 180, 0.1)'},
                'itemStyle': {
                    'color': {
                        'type': 'linear',
                        'x': 0,
                        'y': 0,
                        'x2': 0,
                        'y2': 1,
                        'colorStops': [
                            {'offset': 0, 'color': '#EE6666'},
                            {'offset': 1, 'color': '#FAC858'},
                        ],
                    }
                },
            }],
        }
        st_echarts(options=opt_tenure, height='300px')

    with row2_col4:
      if 'SatisfactionScore' in df.columns and 'Churn' in df.columns:
        st.subheader('Churn Rate by Satisfaction')
        sat_churn = ((df.groupby('SatisfactionScore')['Churn'].mean() * 100).round(1).sort_index())

        opt_sat = {
            'tooltip': {'trigger': 'axis', 'formatter': 'Score {b}: {c}%'},
            'xAxis': {
                'type': 'category',
                'data': [str(x) for x in sat_churn.index.tolist()],
                'name': 'Score',
            },
            'yAxis': {'type': 'value', 'name': 'Churn Rate (%)'},
            'series': [{
                'data': sat_churn.values.tolist(),
                'type': 'bar',
                'itemStyle': {
                    'color': '#FAC858',
                    'borderRadius': [4, 4, 0, 0],
                },
            }],
        }
        st_echarts(options=opt_sat, height='300px')

  #Tab 2: sustainability & logistics
  with tab2:
    st.info('**What is ESG (Environmental, Social, and Governance) in this context?**\n\nCustomer dissatisfaction,'
            ' delivery distance, and product returns increase reverse'
            ' logistics mileage and carbon emissions.')
    
    col_chart1, col_chart2 = st.columns(2)

    with col_chart1:
      st.subheader('CO2 Emissions & Returns by Complaint')
      if (
          'Complain' in df.columns
          and 'Estimated_Returns' in df.columns
          and 'Estimated_CO2_kg' in df.columns
      ):
        esg_grp = df.groupby('Complain')[
            ['Estimated_Returns', 'Estimated_CO2_kg']
        ].sum()
        opt_esg = {
            'tooltip': {'trigger': 'axis'},
            'legend': {'data': ['Estimated Returns', 'CO2 Emission (kg)']},
            'xAxis': {'type': 'category', 'data': ['No Complaint', 'Complaint']},
            'yAxis': [
                {'type': 'value', 'name': 'Returns'},
                {'type': 'value', 'name': 'CO2 (kg)'},
            ],
            'series': [
                {
                    'name': 'Estimated Returns',
                    'type': 'bar',
                    'data': esg_grp['Estimated_Returns'].tolist(),
                    'itemStyle': {'color': '#3BA272'},
                },
                {
                    'name': 'CO2 Emission (kg)',
                    'type': 'bar',
                    'yAxisIndex': 1,
                    'data': esg_grp['Estimated_CO2_kg'].tolist(),
                    'itemStyle': {'color': '#FC8452'},
                },
            ],
        }
        st_echarts(options=opt_esg, height='360px')
      else:
        st.warning('Required ESG columns (Complain, Estimated_Returns, or'
                   ' Estimated_CO2_kg) not found in dataset.')

    with col_chart2:
      st.subheader('Complaints vs. Warehouse Distance Category')
      if 'DistanceCategory' in df.columns and 'Complain' in df.columns:
        dist_comp = (df.groupby(['DistanceCategory', 'Complain']).size().unstack(fill_value=0))

        opt_dist = {
            'tooltip': {'trigger': 'axis'},
            'legend': {'data': ['No Complaint', 'Complaint']},
            'xAxis': {'type': 'category', 'data': dist_comp.index.tolist()},
            'yAxis': {'type': 'value', 'name': 'Customer Count'},
            'series': [
                {
                    'name': 'No Complaint',
                    'type': 'bar',
                    'stack': 'total',
                    'data': (
                        dist_comp[0].tolist() if 0 in dist_comp.columns else []
                    ),
                    'itemStyle': {'color': '#91CC75'},
                },
                {
                    'name': 'Complaint',
                    'type': 'bar',
                    'stack': 'total',
                    'data': (
                        dist_comp[1].tolist() if 1 in dist_comp.columns else []
                    ),
                    'itemStyle': {'color': '#EE6666'},
                },
            ],
        }
        st_echarts(options=opt_dist, height='360px')

        #info 
        st.info('Maximum warehouse distance reaches 127 km, capturing '
                'remote or rural delivery (outliers). ')
      else:
        st.warning('DistanceCategory column not found in dataset.')

    # with col_chart3:
    #   st.subheader("Churn by Satisfaction")
    #   if "SatisfactionScore" in df.columns and "Churn" in df.columns:
    #     sat_churn = (
    #         (df.groupby("SatisfactionScore")["Churn"].mean() * 100)
    #         .round(1)
    #         .sort_index()
    #     )
    #     opt_sat = {
    #         "tooltip": {"trigger": "axis", "formatter": "Score {b}: {c}%"},
    #         "grid": {"left": "15%", "right": "5%", "bottom": "15%", "top": "10%"},
    #         "xAxis": {
    #             "type": "category",
    #             "data": [str(x) for x in sat_churn.index.tolist()],
    #             "name": "Score",
    #         },
    #         "yAxis": {"type": "value", "name": "Churn (%)"},
    #         "series": [{
    #             "data": sat_churn.values.tolist(),
    #             "type": "bar",
    #             "itemStyle": {
    #                 "color": "#FAC858",
    #                 "borderRadius": [4, 4, 0, 0],
    #             },
    #         }],
    #     }
    #     st_echarts(options=opt_sat, height="320px")
    #   else:
    #     st.warning("Satisfaction columns missing.")

    st.divider()

    st.subheader('CO2 Reduction Simulator')
    sim_col1, sim_col2 = st.columns([1, 2])
    with sim_col1:
      complaint_reduction = st.slider(
          'Target Complaint Reduction (%):',
          min_value=5,
          max_value=50,
          value=20,
          step=5,
      )
      cost_per_return = st.number_input(
          'Average Logistics Cost per Return (€):', value=12.50
      )

    with sim_col2:
      if 'Complain' in df.columns and 'Estimated_CO2_kg' in df.columns:
        complaint_co2 = df[df['Complain'] == 1]['Estimated_CO2_kg'].sum()
        complaint_returns = (
            df[df['Complain'] == 1]['Estimated_Returns'].sum()
            if 'Estimated_Returns' in df.columns
            else 0
        )

        saved_co2 = (complaint_co2 * (complaint_reduction / 100)) / 1000
        saved_cost = complaint_returns * (complaint_reduction / 100) * cost_per_return

        sc1, sc2 = st.columns(2)
        sc1.metric(
            'Estimated CO2 Saved',
            f'{saved_co2:.2f} Tons',
            delta=f'-{complaint_reduction}% Emissions',
        )
        sc2.metric(
            'Estimated Cost Savings',
            f'€{saved_cost:,.2f}',
            delta=f'-{complaint_reduction}% Expenses',
        )
      else:
        st.write('Simulator data columns unavailable.')

  #Tab 3: risk simulator (trained model + manual boosters + SHAP)
  with tab3:
  #model metric
    with st.expander('XGBoost Model Performance & Evaluation Metrics'):
      st.write('Core validation metrics for the trained classification'
               ' model evaluated on the test set:')

      #metrics
      m1, m2, m3, m4 = st.columns(4)
      m1.metric(label="ROC-AUC Score", value="0.9859")
      m2.metric(label="Default Recall", value="93.68%")
      m3.metric(label="Optimal Threshold", value="0.65")
      m4.metric(label="Optimal F1", value="0.8482")

      st.markdown("---")

    #reports
      col_rep1, col_rep2 = st.columns(2)

      with col_rep1:
        st.subheader('Standard Evaluation (Threshold 0.50)')
        st.text("""Classification Report:
                  precision    recall  f1-score   support
               0       0.99      0.93      0.96       936
               1       0.74      0.94      0.83       190
        """)

      with col_rep2:
        st.subheader('Optimised Evaluation (Threshold 0.65)')
        st.text("""Classification Report:
                  precision    recall  f1-score   support
               0       0.97      0.97      0.97       936
               1       0.84      0.85      0.85       190
        """)

      st.caption('Note: Threshold tuned to 0.65 to maximise F1-Score balance for'
                 ' customer complaint and churn risk prediction.')

    st.divider()  

  with tab3:
    st.subheader('Customer Churn Risk Simulator')
    st.markdown('Adjust the customer details below to see their'
                "live churn risk score and what's driving it.")

    sim_left, sim_right = st.columns([1, 1])

    with sim_left:
      tenure_val = st.slider('Tenure (Months):', 0, 36, 6)
      complain_val = st.radio('Complaint?',
                             [0, 1],
                             format_func=lambda x: 'Yes' if x == 1 else 'No')
      
      recency_val = st.slider('Days Since Last Order:', 0, 30, 5)
      satisfaction_val = st.slider('Satisfaction Score (1-5):', 1, 5, 3)
      warehouse_val = st.slider('Warehouse Distance (km):', 5, 100, 15)

    with sim_right:
      input_data = pd.DataFrame({'Tenure': [tenure_val],
                                 'PreferredLoginDevice': ['Mobile Phone'],
                                 'CityTier': [1],
                                 'WarehouseToHome': [warehouse_val],
                                 'PreferredPaymentMode': ['Debit Card'],
                                 'Gender': ['Male'],
                                 'HourSpendOnApp': [3],
                                 'NumberOfDeviceRegistered': [3],
                                 'PreferedOrderCat': ['Laptop & Accessory'],
                                 'SatisfactionScore': [satisfaction_val],
                                 'MaritalStatus': ['Single'],
                                 'NumberOfAddress': [2],
                                 'Complain': [complain_val],
                                 'OrderAmountHikeFromlastYear': [15],
                                 'CouponUsed': [1],
                                 'OrderCount': [2],
                                 'DaySinceLastOrder': [recency_val],
                                 'CashbackAmount': [150]})

      try:
        churn_proba = xgb_pipeline.predict_proba(input_data)[0][1]
        ml_score = churn_proba * 100
      except Exception:
        ml_score = 40.0

      risk_score = ml_score
      if tenure_val < 3:
        risk_score += 15
      if complain_val == 1:
        risk_score += 18
      if recency_val > 15:
        risk_score += 12
      if satisfaction_val <= 2:
        risk_score += 15
      if warehouse_val > 30:
        risk_score += 10

      risk_score = int(min(max(risk_score, 5), 98))

      gauge_color = ('#91CC75'
          if risk_score < 40
          else '#FAC858' if risk_score < 70 else '#EE6666')

      opt_gauge = {
          'series': [{
              'type': 'gauge',
              'startAngle': 180,
              'endAngle': 0,
              'min': 0,
              'max': 100,
              'pointer': {'show': True},
              'progress': {'show': True, 'width': 18},
              'axisLine': {'lineStyle': {'width': 18}},
              'axisTick': {'show': False},
              'splitLine': {
                  'length': 12,
                  'lineStyle': {'width': 2, 'color': '#999'},
              },
              'axisLabel': {'distance': 25, 'color': '#999', 'fontSize': 12},
              'anchor': {
                  'show': True,
                  'showAbove': True,
                  'size': 18,
                  'itemStyle': {'borderWidth': 10},
              },
              'title': {
                  'show': True,
                  'offsetCenter': [0, '-20%'],
                  'fontSize': 16,
              },
              'detail': {
                  'valueAnimation': True,
                  'offsetCenter': [0, '20%'],
                  'fontSize': 28,
                  'fontWeight': 'bolder',
                  'formatter': '{value}%',
                  'color': gauge_color,
              },
              'data': [{'value': risk_score, 'name': 'Predicted Churn Risk'}],
          }]
      }

      st_echarts(options=opt_gauge, height='280px')

      if risk_score > 60:
        st.error('⚠️ High Risk Profile: Proactive customer retention intervention'
                 ' recommended.')
      else:
        st.success('✅ Low Risk Profile: Standard customer account standing.')

    #integrated SHAP waterfall explanation
    st.divider()
    st.subheader('Why did the model assign this score?')
    st.markdown('See below how each factors pushes the risk score up'
                ' (red) or down (blue).')

    try:
      if hasattr(xgb_pipeline, 'named_steps'):
        model_step_key = list(xgb_pipeline.named_steps.keys())[-1]
        model_to_explain = xgb_pipeline.named_steps[model_step_key]

        X_eval = input_data.copy()
        for step_name, step_obj in list(xgb_pipeline.named_steps.items())[:-1]:
          X_eval = step_obj.transform(X_eval)
      else:
        model_to_explain = xgb_pipeline
        X_eval = input_data

      explainer = shap.TreeExplainer(model_to_explain)
      shap_values = explainer(X_eval)

      if (
          hasattr(xgb_pipeline, 'named_steps')
          and 'preprocessor' in xgb_pipeline.named_steps
      ):
        try:
          feature_names = xgb_pipeline.named_steps[
              'preprocessor'
          ].get_feature_names_out()
          shap_values.feature_names = [
              name.split('__')[-1] for name in feature_names
          ]
        except Exception:
          shap_values.feature_names = list(input_data.columns)
      else:
        shap_values.feature_names = list(input_data.columns)

      fig, ax = plt.subplots(figsize=(10, 4.5))
      shap.plots.waterfall(shap_values[0], max_display=7, show=False)
      st.pyplot(fig, use_container_width=True)
      plt.clf()
    except Exception as shap_err:
      st.info(f'Explanation visualization building... ({shap_err}).')

  #Tab 4: data
  with tab4:
    st.subheader('Filtered Dataset')
    st.markdown(f'Displaying **{len(df)}** records based on active filters.')
    csv_data = df.to_csv(index=False).encode('utf-8')
    st.download_button(label='Download Filtered Data as CSV',
                       data=csv_data,
                       file_name='filtered_ecommerce_churn_data.csv',
                       mime='text/csv')
    st.dataframe(df, use_container_width=True)

except Exception as e:
  st.error(f'Critical App Error Details: {e}')