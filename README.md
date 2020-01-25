# De-anonymizing Programmers via Code Stylometry
This project is Python implementation of [a work by Caliskan et al.](https://www.usenix.org/system/files/conference/usenixsecurity15/sec15-paper-caliskan-islam.pdf) 
for Java language.

## Installation
Clone the repo and install python packages:
```
git clone https://github.com/rebryk/code_stylometry.git
cd code_stylometry
pip install -r requirements.txt
```

## Usage

### Dataset
Training and validation data is represented by source code of solutions 
to programming tasks from the international programming competition Google Code Jam. 

`data/metadata.json` contains description of rounds and problems that were used to create the dataset.

If you want to download the corpus on your machine, run the following code:
```
cd data/
python crawler.py
```

It will download the solution files in `java` into `data/codejam` directory.
File paths will look like `data/codejam/<round_id>/<problem_id>/<username>.java` 

### Features
The `features` package contains a few useful functions:
* `calculate_features_for_files(files)`
<br>This function calculates sets of features for the given source files.
<br>Usage example: `samples = calculate_features_for_files(['A.java', B.java'])`
* `build_dataset(samples)`
<br>Builds a pandas data frame from the given list of feature sets.
<br>Usage example: `df = build_dataset(samples)`

### Training and validation
You can open [De-anonymizing Programmers via Code Stylometry.ipynb](De-anonymizing%20Programmers%20via%20Code%20Stylometry.ipynb) to see how the methods above are used
to de-anonymize 100 users with 9 code files each.

[CatBoost](http://catboost.ai/) is used to train the model. 

## License
[MIT](LICENSE)
