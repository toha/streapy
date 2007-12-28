
all:
	@echo "This makefile is only for cleaning stuff up. ('make clean')"
	@echo "You can also build the tarball dist with it ('make sdist')"

sdist: clean
	mv -f webapps/__init__.py NON-DIST/irmen__init__.py
	cp NON-DIST/dist__init__.py webapps/__init__.py
	python setup.py sdist
	@echo "Look in the dist/ directory"
	mv -f NON-DIST/irmen__init__.py webapps/__init__.py

clean:
	@echo "Removing stray logfiles, .pyo/.pyc files..."
	find . -name \*.pyo | xargs rm
	find . -name \*.pyc | xargs rm
	find . -name \*.swp | xargs rm
	find . -name \*~ | xargs rm
	find . -name \*_log | xargs rm
	find . -name \*.log | xargs rm
	find . -name \*.log.? | xargs rm
	find . -name \*.log.?? | xargs rm
	@echo "Removing non-CVS files..."
	rm -fv MANIFEST 
	rm -rf build
	rm -rf logs/server.pid
	find . -name  .#\* | xargs rm
	@echo "clean!"


