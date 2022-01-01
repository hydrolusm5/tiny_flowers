$File = New-Item -type file "C:\temp\scripts\output\Powerscribe_Reboot.txt" -force 
$Time = (get-date) 
Add-content $File "Powerscribe 360 monthly reboot has started"

$Time = (get-date)
$smtpServer = "smtpserver.hospital.org"
$msg = new-object Net.Mail.MailMessage
$smtp = new-object Net.Mail.SmtpClient($smtpServer)
$msg.From = "email@hospital.org"
$msg.To.Add("ITSupport@hospital.org")
$msg.subject = "**Attention Initiating PS360 reboot $time***"
$msg.body = (Get-Content "C:\temp\scripts\output\Powerscribe_Reboot.txt" | out-string)
$smtp.Send($msg)

$File = New-Item -type file "C:\temp\scripts\output\Powerscribe_Reboot.txt" -force #wipe out old file



#Stop Sevices on Montage Server
Add-Content $File "$Time Halting Services on Montage Server (PS360-montage)"
$PS360Server = "PS360-montage"
Invoke-Command -ComputerName $PS360Server -ScriptBlock {Stop-Service "Montage Searchd" , "MontageCeleryD" -Force}
$Time = (get-date) 
Add-Content $File "$Time Service Stopped: Montage Searchd and Montage Celeryd"
Invoke-Command -ComputerName $PS360Server -ScriptBlock {Stop-Service "RabbitMQ" , "MontageCeleryBeat" -Force}
$Time = (get-date) 
Add-Content $File "$Time Service Stopped: RabbitMQ and Montage Celerybeat"
Invoke-Command -ComputerName $PS360Server -ScriptBlock {Stop-Service "MontageApache" -Force}
$Time = (get-date) 
Add-Content $File "$Time Service Stopped: Apache"

#Stop Sevices on HL7 Server
$PS360Server = "PS-360-gateway"
$Time = (get-date) 
Add-Content $File "$Time Halting Services on Montage Server (PS360-gateway)"
Invoke-Command -ComputerName $PS360Server -ScriptBlock {Stop-Service 'MSSQL$SQLEXPRESS' , "Px2008" -Force}
$Time = (get-date) 
Add-Content $File "$Time Service Stopped: SQL Server and Px2008"


#Stop Sevices on SUS Server
$PS360Server = "PS-360-sus"
$Time = (get-date) 
Add-Content $File "$Time Halting Services on Montage Server (PS360-SUS)"
Invoke-Command -ComputerName $PS360Server -ScriptBlock {Stop-Service "SPARKService" , "HostManagerService" -Force}
$Time = (get-date) 
Add-Content $File "$Time Service Stopped: Spark and Host Manager"
Invoke-Command -ComputerName $PS360Server -ScriptBlock {Stop-Service "SPARKNodeService" , "SUSService" -Force}
$Time = (get-date) 
Add-Content $File "$Time Service Stopped: Spark Node and SUS Service"


#Stop Sevices on APP/DB Server
$PS360Server = "PS-360-prd"
$Time = (get-date) 
Add-Content $File "Halting Services on Montage Server (PS360-prd)"
Invoke-Command -ComputerName $PS360Server -ScriptBlock {Stop-Service "agw" , "RadBridge" -Force}
$Time = (get-date) 
Add-Content $File "$Time Service Stopped: Gateway and Rad Bridge"
Invoke-Command -ComputerName $PS360Server -ScriptBlock {Stop-Service "W3SVC" , "SQLSERVERAGENT" -Force}
$Time = (get-date) 
Add-Content $File "$Time Service Stopped: WWW and SQL Management"
Invoke-Command -ComputerName $PS360Server -ScriptBlock {Stop-Service "MSSQLSERVER" -Force}
$Time = (get-date) 
Add-Content $File "$Time Service Stopped: SQL Server"


Add-Content $File ".........................................."
#Server reboot
$Time = (get-date) 
Add-Content $File "$Time Starting server reboot steps"


$PS360Server = "PS-360-prd"
$Time = (get-date) 
Add-Content $File "$Time Rebooting PS360-prd"
Restart-Computer $PS360Server -force

$s1=0
do{


if (!(Test-Connection -ComputerName $PS360Server -count 1)) {$s1++}


}while ($s1 -eq 0)

do {

    if (!(Test-Connection $PS360Server -count 1)){
        $UpTime = "down" }
        else{ $UpTime = "up"}
        $Time = (get-date) 
        Add-Content $File "$Time Waiting for $PS360Server to come up..."

    }while ($UpTime -eq "down" )

$Time = (get-date) 
Add-Content $File "$Time $PS360Server is up!

"

$PS360Server = "PS-360-gateway"
$Time = (get-date) 
Add-Content $File "$Time Rebooting PS360-gateway"
Restart-Computer $PS360Server -force

$s1=0
do{


if (!(Test-Connection -ComputerName $PS360Server -count 1)) {$s1++}


}while ($s1 -eq 0)

do {

    if (!(Test-Connection $PS360Server -count 1)){
        $UpTime = "down" }
        else{ $UpTime = "up"}
        $Time = (get-date) 
        Add-Content $File "$Time Waiting for $PS360Server to come up..."

    }while ($UpTime -eq "down" )

$Time = (get-date) 
Add-Content $File "$Time $PS360Server is up!

"

$PS360Server = "PS-360-SUS"
$Time = (get-date) 
Add-Content $File "$Time Rebooting PS360-SUS"
Restart-Computer $PS360Server -force

$s1=0
do{


if (!(Test-Connection -ComputerName $PS360Server -count 1)) {$s1++}


}while ($s1 -eq 0)

