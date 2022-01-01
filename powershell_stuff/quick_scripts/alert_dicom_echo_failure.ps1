$my_AET = 'test_device'
$destination_AET = 'GEPACS'
$destination_IP = '10.1.8.26'
$destination_port = '4100'
$File = New-Item -type file C:\temp\Dicom_echo.txt -force 
$Time = Get-Date

& 'C:\Program Files (x86)\GDCM 3.1\bin\gdcmscu.exe' --echo --debug $destination_IP $destination_port --call $destination_AET --aetitle $my_AET
if($LASTEXITCODE -ne 0) { 
   $DcomImport = "Failed"
   
   Add-content $File "$Time PACS Listener Not Responding!!!"
   $smtpServer = "smtp.hospital.org"
   $msgCAST = new-object Net.Mail.MailMessage
   $smtp = new-object Net.Mail.SmtpClient($smtpServer)

   $msgCAST.From = "PACSERROR@hospital.org"
   $msgCAST.To.Add("email@hospital.org")
   $msgCAST.subject = "GEPACS Image import is not responding!"
   $msgCAST.body = "GEPACS Image import is not responding"
   $smtp.Send($msgCAST)
   $msgCAST.Dispose()

}else{ 
   $DcomImport = "Running"
   echo "running"
   Add-content $File "$Time PACS Listener is Responding"
}