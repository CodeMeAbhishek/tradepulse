# TradePulse Web deploy helper
# Usage (from repo root):  .\infra\deploy-web.ps1

$ErrorActionPreference = "Continue"
$Profile = if ($env:AWS_PROFILE) { $env:AWS_PROFILE } else { "tradepulse" }
$Region = "ap-south-1"
$Account = (aws sts get-caller-identity --profile $Profile --query Account --output text).Trim()
$Repo = "tradepulse-web"
$ImageTag = "latest"
$EcrUri = "$Account.dkr.ecr.$Region.amazonaws.com/$Repo"
$ApiBase = "http://tradepulse-api-1608361585.ap-south-1.elb.amazonaws.com/api/v1"

Write-Host "Account=$Account Region=$Region"

$VpcId = (aws ec2 describe-vpcs --profile $Profile --region $Region `
  --filters Name=isDefault,Values=true --query "Vpcs[0].VpcId" --output text).Trim()
$SubnetIds = (aws ec2 describe-subnets --profile $Profile --region $Region `
  --filters Name=vpc-id,Values=$VpcId Name=default-for-az,Values=true `
  --query "Subnets[].SubnetId" --output text).Trim()
$SubnetList = ($SubnetIds -split "\s+") -join ","

cmd /c "aws ecr describe-repositories --profile $Profile --region $Region --repository-names $Repo >nul 2>&1"
if ($LASTEXITCODE -ne 0) {
  aws ecr create-repository --profile $Profile --region $Region --repository-name $Repo --image-scanning-configuration scanOnPush=true | Out-Null
}

$password = aws ecr get-login-password --profile $Profile --region $Region
$password | docker login --username AWS --password-stdin "$Account.dkr.ecr.$Region.amazonaws.com"

Write-Host "Building web image with API=$ApiBase"
docker build -f apps/web/Dockerfile `
  --build-arg "NEXT_PUBLIC_API_BASE_URL=$ApiBase" `
  --build-arg "NEXT_PUBLIC_DATA_MODE=api" `
  -t "${Repo}:${ImageTag}" .
if ($LASTEXITCODE -ne 0) { throw "docker build failed" }
docker tag "${Repo}:${ImageTag}" "${EcrUri}:${ImageTag}"
docker push "${EcrUri}:${ImageTag}"
if ($LASTEXITCODE -ne 0) { throw "docker push failed" }

$ImageUri = "${EcrUri}:${ImageTag}"
aws cloudformation deploy `
  --profile $Profile `
  --region $Region `
  --stack-name tradepulse-web `
  --template-file infra/web-ecs.yaml `
  --capabilities CAPABILITY_NAMED_IAM `
  --parameter-overrides `
    "VpcId=$VpcId" `
    "PublicSubnetIds=$SubnetList" `
    "ImageUri=$ImageUri"
if ($LASTEXITCODE -ne 0) { throw "cloudformation deploy failed" }

Write-Host "Forcing ECS to pull latest image..."
aws ecs update-service --profile $Profile --region $Region `
  --cluster tradepulse-web --service tradepulse-web --force-new-deployment | Out-Null
aws ecs wait services-stable --profile $Profile --region $Region `
  --cluster tradepulse-web --services tradepulse-web

$WebUrl = (aws cloudformation describe-stacks --profile $Profile --region $Region `
  --stack-name tradepulse-web --query "Stacks[0].Outputs[?OutputKey=='WebUrl'].OutputValue" --output text).Trim()
Write-Host ""
Write-Host "WEB URL: $WebUrl"
Write-Host "API URL: http://tradepulse-api-1608361585.ap-south-1.elb.amazonaws.com"
