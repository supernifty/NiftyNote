# Nifty Note
Simple command line for managing a set of text based notes.

## Installation
```
pip install git+https://github.com/supernifty/NiftyNote
```

## Usage
* nn rm pattern --> remove notes matching pattern
* nn edit title --> add or edit a note with title
* nn list [pattern] --> list note titles containing pattern
* nn find pattern --> find notes containing pattern
* nn view pattern --> show notes with pattern in title

# Web-based interface

## Installation
```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
## Running
```
python3 main.py
```