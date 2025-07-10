# BIDS2NDA
Extract NIMH Data Archive compatible metadata from Brain Imaging Data Structure (BIDS) compatible datasets

## Installation


    pip install https://github.com/INCF/BIDS2NDA/archive/master.zip


## Usage
<!-- python3 -m bids2nda.main -h -->

    usage: bids2nda [-h] [--experimentid_tsv EXPERIMENTID_TSV] BIDS_DIRECTORY GUID_MAPPING OUTPUT_DIRECTORY

    BIDS to NDA converter.

    positional arguments:
      BIDS_DIRECTORY    Location of the root of your BIDS compatible directory.
      GUID_MAPPING      Path to a text file with participant_id to GUID mapping.
                        You will need to use the GUID Tool
                        (https://ndar.nih.gov/contribute.html) to generate GUIDs
                        for your participants.
      OUTPUT_DIRECTORY  Directory where NDA files will be stored.

    optional arguments:
      -h, --help        Show this help message and exit.
      --experimentid_tsv EXPERIMENTID_TSV
                        Path to TSV file w/cols ExperimentID and Pattern for NDA EID lookup

## GUID_MAPPING file format
The is the file format produced by the GUID Tool, one line per subject in the format:

`<participant_id> - <GUID>`

## Example outputs
See [/examples](/examples)

## ExperimentID

### Sidecar
The `image03` column `'experiment_id'` is required for fMRI (`_bold.nii.gz`) files.
This is based on experiment IDs received from NDA after setting the study up through the NDA website [here](https://ndar.nih.gov/user/dashboard/collections.html).

For `_bold` suffixes, the value stored in the json sidecar with the key `ExperimentID` will be used. That is, `sub-1_task-rest_bold.json` might look like
```
{
 ...
 "ExperimentID": "1234",
}
```

### ExperimentID Pattern TSV
If you do not want to modify existing sidecars, you can specify IDs based on file name patterns using a dedicated file.

```
bids2nda ... --experimentid_tsv eid_patt.txt
```

where `eid_patt.txt` might look like

```
ExperimentID    Pattern
1234    task-rest
```
