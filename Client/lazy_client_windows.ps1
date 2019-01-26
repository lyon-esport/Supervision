# python 3.7.2 for windows
$python_64bit = "https://www.python.org/ftp/python/3.7.2/python-3.7.2.post1-embed-amd64.zip"
$python_32bit = "https://www.python.org/ftp/python/3.7.2/python-3.7.2.post1-embed-win32.zip"

# pip latest version
$pip = "https://bootstrap.pypa.io/get-pip.py"

clear-host
Write-Host "--------------------------------------------------------" -ForegroundColor Cyan
Write-Host "-------------------                 --------------------" -ForegroundColor Cyan
Write-Host "------------------   INSTALLATION    -------------------" -ForegroundColor Cyan
Write-Host "-------------------                 --------------------" -ForegroundColor Cyan
Write-Host "--------------------------------------------------------" -ForegroundColor Cyan

# verify if powershell version is uspported (unzip command)
if($PSVersionTable.PSVersion.Major -lt 5)
{
    Write-Host "Your PowerShell Version is not supported" -ForegroundColor Red
    Read-Host -Prompt "Press Enter to exit..."
    exit
}

$notwget = New-Object System.Net.WebClient

# verify if OS in 64 or 32 bit
if([System.Environment]::Is64BitOperatingSystem)
{
    Write-Host "64-bit OS detected" -ForegroundColor Cyan
    $python_url = $python_64bit
}
elseif([System.Environment]::Is32BitOperatingSystem)
{
    Write-Host "32-bit OS detected" -ForegroundColor Cyan
    $python_url = $python_32bit
}
else
{
    Write-Host "Your CPU doesn't match requirement (32-bit or 64-bit)" -ForegroundColor Red
    Read-Host -Prompt "Press Enter to exit..."
    exit
}
# download python
if(-not (Test-Path ".\python.zip") -and -not (Test-Path ".\python\python.exe")) 
{
    try
    { 
        Write-Host "Downloading python ..."
        (new-object System.Net.WebClient).DownloadFile($python_url, ".\python.zip")
        Write-Host "Downloading successfull !" -ForegroundColor Green
    }
    catch 
    {
        Write-Host $_.Exception
        Read-Host -Prompt "Press Enter to exit..."
        exit
    }
}
else
{
    Write-Host "Python already downloaded !" -ForegroundColor Green
}

# unzip python
if(-not (Test-Path ".\python\python.exe")) 
{
    try 
    {   
        if(Test-Path ".\python\")
        {
            Write-Host "Removing old installation ..."
            Remove-Item .\python\ -Force -Recurse
            Write-Host "Deleting successfull !" -ForegroundColor Green
        }
        Write-Host "Unzip python ..."
        Expand-Archive -Path .\python.zip -DestinationPath .\python
        Write-Host "Unzip successfull !" -ForegroundColor Green
        Write-Host "Deleting python.zip ..."
        Remove-Item .\python.zip -Force
        Write-Host "Deleting successfull !" -ForegroundColor Green
        Write-Host "Deleting python\python37._pth ..."
        Remove-Item .\python\python37._pth -Force
        Write-Host "Deleting successfull !" -ForegroundColor Green
    }
    catch 
    {
        Write-Host $_.Exception
        Read-Host -Prompt "Press Enter to exit..."
        exit
    }
}
else
{
    Write-Host "Python already installed !" -ForegroundColor Green
}

# download pip
if(-not (Test-Path ".\pip.py") -and -not (Test-Path ".\python\Scripts\pip3.exe")) 
{
    try
    { 
        Write-Host "Downloading pip ..."
        (new-object System.Net.WebClient).DownloadFile($pip, ".\pip.py")
        Write-Host "Downloading successfull !" -ForegroundColor Green

    }
    catch 
    {
        Write-Host $_.Exception
        Read-Host -Prompt "Press Enter to exit..."
        exit
    }
}
else
{
    Write-Host "Pip already downloaded !" -ForegroundColor Green
}

# set Path environnement with python embedded and pip
$env:Path = "$pwd\python\;$pwd\python\Scripts\" 

# install pip
if(-not (Test-Path ".\python\Scripts\pip3.exe"))
{
    try
    {
        python pip.py
        Write-Host "Deleting pip.py ..."
        Remove-Item .\pip.py -Force
        Write-Host "Deleting successfull !" -ForegroundColor Green
    }
    catch
    {
        Write-Host $_.Exception
        Read-Host -Prompt "Press Enter to exit..."
        exit
    }
}

# set PYTHONPATH environnement with pip
$env:PYTHONPATH = "$pwd\python\Scripts\"

# pip install requirements.txt
pip install -r requirements.txt

clear-host
Write-Host "--------------------------------------------------------" -ForegroundColor Cyan
Write-Host "-------------------                 --------------------" -ForegroundColor Cyan
Write-Host "------------------   CONFIGURATION   -------------------" -ForegroundColor Cyan
Write-Host "-------------------                 --------------------" -ForegroundColor Cyan
Write-Host "--------------------------------------------------------" -ForegroundColor Cyan

# get client name
$probe_name=Read-Host "Probe client -> Name ?"

# get client address
$probe_address=Read-Host "Probe client -> Address ?[IPV4]"

# get client port
$probe_port=Read-Host "Probe client -> Port ?[1-65535]"

# get server address
$server_address=Read-Host "Probe server -> Address ?[IPV4]"

# get server port
$servert_port=Read-Host "Probe client -> Port ?[1-65535]"


[Environment]::SetEnvironmentVariable("PROBE_NAME", $probe_name)
[Environment]::SetEnvironmentVariable("PROBE_IP", $probe_address)
[Environment]::SetEnvironmentVariable("PROBE_PORT", $probe_port)
[Environment]::SetEnvironmentVariable("SERVER_IP", $server_address)
[Environment]::SetEnvironmentVariable("SERVER_PORT", $servert_port)

python client.py

Read-Host -Prompt "Press Enter to exit..."