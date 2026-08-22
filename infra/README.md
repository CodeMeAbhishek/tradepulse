# TradePulse AWS deploy (demo)

Region: `ap-south-1` · Profile: `tradepulse`

## Live URLs

| Service | URL |
|---------|-----|
| Web UI | http://tradepulse-web-80820411.ap-south-1.elb.amazonaws.com |
| API | http://tradepulse-api-1608361585.ap-south-1.elb.amazonaws.com |
| Health | http://tradepulse-api-1608361585.ap-south-1.elb.amazonaws.com/healthz |
| OpenAPI | http://tradepulse-api-1608361585.ap-south-1.elb.amazonaws.com/docs |

Web is wired to `NEXT_PUBLIC_API_BASE_URL=…/api/v1` at image build time.

## Redeploy

```powershell
$env:AWS_PROFILE = "tradepulse"
.\infra\deploy-api.ps1
.\infra\deploy-web.ps1
```

## Tear down (stop cost)

```powershell
aws cloudformation delete-stack --profile tradepulse --region ap-south-1 --stack-name tradepulse-web
aws cloudformation delete-stack --profile tradepulse --region ap-south-1 --stack-name tradepulse-api
# optional: delete ECR repos tradepulse-api / tradepulse-web
```

## Note on Amplify

Amplify Hosting needs a one-time GitHub OAuth in the AWS console. For this hackathon
deploy we ran **Next.js standalone on ECS Fargate** instead (same ALB pattern as the API).
