# sRank

sRank is a rank correlation algorithm presented in paper "When Rank Order Isn’t Enough: New Statistical-Significance-Aware Correlation Measures".

Please cite the following paper when used the code:\
Kutlu, Mucahid, Tamer Elsayed, Maram Hasanain, and Matthew Lease. "When Rank Order Isn't Enough: New Statistical-Significance-Aware Correlation Measures." In Proceedings of the 27th ACM International Conference on Information and Knowledge Management, pp. 397-406. ACM, 2018.


## Installation

It is implemented with python. Download srank.py to run algorithm.

## Usage

```bash
run_results1='path_to_first_run_results'
run_results2='path_to_second_run_results'
### note that both run results should be in query-by-query format, not only mean scores.
### If you are using trec_eval for scoring metrics, just add additional -q to your command line.
alpha='it is alpha argument mentioned in the paper'
beta='it is beta argument mentioned in the paper'
### in any case of non-given alpha and beta, program will consider them as zero.
python srank.py -d1 $run_results1 -d2 $run_results2 -a $alpha -b $beta
```

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License
