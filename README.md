
# How To run

## requirement
- python Version: 3.13

1. create virtual environment for Python 3

`python3 -m venv virtualenvname`
2. activate the virtual environment
- On Linux, Unix or MacOS
`source virtualenvname/bin/activate`
- On windows
` virtualenvname\Scripts\activate`
3. run requirement.txt
`pip install -r  requirements.txt`
4. run fastapi
`uvicorn app.main:app --reload`



    