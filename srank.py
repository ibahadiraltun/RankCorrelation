"""
    Bahadir Altun - github.com/ibahadiraltun/rank_correlation

    Rank Correlation using algorithm shared in paper, When Rank Order Isn’t Enough: New Statistical-Significance-Aware Correlation Measures.

    Please cite the following paper when used the code:
    Kutlu, Mucahid, Tamer Elsayed, Maram Hasanain, and Matthew Lease. "When Rank Order Isn't Enough: New Statistical-Significance-Aware Correlation Measures." In Proceedings of the 27th ACM International Conference on Information and Knowledge Management, pp. 397-406. ACM, 2018.

"""

import pandas as pd
import numpy as np
import logging
import sys
import os

from collections import defaultdict
from scipy import stats

import operator

# /Users/ibahadiraltun/Desktop/InformationRetrieval/trec_dataset/basedir_drank

dir_path_a = None # run results path for first ranking
dir_path_b = None # run results path for second ranking


# alpha and beta are the arguments that mentioned in the paper
alpha = None
beta = None

# keeps query by query run results for both a and b
# i.e run_results_a[run_id] is a list of scores seperated by queries
run_results_a = defaultdict(list)
run_results_b = defaultdict(list)

# keeps run_results for both a and b as a mean value
run_results_a_mean = defaultdict(float)
run_results_b_mean = defaultdict(float)

def get_run_results(dir_path):

    tmp_results = defaultdict(list)
    tmp_results_mean = defaultdict(float)

    for subdir, _, files in os.walk(dir_path):
        for fname in files:
            if '.' in fname:
                continue
            run_id = fname
            filepath = subdir + os.sep + fname
            with open(filepath) as current_run_results:
                lines = current_run_results.readlines()
                for line in lines:
                    line.replace('\n', '')
                    if 'all' in line:
                        tmp_results_mean[fname] = float(line.split('\t')[2])
                        continue
                    # query_id = line.split('\t')[1]
                    # query_id is not necessary to keep scores because scores will be sorted by query ids. run_results_a[run_id][i] is refers to same query as run_results_b[run_id][i]
                    score = float(line.split('\t')[2])
                    tmp_results[run_id].append(score)
    
    return tmp_results, tmp_results_mean

def run_naive_tau():

    print('\nRunning naive tau...')

    global run_results_a_mean, run_results_b_mean
    global dir_path_a, dir_path_b

    if dir_path_a == None or dir_path_b == None:
        print('Error: None type of directory')
        exit(0)

    try:
        _, run_results_a_mean = get_run_results(dir_path_a)
        _, run_results_b_mean = get_run_results(dir_path_b)

        # for key, value in run_results_a.items():
        #     print(str(key) + ' ----->\n' + str(value))

        num_of_runs = len(run_results_a_mean)
        if num_of_runs != len(run_results_b_mean):
            logging.error('Run lengths do not match')
            exit(0)

        cnt_allpairs = num_of_runs * (num_of_runs - 1) / 2
        cnt_concordant = 0
        cnt_discordant = 0

        for runid_a, score_a1 in run_results_a_mean.items():
            for runid_b, score_b2 in run_results_b_mean.items():
                if runid_a == runid_b: # same pair
                    continue
                if runid_a not in run_results_b_mean or runid_b not in run_results_a_mean:
                    logging.error('Runs do not match exactly : error at runs ' + str(runid_a) + ' ' + str(runid_b))
                    exit(0)
                # qsize = len(list_a)
                # for qindex in range(0, qsize):
            
                score_a2 = run_results_a_mean[runid_b]
                score_b1 = run_results_b_mean[runid_a]

                # score_a1 keeps the score of runid_a at run_results_a_mean
                # score_a2 keeps the score of runid_b at run_results_a_mean
                # score_b1 keeps the score of runid_a at run_results_b_mean
                # score_b2 keeps the score of runid_b at run_results_b_mean

                # therefore, if score_a1 < score_a2 and score_b1 < score_b2; these pairs are concordant
                # if score_a1 > score_a2 and score_b1 > score_b2; these pairs are concordant
                # else; that means our pairs sorted in reverse order so these pairs are discordant

                if ((score_a1 == score_a2) or (score_b1 == score_b2)): # neither discordant or concordant
                    continue
                if ((score_a1 < score_a2 and score_b1 < score_b2)
                    or (score_a1 > score_a2 and score_b1 > score_b2)):
                    # print(runid_a, runid_b, score_a1, score_a2, score_b1, score_b2)
                    cnt_concordant = cnt_concordant + 1
                else:
                    cnt_discordant = cnt_discordant + 1
        
        result = (cnt_concordant - cnt_discordant) * 0.5 / cnt_allpairs # we divide (cnt_concordant - cnt_discordant) by 2 because we counted every pair twice
    
        # print(cnt_concordant, cnt_discordant, num_of_runs, cnt_allpairs)

        scores_a = []
        scores_b = []
        for runid, score_a in run_results_a_mean.items():
            scores_a.append(score_a)
            scores_b.append(run_results_b_mean[runid])

        tau, _ = stats.kendalltau(scores_a, scores_b)

        print('Naive tau ===== ' + str(result) + '\tOriginal tau ===== ' + str(tau))

    except Exception as e:
        logging.error('Failed to parse directory: ' + str(e))


    return 

