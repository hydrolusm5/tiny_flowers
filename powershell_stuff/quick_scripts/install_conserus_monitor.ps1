$conserus_server = "server ip"
# Concerus folder on server
$CommonFolder = "\\$conserus_server\WorkstationInstall\ConserusMonitorCommon\"
# Concerus global on server
$GlobalConfig = "\\$conserus_server\WorkstationInstall\MonitorData\global.config"
# list of computers
$host_list = get-content "C:\temp\workstations_list.txt"

# Gather devices and check integration folder
foreach ($host_comp in $host_list) {
    # if the integration folder doesn't exist 
    $Integration =  "\\$host_comp\c$\Program Files\peerVue\pVMonitor\Integration"
    If (($Integration)) {
        
     $File = New-Item -type file "\\my_device\c$\temp\scripts\output\concerus_install_$host_comp.txt" -force # replace my_device with computer executing script

        Invoke-Command -ComputerName $host_comp -ScriptBlock {
          $Integration =  "c:\Program Files\peerVue\pVMonitor\Integration"
          $CommonFolderDestination = "c:\ConserusMonitorCommon"
          $GlobalConfigDestination = "c:\ProgramData\MonitorData\"

          # create the directories for concerus
          New-Item -path $Integration -type Directory -force
          New-Item -path $CommonFolderDestination -type Directory -force
          New-Item -path $GlobalConfigDestination -type Directory -force}
          Add-Content $File "Concerus directories created"


$CommonFolderDestinationUNC = "\\$host_comp\c$\"
$GlobalConfigDestinationUNC = "\\$host_comp\c$\ProgramData\MonitorData\"

# Copy common Folder from server to host station
Copy-Item $CommonFolder -Destination $CommonFolderDestinationUNC -recurse -force
Add-Content $File "Concerus common folder copied"

# Copy global config File
 Copy-Item $GlobalConfig -Destination $GlobalConfigDestinationUNC -recurse -force
 Add-Content $File "Concerus global folder copied"

Start-sleep -Seconds 10      

# run permissions script
$Username = "add user name with admin permission"
$Password = ''
$pass = ConvertTo-SecureString -AsPlainText $Password -Force
$Cred = New-Object System.Management.Automation.PSCredential -ArgumentList $Username,$pass
Invoke-Command -ComputerName $host_comp  -credential $cred  -scriptblock  {Invoke-Expression -Command:"cmd.exe /c 'c:\ConserusMonitorCommon\Concerus_permissions.bat'"}
Add-Content $File "permissions created"

Start-sleep -Seconds 10

#install MSI
 Invoke-Command -ComputerName $host_comp -ScriptBlock {
 msiexec /i C:\ConserusMonitorCommon\Setup.msi /l*v c:\msilog.txt  /qn}
 Add-Content $File "MSI executed"

Start-Sleep 10

Invoke-Command -ComputerName $host_comp -credential $cred -ScriptBlock {
$Source = "C:\ConserusMonitorCommon\Monitor\"
$Destination = "C:\users\*\AppData\Local\"

Copy-Item $Source -Destination $Destination -recurse -force

Get-ChildItem $Destination | ForEach-Object {Copy-Item -Path $Source -Destination $_ -recurse -Force}
    }
Add-Content $File "concerus files added to all users"


# copy start file to startup folder

Invoke-Command -ComputerName $host_comp -ScriptBlock {
$StartFile = "C:\ConserusMonitorCommon\Monitor\Start_Conerus.bat"
$StartFileLocation = "C:\ProgramData\Microsoft\Windows\Start Menu\Programs\StartUp"

Copy-Item $StartFile -Destination $StartFileLocation -recurse -force
}

# Check is folder exsist
$Integration =  "c:\Program Files\peerVue\pVMonitor\Integration"
$CommonFolderDestination = "c:\ConserusMonitorCommon"
$GlobalConfigDestination = "c:\ProgramData\MonitorData\"

    }Else{
        $Time = Get-Date
        Add-Content $File "$Time"
        Add-Content $File "Integration folder already exsist"
}
}

$IntergrationExist = Test-Path -path "\\$host_comp\c$\Program Files\peerVue\pVMonitor\Integration\"
$CommonFolderExist = Test-Path -path "\\$host_comp\c$\ConserusMonitorCommon"
$GlobalConfigExist = Test-Path -path "\\$host_comp\c$\ProgramData\MonitorData\"

Add-Content $File "Intergration folder created...$IntergrationExist"
Add-Content $File "Common folder created...$CommonFolderExist"
Add-Content $File "Global folder created...$GlobalConfigExist"