from flask import Flask, render_template, redirect, url_for, flash, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from forms import RegistrationForm
from models import User, db
import requests  # Use requests to interact with the Azure OpenAI API
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SECRET_KEY'] = 'your_secret_key'
db.init_app(app)

# Set your Azure OpenAI API endpoint and key
AZURE_OPENAI_ENDPOINT = ""
AZURE_OPENAI_API_KEY = ""
AZURE_OPENAI_API_VERSION = "2023-05-15"
AZURE_DEPLOYMENT_NAME = "gpt-35-turbo" # Update to the appropriate API version

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        new_user = User(username=form.username.data, preferences=form.preferences.data)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('index'))
    return render_template('register.html', form=form)

@app.route('/chat', methods=['GET', 'POST'])
def chat():
    if request.method == 'GET':
        return render_template('chat.html')  # Render the chat template
    elif request.method == 'POST':
        data = request.get_json()
        user_input = data['user_input']

        # Prepare the request to Azure OpenAI
        headers = {
          "Content-Type": "application/json",
    "api-key": AZURE_OPENAI_API_KEY
           }

        body = {
           "messages": [{"role": "user", "content": user_input}],
             "model": AZURE_DEPLOYMENT_NAME
             }

        response = requests.post(
                f"{AZURE_OPENAI_ENDPOINT}openai/deployments/{AZURE_DEPLOYMENT_NAME}/chat/completions?api-version={AZURE_OPENAI_API_VERSION}",
                headers=headers,
            json=body
)
        if response.status_code == 200:
            ai_response = response.json()['choices'][0]['message']['content']
            return jsonify({'response': ai_response})  # Return the AI response as JSON
        else:
            # Log the status code and response content for debugging
            print(f"Error: {response.status_code}, Response: {response.text}")
            return jsonify({'response': 'Error: Unable to get a response from Azure OpenAI.'}), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
