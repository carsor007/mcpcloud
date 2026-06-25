# a2a-mcp AWS deployment
#
# Prerequisites: AWS CLI configured, Docker running
#
# Usage:
#   make ecr-create           create ECR repo (first time only)
#   make push                 build image and push to ECR
#   make deploy               deploy CloudFormation stack
#   make update               redeploy after code changes (push + force ECS update)
#   make outputs              print stack outputs (URLs)
#   make destroy              delete the stack

REGION     ?= us-east-1
STACK      ?= a2a-mcp
ACCOUNT_ID := $(shell aws sts get-caller-identity --query Account --output text 2>/dev/null)
ECR_REPO   := $(ACCOUNT_ID).dkr.ecr.$(REGION).amazonaws.com/a2a-mcp
IMAGE      := $(ECR_REPO):latest

# Required for deploy — set via environment or make args
# VPC_ID          ?= vpc-xxxxxxxxxxxxxxxxx
# PUBLIC_SUBNETS  ?= subnet-aaa,subnet-bbb
# PRIVATE_SUBNETS ?= subnet-ccc,subnet-ddd

.PHONY: ecr-create ecr-login push deploy update outputs destroy

ecr-create:
	aws ecr create-repository \
		--repository-name a2a-mcp \
		--region $(REGION) \
		--image-scanning-configuration scanOnPush=true \
	|| true
	@echo "ECR repo: $(ECR_REPO)"

ecr-login:
	aws ecr get-login-password --region $(REGION) | \
	docker login --username AWS --password-stdin $(ACCOUNT_ID).dkr.ecr.$(REGION).amazonaws.com

push: ecr-login
	docker build --platform linux/amd64 -t a2a-mcp:latest ../../
	docker tag a2a-mcp:latest $(IMAGE)
	docker push $(IMAGE)
	@echo ""
	@echo "Pushed: $(IMAGE)"

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
			ContainerImage=$(IMAGE) \
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

update: push
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
