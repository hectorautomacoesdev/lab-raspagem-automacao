<#
  setup-admin.ps1  -- instala as bases que EXIGEM administrador para o caminho cyandrocel.
  Rode em um PowerShell ELEVADO (Executar como administrador).
  Instala: (1) MSVC C++ Build Tools (VCTools)  (2) Tesseract + idioma PT  (3) BlueStacks 5
  Tudo com log em tools\setup-admin.log. Cada etapa e independente (erro em uma nao para as outras).
#>

$ErrorActionPreference = 'Continue'
$tools = "C:\Projetos_IA\Lab_Raspagem_e_Automacao\tools"
Start-Transcript -Path (Join-Path $tools "setup-admin.log") -Append | Out-Null

# --- checagem de admin ---
$isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltinRole]::Administrator)
if (-not $isAdmin) {
    Write-Warning "Este script PRECISA ser rodado como administrador. Abra o PowerShell com 'Executar como administrador' e rode de novo."
    Stop-Transcript | Out-Null
    return
}
Write-Host "== Rodando como administrador. Iniciando instalacoes ==" -ForegroundColor Green

# --- 1) Visual Studio C++ Build Tools (necessario para compilar cyandrocel) ---
Write-Host "`n[1/3] Instalando MSVC C++ Build Tools (pode demorar 15-30 min, ~3-6 GB)..." -ForegroundColor Cyan
$vs = Join-Path $tools "vs_BuildTools.exe"
if (Test-Path $vs) {
    $p = Start-Process -FilePath $vs -Wait -PassThru -ArgumentList @(
        "--quiet","--wait","--norestart","--nocache",
        "--add","Microsoft.VisualStudio.Workload.VCTools",
        "--includeRecommended"
    )
    Write-Host ("   vs_BuildTools exit code: {0} (0 ou 3010 = OK)" -f $p.ExitCode)
} else {
    Write-Warning "   vs_BuildTools.exe nao encontrado em $tools"
}

# --- 2) Tesseract OCR + idioma portugues ---
Write-Host "`n[2/3] Instalando Tesseract OCR..." -ForegroundColor Cyan
choco install tesseract -y --no-progress
# idioma PT (por) para o backend OCR do cyandrocel (tesseract_args usa 'por+eng')
$tessdata = "C:\Program Files\Tesseract-OCR\tessdata"
if (Test-Path $tessdata) {
    try {
        [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
        Invoke-WebRequest -Uri "https://github.com/tesseract-ocr/tessdata/raw/main/por.traineddata" -OutFile (Join-Path $tessdata "por.traineddata") -UseBasicParsing
        Write-Host "   por.traineddata instalado." -ForegroundColor Green
    } catch { Write-Warning "   Falha ao baixar por.traineddata: $_" }
} else {
    Write-Warning "   Pasta tessdata nao encontrada (Tesseract instalou em outro lugar?). Ajuste depois."
}

# --- 3) BlueStacks 5 ---
Write-Host "`n[3/3] Instalando BlueStacks 5..." -ForegroundColor Cyan
choco install bluestacks -y --no-progress

Write-Host "`n== FIM. Confira o resumo abaixo ==" -ForegroundColor Green
Write-Host "cl.exe (MSVC):  " -NoNewline; if (Get-ChildItem "C:\Program Files*\Microsoft Visual Studio\2022\BuildTools\VC\Tools\MSVC\*\bin\Hostx64\x64\cl.exe" -ErrorAction SilentlyContinue) { Write-Host "OK" -ForegroundColor Green } else { Write-Host "NAO ACHOU" -ForegroundColor Red }
Write-Host "tesseract:      " -NoNewline; if (Test-Path "C:\Program Files\Tesseract-OCR\tesseract.exe") { Write-Host "OK" -ForegroundColor Green } else { Write-Host "NAO ACHOU" -ForegroundColor Red }
Write-Host "BlueStacks:     " -NoNewline; if (Test-Path "C:\Program Files\BlueStacks_nxt\HD-Player.exe") { Write-Host "OK" -ForegroundColor Green } else { Write-Host "verifique manualmente" -ForegroundColor Yellow }

Stop-Transcript | Out-Null
