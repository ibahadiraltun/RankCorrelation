# sRank

sRank is a rank correlation algorithm presented in paper "When Rank Order Isn’t Enough: New Statistical-Significance-Aware Correlation Measures".

Please cite the following paper for the rank correlation metric:\
Kutlu, Mucahid, Tamer Elsayed, Maram Hasanain, and Matthew Lease. "When Rank Order Isn't Enough: New Statistical-Significance-Aware Correlation Measures." In Proceedings of the 27th ACM International Conference on Information and Knowledge Management, pp. 397-406. ACM, 2018.


## Installation

It is implemented with python 3.6. Clone this repository to use.

```bash
git clone https://github.com/ibahadiraltun/RankCorrelation
```

## Usage

It is neccessary to import scipy(1.1.0) package to program.
```bash
pip install scipy
```
To run this code from terminal, there are few variables that needs to be clarified.\
-d1: It is the path to the first run-results folder.\
-d2: It is the path to the second run-results folder.\
Note: For both -d1 and -d2, referenced folders must contains run-results with query by query format. If you are using trec_eval to evaluate, just simply add -q to your command.\
-a: The alpha argument mentioned in the paper.\
-b: The beta argument mentioned in the paper.\
Note: The default value of alpha and beta are 0 and 2, respectively.\
-h: This is the parameter to set head-weighted version of the metric. If true, then it will be head-weighted (tau_SigH). Otherwise, it is tau_Sig.
```bash
python srank.py -d1 path_to_first_run_results -d2 path_to_second_run_results -a alpha -b beta -h flag
```

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License
