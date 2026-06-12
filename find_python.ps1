$locations = @(
    "C:\Users\liuyh\AppData\Local\Programs\Python",
    "C:\Python*",
    "C:\Program Files\Python*",
    "C:\Users\liuyh\Anaconda3",
    "C:\Users\liuyh\Miniconda3",
    "C:\ProgramData\Anaconda3",
    "C:\ProgramData\Miniconda3"
)

foreach ($loc in $locations) {
    $matches = Get-ChildItem $loc -Directory -ErrorAction SilentlyContinue
    foreach ($match in $matches) {
        $python = Join-Path $match.FullName "python.exe"
        if (Test-Path $python) {
            Write-Host "Found: $python"
        }
    }
}
