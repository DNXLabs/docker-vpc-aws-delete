export AWS_ROLE?=
export APP_NAME=vpc-delete
export AWS_DEFAULT_REGION?=us-west-2
export AWS_ACCOUNT_ID?=
export DOCKER_DEFAULT_PLATFORM=linux/amd64
PATH_ENVS=.envs
BUILD_VERSION?=latest

.env:
	@echo "make .env"
	cp $(PATH_ENVS)/.env.template $(PATH_ENVS)/.env
	echo >> $(PATH_ENVS)/.env
	touch $(PATH_ENVS)/.env.assume
	touch $(PATH_ENVS)/.env.auth
.PHONY: .env

.env.assume: .env
	@echo "creating $(PATH_ENVS)/.env.assume"
	echo > $(PATH_ENVS)/.env.assume
	docker-compose -f docker-compose.yml pull -q aws
	docker-compose -f docker-compose.yml run --rm aws assume-role.sh > $(PATH_ENVS)/.env.assume
.PHONY: .env.assume

shell-aws: .env
	docker-compose -f docker-compose.yml run --rm aws /bin/bash

shell: .env.assume
	docker-compose -f docker-compose.yml run --rm app /bin/bash

list-vpcs: .env.assume
	docker-compose -f docker-compose.yml run --rm app "python3 aws-vpc.py"

delete-vpcs: .env.assume
	@echo "🗑️  All DEFAULT VPCs will be deleted"
	@if $(MAKE) -s confirm ; then \
    	     	docker-compose -f docker-compose.yml run --rm app "python3 aws-vpc.py --delete true" ; \
	fi
.PHONY: delete-vpcs

# The CI environment variable can be set to a non-empty string,
# it'll bypass this command that will "return true", as a "yes" answer.
confirm:
	@if [[ -z "$(CI)" ]]; then \
		REPLY="" ; \
		read -p "Are you sure? [y/n] > " -r ; \
		if [[ ! $$REPLY =~ ^[Yy]$$ ]]; then \
			printf $(_ERROR) "OK" "Stopping" ; \
			exit 1 ; \
		else \
			printf $(_TITLE) "OK" "Continuing" ; \
			exit 0; \
		fi \
	fi
.PHONY: confirm
_WARN := "\033[33m[%s]\033[0m %s\n"  # Yellow text for "printf"
_TITLE := "\033[32m[%s]\033[0m %s\n" # Green text for "printf"
_ERROR := "\033[31m[%s]\033[0m %s\n" # Red text for "printf"