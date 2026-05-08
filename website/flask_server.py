from flask import Flask, request, jsonify
import joblib
import pandas as pd
from flask_cors import CORS # Helps your frontend talk to your backend

app = Flask(__name__)
CORS(app)

# Load your saved brain and encoder
model = joblib.load('choredistro_model.pkl')
encoder = joblib.load('chore_encoder.pkl')

@app.route('/assign_chore', methods=['POST'])
def assign_chore():
    try:
        # 1. Get the data sent from your website
        data = request.get_json() # get_json() is slightly safer than .json
        
        # 2. Format it exactly how the model expects
        feature_names = ['chore_difficulty', 'zain_pts', 'jasmine_pts', 'justin_pts', 'chloe_pts']
        sample_df = pd.DataFrame([data], columns=feature_names)
        
        # 3. Make the prediction
        prediction_result = model.predict(sample_df)
        prediction_num = int(prediction_result[0])

        person_map = {
            0: "Chloe",
            1: "Jasmine",
            2: "Justin",
            3: "Zain"
        }
        predicted_name = person_map.get(prediction_num, "Unknown Person")
        
        # 4. Send the winner back to the website
        # We wrap predicted_name in str() just in case numpy returns a weird text format
        return jsonify({'assigned_to': str(predicted_name)})
        
    except Exception as e:
        # If ANYTHING goes wrong, this catches it!
        # It prints the exact reason to your VS Code terminal
        print(f"MODEL ERROR: {e}")
        
        # And it safely tells the browser it failed without breaking CORS
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(port=5000, debug=True)