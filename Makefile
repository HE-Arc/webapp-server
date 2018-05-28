ALL = base laravel rails python

.PHONY: all
all: $(ALL)

.PHONY: $(ALL)
$(ALL):
	docker-compose -f build.yml build \
		--build-arg VCS_REF="$(shell git rev-parse HEAD)" \
		--build-arg BUILD_DATE="$(shell date -u +"%Y-%m-%dT%H:%m:%SZ")" \
		$@
