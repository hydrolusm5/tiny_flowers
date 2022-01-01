Param(
    [Parameter(Mandatory=$True)]
    [string]$ip_list
)
$ipaddress = Get-Content $ip_list

foreach($ip in $ipaddress){
$hostname = ([System.Net.Dns]::GetHostByAddress($ip)).Hostname
if($hostname) {
  $ip +": "+ $hostname >> "C:\temp\machinenames.txt"
  $hostname = "unreachable"
}
else {
   $_ +": Cannot resolve hostname" >> "C:\temp\machinenames1.txt" 
}}