pip install -r requirements.txt -Ut build
cp members.py build
cd build
zip -r ../pkg.zip *
