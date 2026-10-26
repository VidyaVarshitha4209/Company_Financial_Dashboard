import os
import pickle
from flask import Flask, jsonify, render_template, request
import pandas as pd

app = Flask(__name__)

# Global variable to store uploaded pandas dataset for Chatbot responses
LATEST_DATA = None

# Load Trained ML Model and Vectorizer
MODEL_PATH = 'model.pkl'
VECTORIZER_PATH = 'vectorizer.pkl'

model = None
vectorizer = None

if os.path.exists(MODEL_PATH) and os.path.exists(VECTORIZER_PATH):
  with open(MODEL_PATH, 'rb') as f:
    model = pickle.load(f)
  with open(VECTORIZER_PATH, 'rb') as f:
    vectorizer = pickle.load(f)


@app.route('/')
def home():
  return render_template('index.html')


# 1. PANDAS & ML INTEGRATED FILE UPLOAD ROUTE
@app.route('/upload', methods=['POST'])
def upload_file():
  global LATEST_DATA

  if 'file' not in request.files:
    return jsonify({'error': 'No file uploaded'}), 400

  file = request.files['file']
  if file.filename == '':
    return jsonify({'error': 'No file selected'}), 400

  try:
    # Pandas: Excel or CSV Reading
    if file.filename.endswith('.csv'):
      df = pd.read_csv(file)
    else:
      df = pd.read_excel(file)

    # Standardize column names
    df.columns = [str(col).strip().capitalize() for col in df.columns]

    # Handle missing essential columns
    if 'Revenue' not in df.columns:
      df['Revenue'] = 0
    if 'Expenses' not in df.columns:
      df['Expenses'] = 0

    # Ensure numeric values for calculations
    df['Revenue'] = pd.to_numeric(df['Revenue'], errors='coerce').fillna(0)
    df['Expenses'] = pd.to_numeric(df['Expenses'], errors='coerce').fillna(0)

    # Scikit-learn Machine Learning Predictions
    if model and vectorizer:
      texts = (
          df.astype(str).agg(' '.join, axis=1)
          if 'Text' not in df.columns
          else df['Text'].astype(str)
      
      )
      X_input = vectorizer.transform(texts)
      predictions = model.predict(X_input)

      if 'Status' not in df.columns:
        df['Status'] = predictions
    else:
      if 'Status' not in df.columns:
        df['Status'] = df.apply(
            lambda r: 'Profit' if r['Revenue'] >= r['Expenses'] else 'Loss',
            axis=1,
        )

    if 'Confidential' not in df.columns:
      df['Confidential'] = 'No'

    # Save to global variable for chatbot analysis
    LATEST_DATA = df.copy()

    # Convert DataFrame to JSON friendly Dictionary
    processed_records = df.to_dict(orient='records')

    # Calculate summary metrics using pandas
    total_revenue = float(df['Revenue'].sum())
    total_expenses = float(df['Expenses'].sum())
    net_profit = total_revenue - total_expenses
    total_records = len(df)

    return jsonify({
        'status': 'success',
        'data': processed_records,
        'summary': {
            'total_revenue': total_revenue,
            'total_expenses': total_expenses,
            'net_profit': net_profit,
            'total_records': total_records,
        },
    })

  except Exception as e:
    return jsonify({'error': f'Error processing file: {str(e)}'}), 500


# 2. CHATBOT ROUTE (Interacts with Uploaded Pandas Data)
@app.route('/chat', methods=['POST'])
def chat():
  global LATEST_DATA
  req_data = request.get_json()
  query = req_data.get('query', '').lower()

  if LATEST_DATA is not None:
    df = LATEST_DATA

    if 'loss' in query:
      loss_count = len(df[df['Status'].astype(str).str.lower() == 'loss'])
      response = (
          f'Current dataset lo total <b>{loss_count} entries</b> Loss record ga'
          ' categorized ayyayi.'
      )

    elif 'confidential' in query:
      conf_count = len(
          df[df['Confidential'].astype(str).str.lower().isin(['yes', 'true'])]
      )
      response = (
          f'Dataset lo total <b>{conf_count} records</b> Confidential status'
          ' kaligi unnayi.'
      )

    elif 'refund' in query:
      if 'Category' in df.columns:
        refund_df = df[
            df['Category'].astype(str).str.lower().str.contains('refund')
        ]
        if not refund_df.empty:
          total_refund = refund_df['Revenue'].sum() + refund_df['Expenses'].sum()
          response = (
              f'Refund category records count: <b>{len(refund_df)}</b>, Total'
              f' processed amount: <b>₹{total_refund:,.2f}</b>.'
          )
        else:
          response = 'Uploaded dataset lo specific Refund entries emi levu.'
      else:
        response = (
            'Uploaded data lo Category column ledhu refund details look up'
            ' cheydaniki.'
        )

    elif 'total' in query or 'summary' in query:
      total_rec = len(df)
      tot_rev = df['Revenue'].sum()
      tot_exp = df['Expenses'].sum()
      response = (
          f'Total Records: <b>{total_rec}</b>, Revenue: <b>₹{tot_rev:,.2f}</b>,'
          f' Expenses: <b>₹{tot_exp:,.2f}</b>.'
      )

    else:
      response = (
          'Nenu mee dataset ni analyze cheyagalanu! Total entries, loss'
          ' records, or confidential rows gurinchi adagandi.'
      )
  else:
    # Default rule-based fallback responses if no file is uploaded yet
    if 'loss' in query:
      response = (
          'Entries where Expenses exceed Revenue are flagged as Loss in the'
          ' dashboard.'
      )
    elif 'confidential' in query:
      response = (
          'Confidential entries are automatically identified using Machine'
          ' Learning model classification.'
      )
    elif 'refund' in query:
      response = (
          'Upload an Excel file to search for specific date and refund'
          ' transaction details.'
      )
    else:
      response = (
          'Hi! Upload an Excel/CSV spreadsheet above to query live financial'
          ' insights.'
      )

  return jsonify({'query': query, 'response': response})


if __name__ == '__main__':
  print('Starting Financial Dashboard Backend...')
  app.run(debug=True)