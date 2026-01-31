$BaseUrl = "http://127.0.0.1:8000"
$Prefix = "/api/v1"

function Req($method, $path, $body = $null, $token = $null) {
    $headers = @{}
    if ($token) { $headers["Authorization"] = "Bearer $token" }
    if ($body) {
        $json = $body | ConvertTo-Json -Depth 10
        $bytes = [System.Text.Encoding]::UTF8.GetBytes($json)
        return Invoke-RestMethod -Method $method -Uri ($BaseUrl + $Prefix + $path) `
            -Headers $headers -ContentType "application/json; charset=utf-8" -Body $bytes
    } else {
        return Invoke-RestMethod -Method $method -Uri ($BaseUrl + $Prefix + $path) -Headers $headers
    }
}

function TryReq($label, $method, $path, $body = $null, $token = $null) {
    Write-Host $label
    try {
        $res = Req $method $path $body $token
        $res | ConvertTo-Json -Depth 5
        return $res
    } catch {
        if ($_.ErrorDetails -and $_.ErrorDetails.Message) {
            Write-Host $_.ErrorDetails.Message
        } else {
            Write-Host $_.Exception.Message
        }
        return $null
    }
}

$reg = TryReq "1) Register" "POST" "/auth/register" @{ email="test@example.com"; password="pass1234" }

$login = TryReq "2) Login" "POST" "/auth/login" @{ email="test@example.com"; password="pass1234" }
$token = $login.access_token

TryReq "3) /me" "GET" "/me" $null $token

TryReq "4) upsert profile" "PUT" "/me/profile" @{ name="Test User"; birth_date="1997-10-04"; gender="male"; height=175.0; weight=70.5 } $token

$family = TryReq "5) add family" "POST" "/me/family" @{ relationship="child"; name="Test Family"; birth_date="2010-05-01"; gender="male" } $token
$familyId = $family.id

TryReq "6) list family" "GET" "/me/family" $null $token

TryReq "7) hospitals list" "GET" "/hospitals?page=1&size=5"

Write-Host "done"