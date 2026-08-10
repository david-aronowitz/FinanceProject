FROM python:3.11-slim

# 2. הגדרת תיקיית העבודה בתוך הקונטיינר
WORKDIR /app

# 3. העתקת קובץ הדרישות והתקנת הספריות
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. העתקת כל שאר קבצי הקוד של הפרויקט לתוך הקונטיינר
COPY . .

# 5. חשיפת הפורט של Flask
EXPOSE 5000

# 6. שינוי: הפקודה הראשית היא app.py (לא main.py שלא קיים)
CMD ["python", "app.py"]
