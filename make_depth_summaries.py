#!/usr/bin/env python

"""
Author: Jennah Dharamshi
Date: 220115

As input this script takes depth profiles for a metagenome sample generated
with different read sets. The depth profiles need to have been generated
with the metaBAT command "jgi_summarize_bam_contig_depths" and have the name structure:
"$sample"_"$reads".depth.txt.

The script also requires a mapping file with a site name in the first column,
and sample name in the second column that corresponds to the sample names in
the initial profile file names.

As output the script will generate three depth profiles:
- "$sample"_depth-single.txt
    A depth profile with only reads from the focal sample.
- "$sample"_depth-site.txt
    A depth profile using read sets obtained from the sample/similar sampling site
    (e.g., different depths from the same lake).
- "$sample"_depth-all.txt
    A depth profile using all read sets
"""

__author__ = 'djennah'

#################################################################################################
##Modules##

import pandas as pd
import argparse
import glob

#################################################################################################
#Command-line usage with argparser

parser = argparse.ArgumentParser(prog='make_depth_summaries.py',
	formatter_class=argparse.ArgumentDefaultsHelpFormatter,
	description='Make summary depth profiles from those generated with different reads sets.')

parser.add_argument('-sample', '--sample', required=True, help = 'Focal \
	sample name to which read sets were mapped.')

parser.add_argument('-map', '--map', required=True, help = 'Path \
	to mapping file of sites and samples.')

parser.add_argument('-depth', '--depth', required=True, help = 'Path \
	to the folder with depth profiles for all reads sets of interest.')

parser.add_argument('-out', '--out', required=True, help = 'Path \
	to the folder where depth profiles should be output.')

args = parser.parse_args()

#################################################################################################
##Functions##
def make_file_list(depth):
    files = []
    for file in glob.glob(args.depth + "/*.depth.txt"):
        files.append(file)
    return files

def parse_map_file(map, focal_sample):
    sample_dict = {}
    with open(args.map, 'r') as f:
        next(f)
        for line in f:
            site, sample = line.strip("\n").split("\t")
            if sample == focal_sample:
                focal_site = site
            if site not in sample_dict.keys():
                sample_dict[site] = []
            sample_dict[site].append(sample)
    return sample_dict, focal_site

def depth_single(focal_sample, files):
    profile = focal_sample + "_" + focal_sample
    for file in files:
        if profile in file:
            profile_single = pd.read_csv(file, sep='\t')
    return profile_single

def subset_files(focal_sample, samples, files):
    files_subset = []
    for sample in samples:
        wanted = focal_sample + "_" + sample
        file = list(filter(lambda x: wanted in x, files))[0]
        files_subset.append(file)
    return files_subset

def depth_multiple(profile_single, files):
    profile_multiple = profile_single[["contigName","contigLen"]]
    for file in files:
        df = pd.read_csv(file, sep='\t')
        df2 = df.iloc[:,[3,4]]
        profile_multiple = pd.concat([profile_multiple, df2], axis=1)
    return profile_multiple

def totalAvgDepth(profile_multiple):
    sum = profile_multiple.filter(regex=".sorted.bam$").sum(axis=1)
    profile_multiple.insert(2, "totalAvgDepth", sum)
    return profile_multiple

#################################################################################################
##Implementation##

#Focal sample
focal_sample = str(args.sample)

#Make list of all depth profiles in given directory
files = make_file_list(args.depth)

#Make dictionary of samples to sites and focal site
sample_dict, focal_site = parse_map_file(args.map, focal_sample)

#Make depth-single profile
profile_single = depth_single(focal_sample, files)
profile_single.to_csv(args.out + "/" + focal_sample + "_depth-single.txt", sep='\t', index=False)

#Make depth-site profile
samples_site = sample_dict[focal_site]
files_site = subset_files(focal_sample, samples_site, files)
profile_site = depth_multiple(profile_single, files_site)
profile_site = totalAvgDepth(profile_site)
profile_site.to_csv(args.out + "/" + focal_sample + "_depth-site.txt", sep='\t', index=False)

#Make depth-all profile
samples_all = list(sample_dict.values())
samples_all = sum(samples_all, [])
files_all = subset_files(focal_sample, samples_all, files)
profile_all = depth_multiple(profile_single, files_all)
profile_all = totalAvgDepth(profile_all)
profile_all.to_csv(args.out + "/" + focal_sample + "_depth-all.txt", sep='\t', index=False)
