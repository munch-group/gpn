from gpn.data import Genome, make_windows, get_seq
import math
import numpy as np
import os
import pandas as pd
from tqdm import tqdm


intervals = pd.read_parquet(input[0])
genome = Genome(input[1])
intervals = make_windows(
    intervals, config["window_size"], config["step_size"], config["add_rc"],
)
print(intervals)
intervals = intervals.sample(frac=1.0, random_state=42)
intervals["assembly"] = wildcards["assembly"]
intervals = intervals[["assembly", "chrom", "start", "end", "strand"]]
intervals = get_seq(intervals, genome)
print(intervals)

chroms = intervals.chrom.unique()
chrom_split = np.random.choice(
    splits, p=split_proportions, size=len(chroms),
)
chrom_split[np.isin(chroms, config["whitelist_validation_chroms"])] = "validation"
chrom_split[np.isin(chroms, config["whitelist_test_chroms"])] = "test"
chrom_split = pd.Series(chrom_split, index=chroms)

intervals_split = chrom_split[intervals.chrom]

for path, split in zip(output, splits):
    print(path, split)
    # to parquet to be able to load faster later
    intervals[(intervals_split==split).values].to_parquet(
        path, index=False,
    )