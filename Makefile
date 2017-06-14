ALL = base laravel rails python

.PHONY: all
all: $(ALL)

.PHONY: $(ALL)
$(ALL):
	docker-compose -f build.yml build \
		--build-arg VCS_REF=`git rev-parse HEAD` \
		--build-arg BUILD_DATE=`date -u +"%Y-%m-%dT%H:%m:%SZ"` \
		$@