def run_naive_srank_unweighted():

    print('\nRunning naive srank unweighted...')

    global run_results_a_mean, run_results_b_mean
    global run_results_a, run_results_b
    global dir_path_a, dir_path_b
    global alpha, beta

    if alpha == None or beta == None:
        print('No given values for alpha/beta. Missing values considered as zero')
        if alpha == None: alpha = 0.0
        if beta == None: beta = 0.0


    if dir_path_a == None or dir_path_b == None:
        print('Error: None type of directory')
        exit(0)

    try:
        run_results_a, run_results_a_mean = get_run_results(dir_path_a)
        run_results_b, run_results_b_mean = get_run_results(dir_path_b)

        # for key, value in run_results_a.items():
        #     print(str(key) + ' ----->\n' + str(value))

        num_of_runs = len(run_results_a_mean)
        if num_of_runs != len(run_results_b_mean):
            logging.error('Run lengths do not match')
            exit(0)

        cnt_allpairs = num_of_runs * (num_of_runs - 1) / 2
        cnt_concordant = 0
        cnt_discordant = 0

        total_penalty = 0.0

        for runid_a, res_a1 in run_results_a.items():
            for runid_b, res_b2 in run_results_b.items():
                if runid_a == runid_b: # same pair
                    continue
                if runid_a not in run_results_b or runid_b not in run_results_a:
                    logging.error('Runs do not match exactly : error at runs ' + str(runid_a) + ' ' + str(runid_b))
                    exit(0)
                # qsize = len(list_a)
                # for qindex in range(0, qsize):
                
                score_a1 = run_results_a_mean[runid_a]
                score_b2 = run_results_b_mean[runid_b]
                score_a2 = run_results_a_mean[runid_b]
                score_b1 = run_results_b_mean[runid_a]

                # score_a1 keeps the score of runid_a at run_results_a_mean
                # score_a2 keeps the score of runid_b at run_results_a_mean
                # score_b1 keeps the score of runid_a at run_results_b_mean
                # score_b2 keeps the score of runid_b at run_results_b_mean

                # therefore, if score_a1 < score_a2 and score_b1 < score_b2; these pairs are concordant
                # if score_a1 > score_a2 and score_b1 > score_b2; these pairs are concordant
                # if there is at least one equality, then we cannot consider those pairs as concordant or discordant
                # else; that means our pairs sorted in reverse order so these pairs are discordant

                # res_a1 = run_results_a[runid_a]
                # res_b2 = run_results_b[runid_b]
                res_a2 = run_results_a[runid_b]
                res_b1 = run_results_b[runid_a]

                # res_a1 keeps the query indexed results of runid_a at run_results_a_mean
                # res_a2 keeps the query indexed results of runid_b at run_results_a_mean
                # res_b1 keeps the query indexed results of runid_a at run_results_b_mean
                # res_b2 keeps the query indexed results of runid_b at run_results_b_mean


                statistical_significance_runa, pval_runa = stats.ttest_ind(res_a1, res_b1)
                statistical_significance_runb, pval_runb = stats.ttest_ind(res_a2, res_b2)

                # any value less then or equal to threshold considered as statistical significant
                threshold = 0.05
                
                # keeps the P(R1, R2) value for current pair
                penalty = 0.0

                if ((score_a1 == score_a2) or (score_b1 == score_b2)): # no discordant and concordant
                    continue
                elif ((score_a1 < score_a2 and score_b1 < score_b2)
                    or (score_a1 > score_a2 and score_b1 > score_b2)):
                    # print(runid_a, runid_b, score_a1, score_a2, score_b1, score_b2)
                    # pairs are concordant
                    cnt_concordant = cnt_concordant + 1
                    if ((pval_runa >= threshold and pval_runb >= threshold)
                        or (pval_runa < threshold and pval_runb < threshold)): # case1 in the paper
                        penalty = 0.0
                    else: # (pval_runa >= threshold and pval_runb < threshold) or (pval_runa < threshold and pval_runb >= threshold), case2 in the paper
                        penalty = alpha
                else:
                    # pairs are discordant
                    cnt_discordant = cnt_discordant + 1
                    if (pval_runa >= threshold and pval_runb >= threshold): # case3 in the paper
                        penalty = beta
                    elif ((pval_runa >= threshold and pval_runb < threshold) or (pval_runa < threshold and pval_runb >= threshold)): # case4 in the paper
                        penalty = alpha + beta
                    else: # (pval_runa < threshold and pval_runb < threshold), case5 in the paper
                        penalty = 2.0
                
                total_penalty = total_penalty + (1 - penalty)

        # result = (cnt_concordant - cnt_discordant) / cnt_allpairs

        result = (total_penalty * 0.5) / cnt_allpairs # we divide total_penalty by 2 beacuse we counted every pair twice
    
        # print(cnt_concordant, cnt_discordant, num_of_runs, cnt_allpairs)

        # scores_a = []
        # scores_b = []
        # for runid, score_a in run_results_a_mean.items():
        #     scores_a.append(score_a)
        #     scores_b.append(run_results_b_mean[runid])

        # tau, _ = stats.kendalltau(scores_a, scores_b)

        # print('Naive tau ===== ' + str(result) + '\tOriginal tau ===== ' + str(tau))

        print('Naive srank with unweighted ===== ' + str(result))

    except Exception as e:
        logging.error('Failed to parse directory: ' + str(e))


    return 


