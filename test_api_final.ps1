# Final API Test Script for AgriSmart Backend
Write-Host "🚀 Testing AgriSmart API with Pre-trained Models..." -ForegroundColor Green

# Set token (replace with your actual token)
$token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJjZDdkOWZlMy0wOGU0LTQxOWUtOWU1NS1jYTg4ZTYwN2EzYzUiLCJleHAiOjE3NTc4MjMwMTV9.wHjox7Qq7dzY6thv_diQd82hjuaM5arSmV61HihnrXI"
$headers = @{"Authorization" = "Bearer $token"}

Write-Host "`n1. Testing Health Check..." -ForegroundColor Yellow
try {
    $healthResponse = Invoke-WebRequest -Uri "http://localhost:8000/api/health" -Method GET
    Write-Host "✅ Health Check: $($healthResponse.StatusCode)" -ForegroundColor Green
    Write-Host "Response: $($healthResponse.Content)" -ForegroundColor Cyan
} catch {
    Write-Host "❌ Health Check Failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n2. Testing Rainfall Prediction..." -ForegroundColor Yellow
try {
    $rainfallBody = '{"year": 2024, "subdivision": 1, "month": 6, "current_rainfall": 5.0}'
    $rainfallResponse = Invoke-WebRequest -Uri "http://localhost:8000/api/predictions/rainfall" -Method POST -Body $rainfallBody -ContentType "application/json" -Headers $headers
    Write-Host "✅ Rainfall Prediction: $($rainfallResponse.StatusCode)" -ForegroundColor Green
    Write-Host "Response: $($rainfallResponse.Content)" -ForegroundColor Cyan
} catch {
    Write-Host "❌ Rainfall Prediction Failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n3. Testing Soil Type Prediction..." -ForegroundColor Yellow
try {
    $soilBody = '{"nitrogen": 40.0, "phosphorus": 30.0, "potassium": 35.0, "temperature": 25.0, "moisture": 25.0, "humidity": 60.0}'
    $soilResponse = Invoke-WebRequest -Uri "http://localhost:8000/api/predictions/soil-type" -Method POST -Body $soilBody -ContentType "application/json" -Headers $headers
    Write-Host "✅ Soil Prediction: $($soilResponse.StatusCode)" -ForegroundColor Green
    Write-Host "Response: $($soilResponse.Content)" -ForegroundColor Cyan
} catch {
    Write-Host "❌ Soil Prediction Failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n4. Testing Pest Detection..." -ForegroundColor Yellow
try {
    $pestBody = '{"crop_type": "wheat", "pest_description": "Small insects on leaves", "damage_level": "medium", "area": 1.0}'
    $pestResponse = Invoke-WebRequest -Uri "http://localhost:8000/api/predictions/pest" -Method POST -Body $pestBody -ContentType "application/json" -Headers $headers
    Write-Host "✅ Pest Detection: $($pestResponse.StatusCode)" -ForegroundColor Green
    Write-Host "Response: $($pestResponse.Content)" -ForegroundColor Cyan
} catch {
    Write-Host "❌ Pest Detection Failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n5. Testing Models List..." -ForegroundColor Yellow
try {
    $modelsResponse = Invoke-WebRequest -Uri "http://localhost:8000/api/predictions/models" -Method GET -Headers $headers
    Write-Host "✅ Models List: $($modelsResponse.StatusCode)" -ForegroundColor Green
    Write-Host "Response: $($modelsResponse.Content)" -ForegroundColor Cyan
} catch {
    Write-Host "❌ Models List Failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n🎉 Test completed!" -ForegroundColor Green
