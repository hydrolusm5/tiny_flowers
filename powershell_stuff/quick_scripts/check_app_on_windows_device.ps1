Param(
    [Parameter(Mandatory=$True)]
    [string]$computerlist, $app
)

$computers =  get-content -path $computerlist
$File = New-Item -type file "C:\temp\.txt" -force
$app = "no"
$app_name = "*"+$app+"*"

foreach ($comp in $computers){
     $compup = Test-Connection -ComputerName $comp -count 1

     if (!($comp)){
           Add-Content $File "$comp"
           Add-Content $File "Computer is down!!!!!!"     
           }else{
                $app_exist = Get-WmiObject -Class Win32_Product -ComputerName $comp | Where-Object -FilterScript {$_.Name -like $app_name} 
                Add-Content $File "$comp"
                Add-Content $File "Computer is up"
                if (!($app_exist)){
                    Add-Content $File "file does not exist"
                     }else{Add-Content $File "$app_exist"}
                     }
Add-Content $File "_______"
          }

