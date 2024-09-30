#https://www.reddit.com/r/PowerShell/comments/cvu7z9/all_getdellwarrantyps1_users_should_read_this/
#
#Usage:
#Run with Single ServiceTag as a Parameter or multiple ServiceTags 
#as a Parameter in quotes separated by comma. 
#Example: .\Get-DellWarrantyInfo.ps1 "TAG1, TAG2, TAG3"
#Or
#Run with no parameters and enter a single ServiceTag or multiple
#ServiceTags seperated by comma without quotes.
#Example: Enter ServiceTag [TAG] : TAG1, TAG2, TAG3
#Run with no parameters and press enter at the prompt without entry 
#to get warranty info on the machine where script is run. 
#Use API Key and Secret as parameters 2 and 3 or edit the below
#to include your API Key and Secret.

Param(  
	[Parameter(Mandatory = $false)]  
	$ServiceTags,
	[Parameter(Mandatory = $false)]  
	$ApiKey,
	[Parameter(Mandatory = $false)]  
	$KeySecret
)

#API Key Expiration: 01/01/2021
$ORG_API_Key="YOUR_API_KEY"
$ORG_API_Secret="YOUR_KEY_SECRET"

$bios = gwmi win32_bios
$st = $bios.SerialNumber

if (!$ServiceTags) {
$ServiceTags = Read-Host -Prompt "Enter ServiceTag [$st] "
}
if (!$ServiceTags) {
$ServiceTags = $st
}
if (!$ApiKey) {
$ApiKey = $ORG_API_Key
}
if (!$ApiKey) {
$ApiKey = Read-Host -Prompt 'Enter API Key '
}
if (!$KeySecret) {
$KeySecret = $ORG_API_Secret
}
if (!$KeySecret) {
$KeySecret = Read-Host -Prompt 'Enter Key Secret '
}

[String]$servicetags = $ServiceTags -join ", "

#Write-Host "Access Token is: $token`n"

$headers = @{"Accept" = "application/json" }
$headers.Add("Authorization", "Bearer $token")

$params = @{ }
$params = @{servicetags = $servicetags; Method = "GET" }

Try {
	$Global:response = Invoke-RestMethod -Uri "https://apigtwb2c.us.dell.com/PROD/sbil/eapi/v5/asset-entitlements" -Headers $headers -Body $params -Method Get -ContentType "application/json"
}
Catch {
	$AuthURI = "https://apigtwb2c.us.dell.com/auth/oauth/v2/token"
	$OAuth = "$ApiKey`:$KeySecret"
	$Bytes = [System.Text.Encoding]::ASCII.GetBytes($OAuth)
	$EncodedOAuth = [Convert]::ToBase64String($Bytes)
	$Headers = @{ }
	$Headers.Add("authorization", "Basic $EncodedOAuth")
	$Authbody = 'grant_type=client_credentials'
	[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
	$AuthResult = Invoke-RESTMethod -Method Post -Uri $AuthURI -Body $AuthBody -Headers $Headers
	$Global:token = $AuthResult.access_token
	$Global:response = Invoke-RestMethod -Uri "https://apigtwb2c.us.dell.com/PROD/sbil/eapi/v5/asset-entitlements" -Headers $headers -Body $params -Method Get -ContentType "application/json"
}
Finally{
	foreach ($Record in $response) {
	$servicetag = $Record.servicetag
	$Json = $Record | ConvertTo-Json
	$Record = $Json | ConvertFrom-Json 
	$Device = $Record.productLineDescription
	$ShipDate = $Record.shipDate
	$EndDate = ($Record.entitlements | Select -Last 1).endDate
	$Support = ($Record.entitlements | Select -Last 1).serviceLevelDescription
	$ShipDate = $ShipDate | Get-Date -f "MM-dd-y"
	$EndDate = $EndDate | Get-Date -f "MM-dd-y"
	$today = get-date
	$type = $Record.ProductID

	if ($type -Like '*desktop') { 
		$type = 'desktop'        
	}
	elseif ($type -Like '*laptop') { 
		$type = 'laptop'
	}

	Write-Host -ForegroundColor White -BackgroundColor "DarkRed" $Computer
	Write-Host "Service Tag   : $servicetag"
	Write-Host "Model         : $Device"
	Write-Host "Type          : $type"
	Write-Host "Ship Date     : $ShipDate"
	if ($today -ge $EndDate) { Write-Host -NoNewLine "Warranty Exp. : $EndDate  "; Write-Host -ForegroundColor "Yellow" "[WARRANTY EXPIRED]" }
	else { Write-Host "Warranty Exp. : $EndDate" } 
	if (!($ClearEMS)) {
		$i = 0
		foreach ($Item in ($($WarrantyInfo.entitlements.serviceLevelDescription | select -Unique | Sort-Object -Descending))) {
			$i++
			Write-Host -NoNewLine "Service Level : $Item`n"
		}

	}
	else {
		$i = 0
		foreach ($Item in ($($WarrantyInfo.entitlements.serviceLevelDescription | select -Unique | Sort-Object -Descending))) {
			$i++
			Write-Host "Service Level : $Item`n"
		}
	}
}
}