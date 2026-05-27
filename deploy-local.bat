@echo off
echo Deploying DAIKUAN to Render...
echo.
echo Step 1: Pushing to GitHub...
git add .
git commit -m "Deploy to Render" -q
git push origin main
echo.
echo Step 2: Opening Render dashboard...
start https://dashboard.render.com/new
echo.
echo Step 3: Follow instructions on Render website to create service
echo.
echo After service is created, configure:
echo   - Name: daikuan-app
echo   - Environment: Python 3
echo   - Root Directory: ./
echo   - Build Command: pip install -r requirements.txt
echo   - Start Command: python server.py
echo   - Environment Variables:
echo     MAIL_USERNAME = 943411733@qq.com
echo     MAIL_PASSWORD = hipziemwzrifbdjh
