$Logfile = "C:\Temp\cbord_Install__$(Get-Date -Format yyyy-MM-dd).log"

Function LogWrite
{
   Param ([string]$LogString)

   Add-content $Logfile -value "$(Get-Date -Format g): $LogString"
}

#variables
$LICENSEE = "enter key"
$LICENSEKEY = "enter key"
$SERVERNAME = "enter database server name"
$DBNAME = "enter database name"
$ScriptDir = "enter script dir"
$odbcdriver = {C:\Temp\fms\setup.exe /S /v/qn } #change to dir of setup file
$Destination = "\\$hostN\c$\temp"
$ProcList = @("fms")
$UninstallRegKey = "HKLM:\SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\*"
$CBRDUninstallKey = "MsiExec.exe /X{83DFE6FF-0960-4F19-BD89-F74E7A72C3E1}"  
$CBRInstall = get-childitem "\\server\fms" # enter server where binaries are stored
$CBRInstall.pspath
$Destination = "C:\temp\fms"

#-----Creates the Directory if it doesn't exist-----#
$TempPath = "C:\temp\fms"
If(!(Test-Path $TempPath)){ 
    LogWrite "Creating FMS directory"       
    New-Item -ItemType Directory -Force -Path $TempPath | Out-Null
}

$CbwPath = "C:\cbordwin"
If(!(Test-Path $CbwPath)){   
    LogWrite "Creating Cbordwin folder"      
    New-Item -ItemType Directory -Force -Path $CbwPath | Out-Null
}

#-----Copy install files-----#
foreach($Xfile in $CBRInstall.pspath){                      
    LogWrite "Copying install files"
    Copy-Item $Xfile -Destination $Destination -force
}

#-----Confirm install files exisit-----#

$InstallExist1 = Test-Path -path "c:\temp\fms\FMS_MSS.msi"
$InstallExist2 = Test-Path -path "c:\temp\fms\setup.exe"
      
if($InstallExist1){
    if($InstallExist2){
        LogWrite "FMS Main installation and setup file found!"
    }else{
         LogWrite "Warning-FMS setup file NOT found...exiting"
         Break 
    }
}else{
     LogWrite "Warning-FMS main installation file NOT found...exiting"
     Break
}
     

#-----Stops Cbord Processes if they are running-----#
Foreach ($kProcess in $ProcList) {  
    LogWrite "Stopping Process: $kProcess"
    $ProcID = Get-Process $kProcess | Select -ExpandProperty ID -ErrorAction SilentlyContinue
    Stop-Process -Id $ProcID -Force
    Start-Sleep -Seconds 5
}

#-----Uninstall old Cbord installs-----# 
If (Get-ItemProperty $UninstallRegKey | Where {$_.UninstallString -like $CBRDUninstallKey}){
    LogWrite "Uninstalling old version of Cbord"
    Start-Process "Msiexec.exe" -ArgumentList "/x {83DFE6FF-0960-4F19-BD89-F74E7A72C3E1} /l*v ""C:\temp\old_cbord_uninstall_$(Get-Date -Format yyyy-MM-dd).log"" /qn /norestart" -Wait
}


#----- Installs New Version of Cbord-----#
LogWrite "Installation of New Cbord Application Start"

#-----installl ODBC drivers-----#
Start-Process "C:\Temp\fms\setup.exe" -ArgumentList "/S /v/qn" 


Start-Sleep -seconds 60

#-----Install ODBC config settings and FMS app-----#
Start-Process "Msiexec.exe" -ArgumentList "/i ""C:\Temp\FMS\FMS_MSS.msi"" LICENSEE=$LICENSEE LICENSEKEY=$LICENSEKEY  SERVERNAME=$SERVERNAME DBNAME=$DBNAME /l*v ""C:\Temp\FMS_Install_$(Get-Date -Format yyyy-MM-dd).log"" /qn /norestart" -Wait 


#----- Grant Modify Rights to Domain Users to Cbordwin Folder-----#
LogWrite "Granting Modify Rights to Domain Users to Cbordwin Folder"
$path = "C:\cbordwin" 
$user = "users" 
$Rights = "Modify, Read, ReadAndExecute, ListDirectory" 
$InheritSettings = "Containerinherit, ObjectInherit" 
$PropogationSettings = "None" 
$RuleType = "Allow" 

$acl = Get-Acl $path
$perm = $user, $Rights, $InheritSettings, $PropogationSettings, $RuleType
$rule = New-Object -TypeName System.Security.AccessControl.FileSystemAccessRule -ArgumentList $perm
$acl.SetAccessRule($rule)
$acl | Set-Acl -Path $path

#-----Confirm Cbord Installation-----#
$Installed = Get-WmiObject -Class Win32_Product -ComputerName $env:COMPUTERNAME | Where-Object -FilterScript {$_.Name -like "Cbord*"}
if(!($Installed)){
    LogWrite "Warning-Cbord not listed as a installed product on this system"
    }else{
        LogWrite "Cbord installed successfully!"
}

#-----Remove install files-----#
LogWrite "Removing installation files"
$FMSFolder = "c:\temp\fms"
Remove-Item $FMSFolder -recurse -Force

$FMSFolder = "c:\temp\fms"
$DeleteCbrd = Test-Path $FMSFolder


if (!($DeleteCbrd)){
    LogWrite "Cbord installation files removed"
}