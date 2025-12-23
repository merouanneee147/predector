@echo off
echo ========================================
echo Systeme de Soutien Pedagogique - PFA V2
echo ========================================
echo.

echo [1/2] Demarrage du Backend Flask...
start "Backend Flask" cmd /k "cd backend && python app.py"

echo [2/2] Attente de 3 secondes...
timeout /t 3 /nobreak > nul

echo [2/2] Demarrage du Frontend Next.js...
start "Frontend Next.js" cmd /k "cd frontend-next && npm run dev"

echo.
echo ========================================
echo Serveurs demarres !
echo ========================================
echo Backend:  http://localhost:5000
echo Frontend: http://localhost:3000
echo ========================================
echo.
echo Appuyez sur une touche pour quitter...
pause > nul
