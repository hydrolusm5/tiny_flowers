# run this script as an admin
#PSexec must be in line C:\Scripts\Pstools\psexec.exe

Param(
    [Parameter(Mandatory=$True)]
    [string]$user_name, $password, $computer_list
)

$password_object = ConvertTo-SecureString $password -AsPlainText -Force
$cred = New-Object System.Management.Automation.PSCredential ($user_name, $password_object)
$computer_list = Get-Content "C:\temp\devices.txt"

Function change_policy{
    Param ($cred, $comp)

    Start-Process -Filepath "C:\Scripts\Pstools\psexec.exe" -Argumentlist "\\$comp -h -d winrm.cmd quickconfig -q" -Credential $cred
	Write-Host "Enabling WINRM Quickconfig" -ForegroundColor Green
	Write-Host "Waiting for 60 Seconds......." -ForegroundColor Yellow
	Start-Sleep -Seconds 60 -Verbose	
    Start-Process -Filepath "C:\Scripts\Pstools\psexec.exe" -Argumentlist "\\$comp -h -d powershell.exe enable-psremoting -force" -Credential $cred
	Write-Host "Enabling PSRemoting" -ForegroundColor Green
    Start-Process -Filepath "C:\Scripts\Pstools\psexec.exe" -Argumentlist "\\$comp -h -d powershell.exe set-executionpolicy RemoteSigned -force" -Credential $cred
	Write-Host "Enabling Execution Policy" -ForegroundColor Green	
    Test-Wsman -ComputerName $comp
    }
    

ForEach ($comp in $computer_list ) {
    change_policy $cred, $comp
}