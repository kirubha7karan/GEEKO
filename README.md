# FlaskBot
A simple Flask chatbot application powered by Gemini 2.0 Flash.

## Prerequisites for Running the App
Get the Gemini API Key from the Google AI Studio.  
Link to refer - [Google AI Studio](https://ai.google.dev/gemini-api/docs/api-key)

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

## Set the Gemini API Key
Before running the Flask app, set the **GEMINI_KEY** environment variable with your API key.

### For Ubuntu (Linux) Users
1. Open the terminal and edit the `~/.bashrc` file:
   ```sh
   nano ~/.bashrc
   ```
2. Add the following line at the end of the file:
   ```sh
   export GEMINI_KEY="<your_api_key>"
   ```
3. Save and exit (Press **CTRL + X**, then **Y**, and **Enter**).
4. Apply the changes:
   ```sh
   source ~/.bashrc
   ```

### For macOS Users
1. If using **bash**, follow the same steps as Ubuntu (`~/.bashrc`).
2. If using **zsh** (default in newer macOS versions), edit `~/.zshrc`:
   ```sh
   nano ~/.zshrc
   ```
3. Add the following line:
   ```sh
   export GEMINI_KEY="<your_api_key>"
   ```
4. Save and exit, then apply the changes:
   ```sh
   source ~/.zshrc
   ```

### For Windows Users
**Using Command Prompt (Temporary for Current Session):**
```cmd
set GEMINI_KEY=<your_api_key>
```

**Using PowerShell (Temporary for Current Session):**
```powershell
$env:GEMINI_KEY="<your_api_key>"
```

**To Set Permanently (Windows Environment Variables):**
1. Open **Control Panel** → **System** → **Advanced system settings**.
2. Click on **Environment Variables**.
3. Under **System Variables**, click **New**.
4. Set **Variable name** as `GEMINI_KEY` and **Variable value** as `<your_api_key>`.
5. Click **OK**, then restart your terminal for changes to apply.

## Running the Flask App
Run the Flask application locally:
```sh
python app.py
```

The application should now be accessible on `http://127.0.0.1:5000/`. 
