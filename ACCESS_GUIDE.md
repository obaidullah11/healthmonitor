# How to Access the Health Monitoring System

## 🚨 Access URLs

Since your API is running on `0.0.0.0:8000`, you should access it using:

### ✅ Correct URLs to Use:

1. **API Documentation (Swagger UI)**:
   ```
   http://localhost:8000/docs
   ```
   OR
   ```
   http://127.0.0.1:8000/docs
   ```

2. **API Health Check**:
   ```
   http://localhost:8000/api/v1/health
   ```

3. **Frontend**:
   - Open File Explorer
   - Navigate to: `C:\Users\hp\Desktop\dataset\New folder\frontend`
   - Double-click on `index.html`
   - It will open in your default browser

## 🔧 Quick Access Steps

### Step 1: Verify API is Running
Your terminal shows the API is running:
```
INFO: Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

### Step 2: Open API Documentation
1. Open any web browser (Chrome, Firefox, Edge)
2. Type in address bar: `http://localhost:8000/docs`
3. You should see the Swagger UI interface

### Step 3: Access Frontend
1. Open Windows Explorer
2. Go to: `C:\Users\hp\Desktop\dataset\New folder\frontend`
3. Right-click on `index.html`
4. Select "Open with" → Your preferred browser

## 🌐 Alternative Access Methods

### Method 1: Direct Browser Access
```
1. Open your browser
2. For API docs: http://localhost:8000/docs
3. For health check: http://localhost:8000/api/v1/health
```

### Method 2: Using File Path for Frontend
```
file:///C:/Users/hp/Desktop/dataset/New%20folder/frontend/index.html
```
(Copy and paste this into your browser's address bar)

### Method 3: Create Desktop Shortcuts

**For API Documentation:**
1. Right-click on desktop
2. New → Shortcut
3. Enter: `http://localhost:8000/docs`
4. Name it: "Health API Docs"

**For Frontend:**
1. Navigate to frontend folder
2. Right-click `index.html`
3. Send to → Desktop (create shortcut)

## ⚠️ Common Issues & Solutions

### Issue 1: "Cannot reach this page"
**Solution**: Make sure the API is running (you should see the terminal window with the server logs)

### Issue 2: "0.0.0.0 refused to connect"
**Solution**: Use `localhost` or `127.0.0.1` instead of `0.0.0.0`

### Issue 3: Frontend not connecting to API
**Solution**: Check that the frontend JavaScript uses `http://localhost:8000` not `http://0.0.0.0:8000`

## 📋 Quick Test Commands

### From PowerShell:
```powershell
# Test API health
Invoke-WebRequest -Uri "http://localhost:8000/api/v1/health" | Select-Object -ExpandProperty Content

# Open API docs in browser
Start-Process "http://localhost:8000/docs"

# Open frontend
Start-Process "C:\Users\hp\Desktop\dataset\New folder\frontend\index.html"
```

### From Command Prompt:
```cmd
# Open API docs
start http://localhost:8000/docs

# Open frontend
start "" "C:\Users\hp\Desktop\dataset\New folder\frontend\index.html"
```

## 🎯 What You Should See

1. **API Documentation** (`http://localhost:8000/docs`):
   - Interactive Swagger UI
   - List of all API endpoints
   - "Try it out" buttons for testing

2. **Frontend** (`index.html`):
   - Health Monitoring System form
   - 6 input fields for health parameters
   - Submit button
   - Results display area

3. **Health Check** (`http://localhost:8000/api/v1/health`):
   ```json
   {
     "success": true,
     "message": "API is healthy and running",
     "data": {
       "api_status": "healthy",
       "model_status": {
         "models_loaded": true,
         "random_forest_available": true,
         "neural_network_available": true,
         "fallback_available": true
       }
     }
   }
   ```

## 🚀 Quick Start

1. **Keep the API running** (don't close the terminal with `python main.py`)
2. **Open browser** and go to: `http://localhost:8000/docs`
3. **Open frontend**: Navigate to frontend folder and open `index.html`
4. **Test it**: Enter health data in the form and click "Predict Health Status"

---

*If you still can't access, let me know what error message you're seeing!*

