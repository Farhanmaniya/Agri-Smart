@echo off
echo Testing AgriSmart API...
echo.

echo 1. Testing health check...
curl -X GET "http://localhost:8000/api/health"
echo.
echo.

echo 2. Testing rainfall prediction...
curl -X POST "http://localhost:8000/api/predictions/rainfall" -H "Content-Type: application/json" -H "Authorization: Bearer %TOKEN%" -d "{\"temperature\": 25.0, \"humidity\": 60.0, \"pressure\": 1013.0, \"wind_speed\": 10.0, \"month\": 6, \"day_of_year\": 150}"
echo.
echo.

echo 3. Testing soil prediction...
curl -X POST "http://localhost:8000/api/predictions/soil-type" -H "Content-Type: application/json" -H "Authorization: Bearer %TOKEN%" -d "{\"ph\": 6.5, \"nitrogen\": 40.0, \"phosphorus\": 30.0, \"potassium\": 35.0, \"organic_matter\": 2.5, \"moisture\": 25.0, \"temperature\": 25.0}"
echo.
echo.

echo 4. Testing pest detection...
curl -X POST "http://localhost:8000/api/predictions/pest" -H "Content-Type: application/json" -H "Authorization: Bearer %TOKEN%" -d "{\"crop_type\": \"wheat\", \"pest_description\": \"Small insects on leaves\", \"damage_level\": \"medium\", \"area\": 1.0}"
echo.
echo.

echo 5. Testing models list...
curl -X GET "http://localhost:8000/api/predictions/models" -H "Authorization: Bearer %TOKEN%"
echo.
echo.

echo Test completed!
pause
