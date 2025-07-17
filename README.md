# BIDS2NDA
Extract [NIMH Data Archive](https://nda.nih.gov/) compatible metadata from [Brain Imaging Data Structure (BIDS)](https://bids-specification.readthedocs.io/) compatible datasets.

This builds a [`image03.csv`](https://nda.nih.gov/data-structure/image03) data structure for upload with [nda-tools](https://github.com/NDAR/nda-tools) or [web uploader](https://nda.nih.gov/vt/).
Data must first be organized in BIDS (see [bids-validator](https://bids-validator.readthedocs.io/en/stable/)) and [NDA's Global Unique IDentifiers](https://nda.nih.gov/nda/data-standards#guid) must have already been generated.

## Notable forks and resources
  * [brown-bnc/bids2nda](https://github.com/brown-bnc/bids2nda) adds `--expid_mapping` and `--lookup_csv`
  * [WillForan/bids2nda](https://github.com/WillForan/bids2nda)
  * Behavior and Neuroimaging Core at Brown University [NDA Upload docs (gitbook)](https://docs.ccv.brown.edu/bnc-user-manual/bids/bids-to-nimh-data-archive-nda)
  * Intermountain Neuroimaging Consortium (INC) at CU Bolder [NDA upload documentation (sphinix)](https://inc-documentation.readthedocs.io/en/dev/nda_uploads.html)

## Installation
```
pip install git@https://github.com/bids-standard/bids2nda
```

Or using [`uv`](https://docs.astral.sh/uv/)

```
uv tool install "bids2nda @ git+https://github.com/WillForan/bids2nda@lncd"
```

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
      --session_mapping SESSION_MAPPING
                        Path to auxiliary TSV to supplement or replace sessions.tsv/participants.tsv

## Prerequisites

Here is an example directory tree. In addition to BIDS organized `.nii.gz` and `.json` files, you will also need a GUID mapping, participants, and scans file.
```
guid_map.txt # ** GUID_MAPPING file: id lookup
eid_patt.txt # ** optional experiment ID pattern lookup file (vs json sidecar value)
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

Additionally, NDA specific actions are required

  * get assigned collection ID
  * generate GUIDs  ([guid-tool](https://nda.nih.gov/nda/nda-tools#:~:text=Tool%20Command%20Line-,installers,-File%20Name): `guid-tool -a get -b "$tmpcsv"`)
  * create fMRI experiment IDs

## Afterward

Upload with [nda-tools](https://github.com/NDAR/nda-tools)'s vtcmd, like

```
cd nda2bids_output
vtcmd image03.csv \
  -c $NDA_CONTAINER_ID \
  --title "$UPLOAD_TITLE"\
  --description "$DESC" \
  --buildPackage \
  --log-dir logs/ \
  --verbose \
  -w -j
```

## Input File descriptions 

### GUID_MAPPING file format
The guid mapping file uses the same format produced by the [GUID Tool](https://nda.nih.gov/nda/nda-tools#guid-tool), one line per subject source sperated by ` - `:

`<participant_id> - <GUID>`

It is not part of the BIDS specification.
The file translates BIDS subject id into NDA participant id (GUID) and can be stored anywhere.
Its location is explicitly given to the `bids2nda` command.

See [`examples/guid_map.txt`](examples/guid_map.txt)

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

### ExperimentID
NDA uploads `image03` uploads require the `'experiment_id'` column for fMRI (`_bold.nii.gz`) files.
Experiment IDs are created manually within a collection's experiment tab. See the NDA website's [collection page](https://ndar.nih.gov/user/dashboard/collections.html) and ["create nda experiments" chapter](https://nda.nih.gov/nda/tutorials/nda-experiments?chapter=create-nda-experiments).

#### Sidecar
For `_bold` suffixes, the value stored in the json sidecar with the key `ExperimentID` will be used. That is, `sub-1_task-rest_bold.json` might look like
```
{
 ...
 "ExperimentID": "1234",
}
```

#### ExperimentID Pattern TSV
If you do not want to modify existing sidecars, you can specify IDs based on file name patterns using a dedicated file.
This is not in the BIDS standard.

```
bids2nda ... --experimentid_tsv eid_patt.txt
```

where `eid_patt.txt` might look like

```
ExperimentID	Pattern
1234	task-rest
```

### Auxiliary Session mapping
The BIDS described root level `participant.tsv`, subject level `*_sessions.tsv`, session level `*_scans.tsv`, and json sidecar (`ExperimentID`, `Pho`) can describe all all the information needed for an NDA upload. However, `bids2nda` can also pull this information from a centralized `session map` tab separated file with a line per session. For an example see [`examples/session_map.txt`](examples/session_map.txt).

```
participant_id	session_id	acq_time	age	sex
sub-a	ses-1	2005-12-01	20	M
sub-a	ses-2	2005-01-01	39	M
```
