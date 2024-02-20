# meta-utils

## Genome-resolved metagenomics

### "make_depth_summaries.py"

For use in differential coverage binning of metagenomic contigs into metagenome-assembled genomes (MAGs).

Script takes individual metagenome depth profiles generated with different read sets and outputs three summary depth profiles:

1. Coverage in the given sample ("$sample"_depth-single.txt)
2. Coverage across related samples (e.g., from the same site) based on provided mapping file ("$sample"_depth-all.txt)
3. Coverage across all provided samples ("$sample"_depth-all.txt)

The depth profiles need to have been generated with the metaBAT (https://bitbucket.org/berkeleylab/metabat/src/master/) command "jgi_summarize_bam_contig_depths" and have the name structure:
"$sample"_"$reads".depth.txt.

The script also requires a tab-seperated mapping file with a site name in the first column, and sample name in the second column that corresponds to the sample names in the initial profile file names.

Example:

```
python scripts/make_depth_summaries.py \
  -sample "Sample_name" \
  -map "Site-to-sample_map_file.tsv" \
  -depth "Folder_with_all_depth_profiles" \
  -out "Output_folder"
```
