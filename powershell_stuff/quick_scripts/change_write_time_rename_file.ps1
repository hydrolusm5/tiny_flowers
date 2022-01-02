$FilePath = get-childitem "C:\temp"
$Daysback = "-1"

$x=1
foreach($File in $FilePath){
    $File.LastWriteTime = (Get-Date).AddDays($Daysback)
    Rename-item $File.PSPath -NewName "$x.png"
    ++$x
    }

