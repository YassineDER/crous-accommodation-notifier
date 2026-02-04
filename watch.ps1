while ($true) {
    Clear-Host
    Write-Host "---------------------------------------------"
    Write-Host "Starting script at $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
    Write-Host "Running: poetry run python main.py"
    Write-Host "To stop, press Ctrl+C"
    Write-Host "---------------------------------------------"
    
    poetry run python main.py --max-price 300
    
    $exitCode = $lastexitcode
    
    Write-Host "---------------------------------------------"
    Write-Host "Script stopped at $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') with exit code: $exitCode"
    Write-Host "Restarting in 5 seconds..."
    Write-Host "---------------------------------------------"
    
    Start-Sleep -Seconds 5
}