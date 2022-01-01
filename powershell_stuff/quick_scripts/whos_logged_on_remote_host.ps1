 [System.Reflection.Assembly]::LoadWithPartialName('Microsoft.VisualBasic') | Out-Null
$HostName = [Microsoft.VisualBasic.Interaction]::InputBox("Enter the name of the workstation.")

$explorerprocesses = @(Get-WmiObject -comp $HostName -Query "Select * FROM Win32_Process WHERE Name='explorer.exe'" -ErrorAction SilentlyContinue)
If ($explorerprocesses.Count -eq 0)
{
    "No explorer process found / No users interactively logged on"
}
Else
{
    ForEach ($i in $explorerprocesses)
    {
        $Username = $i.GetOwner().User
        $Domain = $i.GetOwner().Domain
        Write-Host "$Domain\$Username logged on since: $($i.ConvertToDateTime($i.CreationDate))"
    }
}

