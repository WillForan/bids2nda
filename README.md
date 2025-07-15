# BIDS2NDA
Extract [NIMH Data Archive](https://nda.nih.gov/) compatible metadata from [Brain Imaging Data Structure (BIDS)](https://bids-specification.readthedocs.io/) compatible datasets.

This builds a [`image03.csv`](https://nda.nih.gov/data-structure/image03) data structure for upload with [nda-tools](https://github.com/NDAR/nda-tools) or [web uploader](https://nda.nih.gov/vt/).
Data must first be organized in BIDS (see [bids-validator](https://bids-validator.readthedocs.io/en/stable/)) and [NDA's Global Unique IDentifiers](https://nda.nih.gov/nda/data-standards#guid) must have already been generated.

## Installation


    pip install https://github.com/INCF/BIDS2NDA/archive/master.zip


## Usage

    usage: bids2nda [-h] [-v] BIDS_DIRECTORY GUID_MAPPING OUTPUT_DIRECTORY

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

## Prerequisites

Here is an example directory tree. In addition to BIDS organized `.nii.gz` and `.json` files, you will also need a GUID mapping, participants, and scans file.
```
guid_map.txt # ** GUID_MAPPING file: id lookup
BIDS/
├── participants.tsv # ** Participants File: age, sex
└── sub-10000
    └── ses-1
        ├── anat
        │   ├── sub-10000_ses-1_T1w.json
        │   ├── sub-10000_ses-1_T1w.nii.gz
        ├── func
        │   ├── sub-10000_ses-1_task-rest_bold.json
        │   ├── sub-10000_ses-1_task-rest_bold.nii.gz
        └── sub-10000_ses-1_scans.tsv # ** Scans File: acq_time->interview_date
```


### GUID_MAPPING file format
The is the file format produced by the [GUID Tool](https://nda.nih.gov/nda/nda-tools#guid-tool), one line per subject in the format:

`<participant_id> - <GUID>`

It is not part of the BIDS specification.
The file translates BIDS subject id into NDA participant id (GUID) and can be stored anywhere.
Its location is explicitly given to the `bids2nda` command.

### Participants File
A [Participants File](https://bids-specification.readthedocs.io/en/stable/modality-agnostic-files.html#participants-file) is at the BIDS root like `BIDS/participants.tsv`.
It should at least have columns `participant_id`, `age`, and `sex`.

|col|desc|notes|
|---|---|---|
|`particiapnt_id` | like `sub-X` | does not include session label (See [Sessions File](https://bids-specification.readthedocs.io/en/stable/modality-agnostic-files.html#sessions-file). Not supported here) |
|`age` | number in years | converted to months for NDA's `interview_age`|
|`sex` |||

Contents could look like
```
participant_id	sex	age
sub-100000  	M	46
```

### Scans File

[Scans File](https://bids-specification.readthedocs.io/en/stable/modality-agnostic-files.html#scans-file) is at the session (or subject if session is omitted) level like `BIDS/sub-X/ses-1/sub-X_ses-1_scans.tsv`. 
It must have at least `filename` and `acq_time`.

|col|desc|notes|
|---|---|---|
|`filename`| like `func/sub-X_bold.nii.gz` | relative to session root |
|`acq_time`| date like `YYYY-MM-DD` | creates `interview_date` NDA column|


Contents could look like
```
acq_time	filename
2000-12-31	anat/sub-100000_ses-1_T1w.nii.gz
2000-12-31	func/sub-100000_ses-1_task-rest_bold.nii.gz
```

## Example outputs
See [/examples](/examples)

## Notes:
Column `'experiment_id'` must be manually filled.
For `_bold` suffixes, the value stored in the json sidecar with the key `ExperimentID` will be used.
This is based on experiment IDs received from NDA after setting the study up through the NDA website [here](https://ndar.nih.gov/user/dashboard/collections.html).
