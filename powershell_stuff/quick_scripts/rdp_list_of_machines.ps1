Param(
    [Parameter(Mandatory=$True)]
    [string]$host_list, $user, [string]$password
)

Foreach ($host in $host_list){
    echo $host
    $server = $host
    cmdkey /generic:TERMSRV/$server /user:$user /pass:$password
    mstsc /v:$server
}