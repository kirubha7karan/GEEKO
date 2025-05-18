# FlaskBot
A simple Flask chatbot application powered by Gemini 2.0 Flash.

## Prerequisites for Running the App
1. Get the Gemini API Key from the Google AI Studio.  
 - Link to refer - [Google AI Studio](https://ai.google.dev/gemini-api/docs/api-key)
2. Set Required env variables - ref .env.sample file 
3. Setup the Weaviate in Local

## Installation

### Clone the Repository
```sh
cd <path/to/your/directory>
git clone <repository-url>
cd flaskbot
```

### Set Up a Virtual Environment
Create a virtual environment using Python's `venv` module:
```sh
python -m venv venv
```

Activate the virtual environment:
- On Windows:
  ```sh
  venv\Scripts\activate
  ```
- On macOS/Linux:
  ```sh
  source venv/bin/activate
  ```

### Install Dependencies
Install all required modules from `requirements.txt`:
```sh
pip install -r requirements.txt
```

## To use Testlink Function calls
1. **TLINK_API_KEY** and **TLINK_URL** has to be set

## Running the Flask App
Run the Weaviate:
```
docker-compose up
```
Run the Flask application locally:
```sh
python app.py
```

The application should now be accessible on `http://127.0.0.1:5000/`. 