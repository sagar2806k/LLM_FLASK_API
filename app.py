from flask import Flask, request, jsonify, render_template
from flask_mysqldb import MySQL
from langchain_groq import ChatGroq
import os
from dotenv import load_dotenv

load_dotenv()
os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")

app = Flask(__name__)

# MySQL connection
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'llm_model'

mysql = MySQL(app)

# Function to get LLM response
def get_llm_response(query):
    try:
        llm = ChatGroq(model="mixtral-8x7b-32768",groq_api_key=os.environ["GROQ_API_KEY"])
        response = llm.invoke(query)  # Use the correct method to invoke the model
        # Extract text from the response
        return response.content
    except Exception as e:
        print(f"Error generating LLM response: {e}")
        return "An error occurred."

@app.route('/')
def index():
    return "LLM FLASK APP"

@app.route('/query', methods=['POST'])
def handle_query():
    query_text = request.json.get('query')
    response_text = get_llm_response(query_text)

    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO queries (query_text, response_text) VALUES (%s, %s)", (query_text, response_text))
    mysql.connection.commit()
    cur.close()

    return jsonify({"query": query_text, "response": response_text})

@app.route('/form')
def form():
    return render_template('form.html')

@app.route('/submit', methods=['POST'])
def submit():
    query_text = request.form['query']
    response_text = get_llm_response(query_text)

    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO queries (query_text, response_text) VALUES (%s, %s)", (query_text, response_text))
    mysql.connection.commit()
    cur.close()

    return render_template('result.html', query=query_text, response=response_text)

if __name__ == '__main__':
    app.run(debug=True)
