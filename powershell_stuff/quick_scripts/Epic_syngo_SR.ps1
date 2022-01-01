Param(
    [Parameter(Mandatory=$True)]
    [string]$server_name
)

#-----Log File creation-----#
$Logfile = "\\$server_name\f$\DiscreteDataExport\logs\Syngo_Epic_$(Get-Date -Format yyyy-MM-dd).log"

Function LogWrite
{
   Param ([string]$LogString)

   Add-content $Logfile -value "$(Get-Date -Format g): $LogString"
}

$LogPath = "\\$server_name\f$\DiscreteDataExport\logs"
If(!(Test-Path $LogPath)){
    New-Item -ItemType Directory -Force -Path $LogPath | Out-Null
}



$LogfileError = "\\$server_name\f$\DiscreteDataExport\logs\Syngo_Epic_Error_$(Get-Date -Format yyyy-MM-dd).log"

Function LogWriteError
{
   Param ([string]$LogString)

   Add-content $LogfileError -value "$(Get-Date -Format g): $LogString"
}

$LogPath = "\\$server_name\f$\DiscreteDataExport\logs"
If(!(Test-Path $LogPath)){
    New-Item -ItemType Directory -Force -Path $LogPath | Out-Null
}

LogWrite " "
LogWrite "Starting Script"
LogWrite "Loading Variables"
#----- Set Variables for Script-----#
$FileTypeX = "*.xml"
$FileTypeL = "*.log"
$SyngoDropFolder = "\\$server_name\f$\DiscreteDataExport"
$WorkFolder = "\\$server_name\f$\DiscreteDataExport\workingFolder"
$DestinationFolder = "\\$server_name\f$\DiscreteDataExport\final"
#$xml = [xml](Get-Content c:\temp\1.3.12.2.1107.5.8.9.10050568830410.20160720185838557.xml) 
$AccNum = ($xml.ContextType.Text |Where-Object {$_.Name -match "AccessionNumber"}).Value
$PtId = ($xml.ContextType.Text |Where-Object {$_.Name -match "PatientID"}).Value
$XmlRaw = Get-ChildItem $SyngoDropFolder  | Where-Object { $_.Name -like $FileTypeX }
$XmlRawArchive = "\\$server_name\f$\DiscreteDataExport\Archive"
$ErrorFolder = "\\$server_name\f$\DiscreteDataExport\ErrorQueue"
$Daysback = "-4"
$DaysbackError = "-10"
$DaysbackFinal = "-14"
$CurrentDate = Get-Date
$DatetoDelete = $CurrentDate.AddDays($Daysback)
$DatetoDeleteError = $CurrentDate.AddDays($DaysbackError)
$DatetoDeleteFinal = $CurrentDate.AddDays($DaysbackFinal)
$EmailAList = "msavoy@jhmc.org","ANCSYS@jhmc.org"


LogWrite "Checking for files to process"
$XmlCountRaw = $XmlRaw.Count
#------Move all current XML files to work directory-----#
LogWrite "Found $XmlCountRaw files that need processing..."
foreach ($kXmlRaw in $XmlRaw) {

    copy-item -Path $kXmlRaw.PSPath -Destination $XmlRawArchive -force   
    move-item -Path $kXmlRaw.PSPath -Destination $WorkFolder -force
}

$WorkFolderF = Get-ChildItem $WorkFolder | Where-Object { $_.Name -like $FileTypeX }
$WorkFolderC = $WorkFolderF.Count

LogWrite "$XmlCountRaw files moved from Syngo folder to Work Dir.  There are now $WorkFolderC files in Work Dir"

#-----Get acc# and Pt ID from each file in the work dir and rename file-----#
$x = 1
foreach($F in $WorkFolderF){
    $xml = [xml](Get-Content $F.PSPath)
    $AccNum = ($xml.ContextType.Text |Where-Object {$_.Name -match "AccessionNumber"}).Value
    $PtId = ($xml.ContextType.Text |Where-Object {$_.Name -eq "PatientID"}).Value
    $FirstName = ($xml.ContextType.personname |Where-Object {$_.Name -match "PatientsName"}).firstname
    $LastName = ($xml.ContextType.personname |Where-Object {$_.Name -match "PatientsName"}).Lastname


    #Find if first character of acc# is a letter
    $LetEx = $PtId[0]

    #Remove letter if first character of acc# is a letter

    if ($LetEx -match '^[a-zA-Z]') {
        $PtId = $PtId -replace $LetEx}


    if ((!$AccNum) -or (!$PtId)) {
        LogWrite "$F contains NO Acc Number or PtID!!"        
        LogWrite "Moving $F to the error folder"
        LogWrite " "
        Move-Item -Path $F.PSPath -Destination $ErrorFolder -Force
        LogWriteError "$F contains NO Acc Number or PtID!!"
        LogWriteError "Firstname: $FirstName"
        LogWriteError "Lastname:  $LastName"
        LogWriteError "Accname:   $AccNum"
        LogWriteError "PtID:      $PtId"
        LogWriteError ""

    }else{
        LogWrite "Found! File $F has Acc# $AccNum and PtID $PtId "
        $newName = "$PtId`_$AccNum`.xml" 
        $newPath = Join-Path -Path $DestinationFolder -ChildPath $newName        
        Move-Item -Path $F.FullName -Destination $newPath -Force
        LogWrite "$F has been renamed to $PtId`_$AccNum`_$x`.xml"
        LogWrite "$PtId`_$AccNum`_$x`.xml has been moved to $DestinationFolder"
        LogWrite " "
        ++$x
    }
}

