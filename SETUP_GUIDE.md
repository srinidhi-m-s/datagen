# 🚀 Complete Setup Guide

## What You Have

A fully functional **Data Generation AI Platform** with:
- ✅ Google Gemini API integration (free tier)
- ✅ Beautiful, modern web interface
- ✅ Natural language data generation
- ✅ CSV/JSON export functionality
- ✅ Mock Kaggle and RAG services (for future implementation)

## 📋 Prerequisites

Before you start, make sure you have:
- [ ] Python 3.8 or higher installed
- [ ] Internet connection
- [ ] A Google account (for API key)

## 🔑 Step 1: Get Your Gemini API Key (2 minutes)

1. **Visit Google AI Studio**
   - Go to: https://makersuite.google.com/app/apikey
   
2. **Sign In**
   - Use your Google account
   
3. **Create API Key**
   - Click "Create API Key" button
   - Select "Create API key in new project" (or use existing)
   - Copy the generated key (starts with "AIza...")

4. **Important**: Keep this key safe! You'll need it in the next step.

## ⚙️ Step 2: Configure the Application (1 minute)

1. **Open the `.env` file** in the project root directory

2. **Add your API key**
   ```
   GEMINI_API_KEY=AIzaSyD...your_actual_key_here
   ```
   
3. **Save the file**

That's it! The application is now configured.

## 🎯 Step 3: Install and Run (2 methods)

### Method A: Automatic (Recommended for Windows)

Simply **double-click** the `start.bat` file. It will:
- ✅ Check Python installation
- ✅ Verify API key
- ✅ Install dependencies
- ✅ Start the server

### Method B: Manual

Open a terminal in the project directory and run:

```bash
# Install dependencies
pip install -r requirements.txt

# Start the server
cd backend
python main.py
```

## 🌐 Step 4: Access the Application

Once the server starts, you'll see:
```
🚀 Server starting on http://0.0.0.0:8000
```

Open your browser and go to:
- **http://localhost:8000**

## 🧪 Step 5: Test the Application

### Quick Test

1. **Enter a query** in the text area:
   ```
   Generate 10 customer records with name, email, age, and phone number
   ```

2. **Click "Generate Data"**

3. **Wait 2-5 seconds** for the AI to generate data

4. **View results** in the table below

5. **Download** as CSV or JSON if needed

### Try Example Queries

Click on any of the example cards at the bottom:
- 👥 Customer Data
- 📦 Product Catalog
- 💳 Transactions
- 👔 Employee Data

## ✅ Verification Checklist

After setup, verify everything works:

- [ ] Server starts without errors
- [ ] Browser opens to http://localhost:8000
- [ ] Page loads with beautiful dark theme
- [ ] Can enter a query
- [ ] "Generate Data" button works
- [ ] Data appears in table
- [ ] Can download CSV
- [ ] Can download JSON

## 🔧 Troubleshooting

### Problem: "GEMINI_API_KEY not found"

**Solution:**
1. Make sure you created a `.env` file (not `.env.example`)
2. Check that your API key is on the line: `GEMINI_API_KEY=your_key_here`
3. No spaces around the `=` sign
4. No quotes around the key

### Problem: "Python is not installed"

**Solution:**
1. Download Python from: https://www.python.org/downloads/
2. During installation, check "Add Python to PATH"
3. Restart your terminal/command prompt

### Problem: "Port 8000 is already in use"

**Solution:**
1. Close any other applications using port 8000
2. Or change the port in `.env`:
   ```
   PORT=8080
   ```

### Problem: "pip install fails"

**Solution:**
1. Try: `python -m pip install --upgrade pip`
2. Then: `pip install -r requirements.txt`
3. If still fails, install packages individually:
   ```bash
   pip install fastapi
   pip install uvicorn
   pip install google-generativeai
   pip install python-dotenv
   pip install pydantic
   ```

### Problem: "Empty or invalid data generated"

**Solution:**
1. Be more specific in your query
2. Specify the number of records you want
3. List the exact fields you need
4. Example: "Generate 20 products with SKU, name, category, and price"

### Problem: "Rate limit exceeded"

**Solution:**
- Free tier has limits (15 requests/minute)
- Wait a minute and try again
- For production, consider upgrading to paid tier

## 📚 Additional Resources

### Documentation Files
- `README.md` - Project overview
- `QUICKSTART.md` - Quick start guide
- `GEMINI_INTEGRATION.md` - Detailed API documentation
- `PROJECT_STRUCTURE.md` - Technical architecture

### Testing
Run the API test script:
```bash
python test_api.py
```

### API Documentation
Once server is running, visit:
- http://localhost:8000/docs (Interactive API docs)
- http://localhost:8000/redoc (Alternative docs)

## 🎨 Using the Application

### Writing Good Queries

**✅ Good Examples:**
```
Generate 50 customer records with name, email, age, phone, and address
Create 25 products with SKU, name, category, price, and stock quantity
Generate 40 transactions with ID, customer_id, amount, date, and status
```

**❌ Bad Examples:**
```
Give me data (too vague)
Customers (no details)
Make a database (unclear)
```

### Tips for Best Results

1. **Be Specific**: State exactly what you need
2. **Include Count**: Specify how many records
3. **List Fields**: Name all the fields you want
4. **Add Context**: Mention relationships if needed
5. **Use Examples**: Reference real-world scenarios

### Example Workflow

1. **Start Simple**
   ```
   Generate 5 customers with name and email
   ```

2. **Review Results**
   - Check if data looks realistic
   - Verify all fields are present

3. **Refine Query**
   ```
   Generate 50 customers with name, email, age (18-65), 
   phone number, address, and membership tier (bronze/silver/gold)
   ```

4. **Download Data**
   - Click "Download CSV" for spreadsheets
   - Click "Download JSON" for programming

## 🚀 Next Steps

### Immediate Use
- Generate data for your projects
- Test with different queries
- Export and use in your applications

### Future Enhancements
The application is designed to be extended:
- [ ] Integrate real Kaggle API
- [ ] Implement RAG for better context
- [ ] Add data validation
- [ ] Create user accounts
- [ ] Save query history
- [ ] Add more export formats

### Learning Opportunities
- Study `gemini_service.py` to learn prompt engineering
- Explore `app.js` to see frontend integration
- Modify `styles.css` to customize the design
- Extend `main.py` to add new endpoints

## 💡 Pro Tips

1. **Keyboard Shortcut**: Press `Ctrl+Enter` in the query box to generate
2. **Example Cards**: Click any example to auto-fill the query
3. **Schema Display**: Check the schema to see data types
4. **Context Options**: Enable Kaggle/RAG for mock context (future: real data)
5. **Batch Generation**: For large datasets, generate in batches of 50-100

## 🆘 Getting Help

If you encounter issues:

1. **Check the logs** in the terminal where the server is running
2. **Review documentation** in the project files
3. **Test API directly** using `test_api.py`
4. **Verify API key** at https://makersuite.google.com/app/apikey
5. **Check API quota** to ensure you haven't hit limits

## 🎉 You're Ready!

Your Data Generation AI Platform is now fully set up and ready to use!

**Quick Start Command:**
```bash
# Just run this:
start.bat
```

Then open: **http://localhost:8000**

---

**Enjoy generating data with AI! 🚀**

For questions or issues, refer to the documentation files or check the Gemini API documentation at https://ai.google.dev/docs