def run_naive_srank_weighted():

    print('\nRunning naive srank weighted...')

    global run_results_a_mean, run_results_b_mean
    global run_results_a, run_results_b
    global dir_path_a, dir_path_b
    global alpha, beta

    if alpha == None or beta == None:
        print('No given values for alpha/beta. Missing values considered as zero')
        if alpha == None: alpha = 0.0
        if beta == None: beta = 0.0


    if dir_path_a == None or dir_path_b == None:
        print('Error: None type of directory')
        exit(0)

    try:
        run_results_a, run_results_a_mean = get_run_results(dir_path_a)
        run_results_b, run_results_b_mean = get_run_results(dir_path_b)

        # print(run_results_a_mean)
        # print('--------')
        # print(run_results_b_mean)


        # sorting ranks according to their average scores.
        sorted_run_results_a_mean = sorted(run_results_a_mean.items(), key = operator.itemgetter(1), reverse = True)
        sorted_run_results_b_mean = sorted(run_results_b_mean.items(), key = operator.itemgetter(1), reverse = True)

        # print('--------')
        # print(sorted_run_results_a_mean)
        # print('--------')
        # print(sorted_run_results_b_mean)

        # for key, value in run_results_a.items():
        #     print(str(key) + ' ----->\n' + str(value))

        num_of_runs = len(run_results_a_mean)
        if num_of_runs != len(run_results_b_mean):
            logging.error('Run lengths do not match')
            exit(0)

        cnt_allpairs = num_of_runs * (num_of_runs - 1) / 2
        cnt_concordant = 0
        cnt_discordant = 0

        total_penalty = 0.0

        index_a = 0
        for runid_a, res_a1 in run_results_a.items():
            index_a = index_a + 1
            if index_a == 1: continue
            index_b = 0
            total_C = 0
            for runid_b, res_b2 in run_results_b.items():
                index_b = index_b + 1
                if index_b == index_a: break
                if runid_a == runid_b: # same pair
                    continue
                if runid_a not in run_results_b or runid_b not in run_results_a:
                    logging.error('Runs do not match exactly : error at runs ' + str(runid_a) + ' ' + str(runid_b))
                    exit(0)
                # qsize = len(list_a)
                # for qindex in range(0, qsize):
                
                score_a1 = run_results_a_mean[runid_a]
                score_b2 = run_results_b_mean[runid_b]
                score_a2 = run_results_a_mean[runid_b]
                score_b1 = run_results_b_mean[runid_a]

                # score_a1 keeps the score of runid_a at run_results_a_mean
                # score_a2 keeps the score of runid_b at run_results_a_mean
                # score_b1 keeps the score of runid_a at run_results_b_mean
                # score_b2 keeps the score of runid_b at run_results_b_mean

                # therefore, if score_a1 < score_a2 and score_b1 < score_b2; these pairs are concordant
                # if score_a1 > score_a2 and score_b1 > score_b2; these pairs are concordant
                # if there is at least one equality, then we cannot consider those pairs as concordant or discordant
                # else; that means our pairs sorted in reverse order so these pairs are discordant

                # res_a1 = run_results_a[runid_a]
                # res_b2 = run_results_b[runid_b]
                res_a2 = run_results_a[runid_b]
                res_b1 = run_results_b[runid_a]

                # res_a1 keeps the query indexed results of runid_a at run_results_a_mean
                # res_a2 keeps the query indexed results of runid_b at run_results_a_mean
                # res_b1 keeps the query indexed results of runid_a at run_results_b_mean
                # res_b2 keeps the query indexed results of runid_b at run_results_b_mean


                statistical_significance_runa, pval_runa = stats.ttest_ind(res_a1, res_b1)
                statistical_significance_runb, pval_runb = stats.ttest_ind(res_a2, res_b2)

                # any value less then or equal to threshold considered as statistical significant
                threshold = 0.05
                
                # keeps the P(R1, R2) value for current pair
                penalty = 0.0

                if ((score_a1 == score_a2) or (score_b1 == score_b2)): # no discordant and concordant
                    continue
                elif ((score_a1 < score_a2 and score_b1 < score_b2)
                    or (score_a1 > score_a2 and score_b1 > score_b2)):
                    # print(runid_a, runid_b, score_a1, score_a2, score_b1, score_b2)
                    # pairs are concordant
                    cnt_concordant = cnt_concordant + 1
                    if ((pval_runa >= threshold and pval_runb >= threshold)
                        or (pval_runa < threshold and pval_runb < threshold)): # case1 in the paper
                        penalty = 0.0
                    else: # (pval_runa >= threshold and pval_runb < threshold) or (pval_runa < threshold and pval_runb >= threshold), case2 in the paper
                        penalty = alpha
                else:
                    # pairs are discordant
                    cnt_discordant = cnt_discordant + 1
                    if (pval_runa >= threshold and pval_runb >= threshold): # case3 in the paper
                        penalty = beta
                    elif ((pval_runa >= threshold and pval_runb < threshold) or (pval_runa < threshold and pval_runb >= threshold)): # case4 in the paper
                        penalty = alpha + beta
                    else: # (pval_runa < threshold and pval_runb < threshold), case5 in the paper
                        penalty = 2.0
                
                total_C = total_C + (1 - penalty)

            # print(index_a, total_C, total_penalty)

            total_penalty = total_penalty + ((total_C / (index_a - 1))) # head-weighted 

        # result = (cnt_concordant - cnt_discordant) / cnt_allpairs

        result = (total_penalty / (num_of_runs - 1))
    
        # print(cnt_concordant, cnt_discordant, num_of_runs, cnt_allpairs)

        # scores_a = []
        # scores_b = []
        # for runid, score_a in run_results_a_mean.items():
        #     scores_a.append(score_a)
        #     scores_b.append(run_results_b_mean[runid])

        # tau, _ = stats.kendalltau(scores_a, scores_b)

        # print('Naive tau ===== ' + str(result) + '\tOriginal tau ===== ' + str(tau))

        print('Naive srank with weighted ===== ' + str(result))

    except Exception as e:
        logging.error('Failed to parse directory: ' + str(e))


    return 



if __name__ == '__main__':

    args_length = len(sys.argv)

    for i in range(0, args_length):
        if sys.argv[i] == '-d1':
            dir_path_a = sys.argv[i + 1]
            i = i + 1
        if sys.argv[i] == '-d2':
            dir_path_b = sys.argv[i + 1]
            i = i + 1
        if sys.argv[i] == '-a':
            alpha = float(sys.argv[i + 1])
            i = i + 1
        if sys.argv[i] == '-b':
            beta = float(sys.argv[i + 1])
            i = i + 1


    run_naive_tau()
    run_naive_srank_unweighted()
    run_naive_srank_weighted()

