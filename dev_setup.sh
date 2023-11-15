# python dependencies
pip install -r requirements.txt
python -m spacy download en_core_web_sm

# install the local package
pip install -e .

# tesseract for OCR
sudo apt update
sudo apt install tesseract-ocr

# java for runing grobit
sudo apt install openjdk-11-jre-headless -y
java -version

# grobit backend
bash serve_grobid.sh