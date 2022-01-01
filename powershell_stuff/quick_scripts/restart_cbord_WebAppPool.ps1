# Variables
$Time = Get-Date
$File = New-Item -type file "C:\temp\cbordapppool.txt" -force
$Service = "CBORDDataService.generic"

# Restart app Data Service
Stop-Service $Service -force

# Wait 1 minute for service to stop
Start-Sleep -Seconds 60 
Start-Service $Service
Start-Sleep -Seconds 20 

$ServiceState = (get-service  |where {$_.name -eq "CBORDDataService.generic"}).status

If (!($ServiceState -eq "Running")) {

Add-Content $File "$Time `n$Service is no responding to the service kill/Start commands.  Please investigate" 
 
} else {Add-Content $File "`n$Service has succesfully stopped"
    $Time = Get-Date
    Add-Content $File "$Time Now starting the Data Service"
    $Time = Get-Date
    Add-Content $File "$Time Now restarting the AppPools"

Import-Module WebAdministration
reStart-WebAppPool -Name "DefaultAppPool"
reStart-WebAppPool -Name "RoomServiceChoiceAppPool"
reStart-WebAppPool -Name "RoomServiceAdminAppPool"
$Time
Add-Content $File "$Time Cbord AppPools have been successfully restarted!" 
$Time
Add-Content $File "$Time Checking AppPool's status..." 

$AppPoolStatus = Get-childItem IIS:\apppools | format-list -property name, state | Out-String
$Time
Add-Content $File "$AppPoolStatus"
$ServiceState = (get-service  |where {$_.name -eq "CBORDDataService.generic"}).status
$Time
Add-Content $File "$Time Status of Cbord Data Service is $ServiceState"
}


$smtpServer = "smtp.hospital.org"
$msg = new-object Net.Mail.MailMessage
$smtp = new-object Net.Mail.SmtpClient($smtpServer)
$msg.From = "service_account@hsopital.org"
$msg.To.Add("service_account@hospital.org")
$msg.subject = "RoomServiceChoice restart-TEST $time"
$msg.body = (Get-Content "C:\temp\cbordapppool.txt" | out-string)
$smtp.Send($msg)