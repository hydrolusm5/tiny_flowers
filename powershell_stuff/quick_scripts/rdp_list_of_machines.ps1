$HostN = get-content 'C:\Temp\scripts\input\servers.txt'

Foreach ($HostNe in $HostN){
    echo "$HostNe"
    $Server="$HostNe"
    $User="jhmc\msavoy"
    $Password=""
    cmdkey /generic:TERMSRV/$Server /user:$User /pass:$Password
    mstsc /v:$Server
}