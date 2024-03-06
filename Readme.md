# Instructions to host the App

## venv (open the terminal and paste the following)

### Create a venv 
```bash	
python -m venv .venv
```
### Connect to venv on windows
```bash	
.venv\Scripts\activate
```
### Download requirements
```bash
pip install -r requirements.txt
```
## Create a folder with both the csv files in it

### Folder and filenames
* Folder name should be "data"
* personal csv should be named "kolj2.csv"
* general csv should be named "airports.csv"

## Start streamlit app
```python
streamlit run app.py --theme.base dark
```


