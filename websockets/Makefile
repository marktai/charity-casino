export GOPATH := $(shell pwd)
default: build

init:
	rm -f bin/server bin/main bin/pf-websockets
	@cd src/main && go get

build: init
	go build -o bin/pf-websockets src/main/main.go 

run: build
	@pkill ^pf-websockets$ || :
	bin/pf-websockets>log.txt 2>&1 &

log: run
	tail -f -n2 log.txt
