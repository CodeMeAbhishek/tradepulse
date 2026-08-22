# TradePulse API deploy helper (Windows PowerShell)
# Usage (from repo root):  .\infra\deploy-api.ps1

$ErrorActionPreference = "Continue"
$Profile = if ($env:AWS_PROFILE) { $env:AWS_PROFILE } else { "tradepulse" }
$Region = "ap-south-1"
$Account = (aws sts get-caller-identity --profile $Profile --query Account --output text).Trim()
if (-not $Account) { throw "Could not resolve AWS account" }
$Repo = "tradepulse-api"
$ImageTag = "latest"
$EcrUri = "$Account.dkr.ecr.$Region.amazonaws.com/$Repo"

Write-Host "Account=$Account Region=$Region Profile=$Profile"

$VpcId = (aws ec2 describe-vpcs --profile $Profile --region $Region `
  --filters Name=isDefault,Values=true --query "Vpcs[0].VpcId" --output text).Trim()
if (-not $VpcId -or $VpcId -eq "None") { throw "No default VPC found in $Region" }

$SubnetIds = (aws ec2 describe-subnets --profile $Profile --region $Region `
  --filters Name=vpc-id,Values=$VpcId Name=default-for-az,Values=true `
  --query "Subnets[].SubnetId" --output text).Trim()
$SubnetList = ($SubnetIds -split "\s+") -join ","
if (-not $SubnetList) { throw "No default subnets in VPC $VpcId" }
Write-Host "VPC=$VpcId Subnets=$SubnetList"

Write-Host "Ensuring ECR repository..."
cmd /c "aws ecr describe-repositories --profile $Profile --region $Region --repository-names $Repo >nul 2>&1"
if ($LASTEXITCODE -ne 0) {
  aws ecr create-repository --profile $Profile --region $Region --repository-name $Repo --image-scanning-configuration scanOnPush=true
  if ($LASTEXITCODE -ne 0) { throw "Failed to create ECR repo" }
}

$password = aws ecr get-login-password --profile $Profile --region $Region
$password | docker login --username AWS --password-stdin "$Account.dkr.ecr.$Region.amazonaws.com"
if ($LASTEXITCODE -ne 0) { throw "docker login to ECR failed" }

Write-Host "Building image..."
docker build -f apps/api/Dockerfile -t "${Repo}:${ImageTag}" .
if ($LASTEXITCODE -ne 0) { throw "docker build failed" }
docker tag "${Repo}:${ImageTag}" "${EcrUri}:${ImageTag}"
docker push "${EcrUri}:${ImageTag}"
if ($LASTEXITCODE -ne 0) { throw "docker push failed" }

$ImageUri = "${EcrUri}:${ImageTag}"
Write-Host "Deploying CloudFormation stack with $ImageUri"
aws cloudformation deploy `
  --profile $Profile `
  --region $Region `
  --stack-name tradepulse-api `
  --template-file infra/api-ecs.yaml `
  --capabilities CAPABILITY_NAMED_IAM `
  --parameter-overrides `
    "VpcId=$VpcId" `
    "PublicSubnetIds=$SubnetList" `
    "ImageUri=$ImageUri" `
    "CorsOrigins=http://tradepulse-web-80820411.ap-south-1.elb.amazonaws.com,http://localhost:3000,http://127.0.0.1:3000"
if ($LASTEXITCODE -ne 0) { throw "cloudformation deploy failed" }

Write-Host "Forcing ECS to pull latest image..."
aws ecs update-service --profile $Profile --region $Region `
  --cluster tradepulse-api --service tradepulse-api --force-new-deployment | Out-Null
aws ecs wait services-stable --profile $Profile --region $Region `
  --cluster tradepulse-api --services tradepulse-api

$ApiUrl = (aws cloudformation describe-stacks --profile $Profile --region $Region `
  --stack-name tradepulse-api --query "Stacks[0].Outputs[?OutputKey=='ApiUrl'].OutputValue" --output text).Trim()
Write-Host ""
Write-Host "API URL: $ApiUrl"
Write-Host "Health:  $ApiUrl/healthz"
Write-Host "OpenAPI: $ApiUrl/docs"
