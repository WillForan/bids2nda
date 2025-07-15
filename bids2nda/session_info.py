"""
Reading session and participant information.
Age, Sex, and AcqTime from BIDS standard files or from auxiliary lookups.
"""
import os.path
import re
from glob import glob

import pandas as pd


def sub_from_file(path: str) -> str | None:
    """Quick subj extraction from file path.
    >>> sub_from_file('bids/sub-12ab/ses-xyz')
    12ab
    """
    if m := re.search(r"sub-([^_/-]*)", path):
        return m.group(0)
    return None


def outer_merge(
    auth_df: pd.DataFrame,
    participants_df: pd.DataFrame,
    auth_desc: str = "auth",
    part_desc: str = "prev",
) -> pd.DataFrame:
    """
    Merge new authoritative dataframe with existing participants.
    Report columns in non-auth df that might be overwritten.
    Include session_id in merge if exists in both inputs.
    """

    print(f"Using {auth_df.shape[0]} {auth_desc} rows ({auth_df.columns})")
    # do we have what we need to merge
    shared_cols = set(auth_df.columns).intersection(set(participants_df.columns))
    if "participant_id" not in shared_cols:
        raise Exception(
            "{auth_desc} or {part_desc} is missing 'participant_id' column!"
        )

    # are we overwriting data?
    overlap = shared_cols - {"participant_id", "session_id"}
    if len(overlap) != 0:
        print(
            f"WARNING: {auth_desc} and {part_desc} share overlapping columns {overlap}."
            + f"Will keep only values from {auth_desc}."
        )

    # should session be included in merge?
    merge_cols = ["participant_id"]
    if "session_id" in shared_cols:
        merge_cols += ["session_id"]

    # outer merge with auth df prefix set to empty string:
    #  for all shared columns, only take auth's value
    nonauth_prefix = "_" + auth_desc.replace(" ", "_")
    merged = auth_df.merge(
        participants_df,
        how="outer",  # use everything
        on=merge_cols,
        suffixes=("", nonauth_prefix),
    )
    return merged


def read_participant_info(
    bids_directory: os.PathLike, aux_df: pd.DataFrame | None = None
) -> pd.DataFrame:
    """Build DataFrame for age and sex lookup. Uses successive outer merges to allow for multiple sources
    In order of authoritative information:
      1. auxiliary session mapping
      2. sessions.tsv
      3. participants.tsv

    Note: scan.tsv AcqTime will still trump any value in these other three places.
    """
    # lowest authority first: participants.tsv at root of BIDS directory
    participants_file = os.path.join(bids_directory, "participants.tsv")
    if os.path.isfile(participants_file):
        participants_df = pd.read_csv(participants_file, header=0, sep="\t")
    else:
        print("WARNING: {participants_file} does not exist.")
        participants_df = pd.DataFrame(columns=["participant_id"])

    # higher priority: session values stored in per sub- folder
    sessions_files = glob(os.path.join(bids_directory, "sub-*", "*_sessions.tsv"))
    if len(sessions_files) > 0:
        sessions_df = pd.concat(
            (
                pd.read_csv(f, sep="\t").assign(participant_id=sub_from_file(f))
                for f in sessions_files
            ),
            ignore_index=True,
        )

        participants_df = outer_merge(
            sessions_df, participants_df, "session files", "participants.tsv"
        )

    # final source: file provided on command line
    if aux_df is not None:
        participants_df = outer_merge(
            aux_df, participants_df, "auxiliary tsv", "participants.tsv sessions.tsv"
        )

    if "age" not in participants_df.columns or "sex" not in participants_df.columns:
        raise Exception(
            f"{participants_file}, sub-*/sessions.tsv, nor auxiliary lookup provide columns 'age' and 'sex' for nda columns 'interview_age' and 'sex' (have: {list(participants_df.columns)})"
        )

    return participants_df


def read_scan_date(scans_file: str, file: str) -> str:
    """Extract acq_time from scan_file.
    Find row where filename column value matches ``file``"""
    if not os.path.exists(scans_file):
        print(
            "%s file not found - information about scan date required by NDA could not be found. Alternatively, information could be stored in sessions.tsv"
            % scans_file
        )
        sys.exit(-1)
    scans_df = pd.read_csv(scans_file, header=0, sep="\t")
    if "filename" not in scans_df.columns or "acq_time" not in scans_df.columns:
        raise Exception(
            f"{scans_file} must have columns 'filename' and 'acq_time' (YYYY-MM-DD) to create 'interview_date' nda column'"
        )

    for _, row in scans_df.iterrows():
        if file.endswith(row["filename"].replace("/", os.sep)):
            return row.acq_time
    raise Exception(f"no row where filename={file} in {scans_file}")