do {

    if (!(Test-Connection $PS360Server -count 1)){
        $UpTime = "down" }
        else{ $UpTime = "up"}
        $Time = (get-date) 
        Add-Content $File "$Time Waiting for $PS360Server to come up..."

    }while ($UpTime -eq "down" )

$Time = (get-date) 
Add-Content $File "$Time $PS360Server is up!

"

$PS360Server = "PS-360-Montage"
$Time = (get-date) 
Add-Content $File "$Time Rebooting PS360-Montage"
Restart-Computer $PS360Server -force

 #-----keep pinging until the server goes down-----#
$s1=0
do{


if (!(Test-Connection -ComputerName $PS360Server -count 1)) {$s1++}


}while ($s1 -eq 0)

#-----Keep ping the server until it comes up-----#
do {
   
    if (!(Test-Connection $PS360Server -count 1)){
        $UpTime = "down" }
        else{ $UpTime = "up"}
        $Time = (get-date) 
        Add-Content $File "$Time Waiting for $PS360Server to come up..."

    }while ($UpTime -eq "down" )

$Time = (get-date) 
Add-Content $File "$Time $PS360Server is up!

"
#Wait for services to fully start
Start-sleep -seconds 300

#Checking Services
$Time = (get-date) 
Add-Content $File "....................................

"
$Time = (get-date) 
Add-Content $File "$Time Checking Powescribes services"

$PS36001service=Get-Service -computer ps-360-prd
$PS36001Service1=($PS36001service| where name -eq "agw").status
$PS36001Service2=($PS36001service| where name -eq "MsDtsServer110").status
$PS36001Service3=($PS36001service| where name -eq "MSMQ").status
$PS36001Service4=($PS36001service| where name -eq "MSMQTriggers").status
$PS36001Service5=($PS36001service| where name -eq "MSSQLSERVER").status
$PS36001Service6=($PS36001service| where name -eq "RadBridge").status
$PS36001Service7=($PS36001service| where name -eq "RpcEptMapper").status
$PS36001Service8=($PS36001service| where name -eq "RpcEptMapper").status
$PS36001Service9=($PS36001service| where name -eq "RpcEptMapper").status
$PS36001Service10=($PS36001service| where name -eq "SQLSERVERAGENT").status
$PS36001Service11=($PS36001service| where name -eq "SQLWriter").status
$PS36001Service12=($PS36001service| where name -eq "IISADMIN").status
$PS36001Service13=($PS36001service| where name -eq "W3SVC").status

$PS36004service=Get-Service -computer ps-360-SUS
$PS36004Service1=($PS36004service| where name -eq 'MSSQL$SQLEXPRESS').status
$PS36004Service2=($PS36004service| where name -eq "W3SVC").status
$PS36004Service3=($PS36004service| where name -eq "SPARKService").status
$PS36004Service4=($PS36004service| where name -eq "HostManagerService").status
$PS36004Service5=($PS36004service| where name -eq "SPARKNodeService").status
$PS36004Service6=($PS36004service| where name -eq "SUSService").status

$PS36003service=Get-Service -computer ps-360-gateway
$PS36003Service5=($PS36003service| where name -eq "Px2008").status


Add-Content $File "SQL Server servcie on PS30-prd = $PS36001Service5"
Add-Content $File "SQL Agent on PS360-prd = $PS36001Service10"
Add-Content $File "WWW Service on on PS360-prd = $PS36001Service13"
Add-Content $File "Rad Bridge Service on PS360-prd = $PS36001Service6"


Add-Content $File "SQL Server Service on PS360-SUS = $PS36004Service1"
Add-Content $File "SPark Host Manager on PS360-SUS = $PS36004Service4"
Add-Content $File "Spark Node Service on PS360-SUS = $PS36004Service5"
Add-Content $File "Speech Utility Service on PS360-SUS = $PS36004Service6"
Add-Content $File "Spark Service on PS360-SUS = $PS36004Service3"

Add-Content $File "PX2008 Service on PS360-gateway = $PS36003Service5"

$OSPS360 = Get-WMIObject -Namespace "root\CIMV2" -Class Win32_OperatingSystem -comp ps360-prd
$PS36002UptimePrd= ($OSPS360.ConvertToDateTime($OSPS360.lastbootuptime))

$OSPS360 = Get-WMIObject -Namespace "root\CIMV2" -Class Win32_OperatingSystem -comp ps360-montage
$PS36002UptimeMontage= ($OSPS360.ConvertToDateTime($OSPS360.lastbootuptime))

$OSPS360 = Get-WMIObject -Namespace "root\CIMV2" -Class Win32_OperatingSystem -comp ps360-gateway
$PS36002UptimeGateway= ($OSPS360.ConvertToDateTime($OSPS360.lastbootuptime))

$OSPS360 = Get-WMIObject -Namespace "root\CIMV2" -Class Win32_OperatingSystem -comp ps360-SUS
$PS36002UptimeSus= ($OSPS360.ConvertToDateTime($OSPS360.lastbootuptime))


Add-content $File ">>>>>>>>>>>>>>>>>>>>>>>>>>>>
>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"

Add-content $File "Server PS360-prd was last rebooted on $PS36002UptimePrd"
Add-content $File "Server PS360-montage was last rebooted on $PS36002UptimeMontage"
Add-content $File "Server PS360-gateway was last rebooted on $PS36002UptimeGateway"
Add-content $File "Server PS360-SUS was last rebooted on $PS36002UptimeSus"

$Time = (get-date)
$msg = new-object Net.Mail.MailMessage
$msg.subject = "Powerscribe 360 Reboot log-Compelete $time"
$msg.body = (Get-Content "C:\temp\scripts\output\Powerscribe_Reboot.txt" | out-string)
$smtp.Send($msg)