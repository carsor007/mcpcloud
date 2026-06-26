# MCPCloud — AWS deployment
#
# Prerequisites: AWS CLI configured, Docker running
#
# First-time setup:
#   1. make ecr-public-create     create a public ECR repo (once)
#   2. make push-public           build and push the image publicly
#   3. Update README Deploy button with your public image URI
#
# Per-customer deployment:
#   make deploy VPC_ID=... PUBLIC_SUBNETS=... PRIVATE_SUBNETS=...
#
# After a code change:
#   make push-public && make update

REGION       ?= us-east-1
STACK        ?= mcpcloud
ACCOUNT_ID   := $(shell aws sts get-caller-identity --query Account --output text 2>/dev/null)

# Private ECR (your account, for internal use / Marketplace submission)
PRIVATE_REPO := $(ACCOUNT_ID).dkr.ecr.$(REGION).amazonaws.com/mcpcloud
PRIVATE_IMG  := $(PRIVATE_REPO):latest

# Public ECR (gallery.ecr.aws — anyone can pull, no auth required)
# Replace YOUR_ALIAS with your ECR Public alias after running ecr-public-create
ECR_PUBLIC_ALIAS ?= u1x5w2j4
PUBLIC_REPO      := public.ecr.aws/$(ECR_PUBLIC_ALIAS)/mcpcloud
PUBLIC_IMG       := $(PUBLIC_REPO):latest

.PHONY: ecr-private-create ecr-public-create ecr-login push-private push-public push deploy update outputs destroy

# ── ECR setup ─────────────────────────────────────────────────────────────────

ecr-private-create:
	aws ecr create-repository \
		--repository-name mcpcloud \
		--region $(REGION) \
		--image-scanning-configuration scanOnPush=true \
	|| true
	@echo "Private ECR: $(PRIVATE_REPO)"

ecr-public-create:
	@echo "Creating public ECR repository..."
	aws ecr-public create-repository \
		--repository-name mcpcloud \
		--region us-east-1 \
	|| true
	@echo ""
	@echo "Your ECR Public alias is shown above under repositoryUri."
	@echo "It looks like: public.ecr.aws/a1b2c3d4/mcpcloud"
	@echo "Set ECR_PUBLIC_ALIAS=a1b2c3d4 in this Makefile or as an env var."

# ── Build & push ──────────────────────────────────────────────────────────────

ecr-login:
	aws ecr get-login-password --region $(REGION) | \
	docker login --username AWS --password-stdin $(ACCOUNT_ID).dkr.ecr.$(REGION).amazonaws.com

ecr-public-login:
	aws ecr-public get-login-password --region us-east-1 | \
	docker login --username AWS --password-stdin public.ecr.aws

build:
	docker build --platform linux/amd64 -t mcpcloud:latest ../../

push-private: ecr-login build
	docker tag mcpcloud:latest $(PRIVATE_IMG)
	docker push $(PRIVATE_IMG)
	@echo "Private image: $(PRIVATE_IMG)"

push-public: ecr-public-login build
	docker tag mcpcloud:latest $(PUBLIC_IMG)
	docker push $(PUBLIC_IMG)
	@echo ""
	@echo "Public image: $(PUBLIC_IMG)"
	@echo "Deploy button URL (update README):"
	@echo "https://console.aws.amazon.com/cloudformation/home#/stacks/create/review?templateURL=https://raw.githubusercontent.com/carsor007/mcpcloud/main/deploy/aws/cloudformation.yaml&stackName=mcpcloud"

push: push-public push-private

# ── CloudFormation ────────────────────────────────────────────────────────────

deploy:
	@test -n "$(VPC_ID)"          || (echo "ERROR: set VPC_ID";          exit 1)
	@test -n "$(PUBLIC_SUBNETS)"  || (echo "ERROR: set PUBLIC_SUBNETS";  exit 1)
	@test -n "$(PRIVATE_SUBNETS)" || (echo "ERROR: set PRIVATE_SUBNETS"; exit 1)
	aws cloudformation deploy \
		--template-file cloudformation.yaml \
		--stack-name $(STACK) \
		--capabilities CAPABILITY_NAMED_IAM \
		--region $(REGION) \
		--parameter-overrides \
			ContainerImage=$(PUBLIC_IMG) \
			VpcId=$(VPC_ID) \
			PublicSubnetIds=$(PUBLIC_SUBNETS) \
			PrivateSubnetIds=$(PRIVATE_SUBNETS) \
			$(if $(CERT_ARN),CertificateArn=$(CERT_ARN),) \
			$(if $(JIRA_URL),JiraUrl=$(JIRA_URL),) \
			$(if $(JIRA_EMAIL),JiraEmail=$(JIRA_EMAIL),) \
			$(if $(JIRA_API_TOKEN),JiraApiToken=$(JIRA_API_TOKEN),) \
			$(if $(SLACK_WEBHOOK_URL),SlackWebhookUrl=$(SLACK_WEBHOOK_URL),) \
			$(if $(ANTHROPIC_API_KEY),AnthropicApiKey=$(ANTHROPIC_API_KEY),)
	@$(MAKE) outputs

update: push-public
	aws ecs update-service \
		--cluster $(STACK) \
		--service $(STACK) \
		--force-new-deployment \
		--region $(REGION) \
		--query 'service.deployments[0].{status:status,desired:desiredCount,running:runningCount}' \
		--output table

outputs:
	@aws cloudformation describe-stacks \
		--stack-name $(STACK) \
		--region $(REGION) \
		--query 'Stacks[0].Outputs[*].[OutputKey,OutputValue]' \
		--output table 2>/dev/null || echo "Stack not deployed yet."

destroy:
	@echo "This will delete the stack and all resources including data."
	@read -p "Type the stack name to confirm: " confirm && [ "$$confirm" = "$(STACK)" ]
	aws cloudformation delete-stack --stack-name $(STACK) --region $(REGION)
	@echo "Deletion started. Monitor at: AWS Console → CloudFormation → $(STACK)"
