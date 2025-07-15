.PHONY: test
test: .test

.test: $(wildcard bids2nda/**py)  $(wildcard examples/**)  $(wildcard tests/**py)
	python3 -m pytest tests/ | tee $@ # --pdb
