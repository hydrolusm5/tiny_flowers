$File = new-item -type file "c:\temp\url.txt" -force
$complist = Get-Content "c:\temp\complist.txt"
$icon_image_location = 'c:\temp\icon.ico'
$icon_destination_path = "folder...." #path where icon will go on destination computer
$url = 'url.....'


$ico_file_name = Split-Path $icon_image_location -Leaf
foreach($comp in $complist){
    
    Add-content $File "Computername:$comp"
    Copy-Item $icon_image_location -Destination "\\$comp\$icon_destination_path" 
    $InstallExist2 = Test-Path -path "\\$comp\$icon_destination_path\$ico_file_name" #check to see if file was copied to destination computer
    if($InstallExist2){
        Add-Content $File "Copy was successfuly"
        Invoke-command -computername $comp -ScriptBlock {
        $Shell = New-Object -ComObject ("WScript.Shell")
        $ShortCut = $Shell.CreateShortcut("c:\users\public\Desktop\Nuance Powershare.lnk") #enter link name......
        $ShortCut.TargetPath= "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe" 
        $ShortCut.Arguments = $url
        $ShortCut.WorkingDirectory = "C:\Program Files (x86)\Google\Chrome\Application";
        $ShortCut.WindowStyle = 1;
        $ShortCut.Hotkey = "CTRL+SHIFT+F";
        $ShortCut.IconLocation = $icon_destination_path +'\'+ $ico_file_name;
        $ShortCut.Description = "Nuance Powershare!";
        $ShortCut.Save()
        }
     }else{

        Add-Content $File "Copy Failed"
        
    }
    $InstallExist2 = Test-Path -path "\\$comp\c$\users\public\Desktop\Nuance Powershare.lnk"
    Add-Content $File "APP Installed:$InstallExist2"
    Add-Content $File "_________________________________________________"
    }