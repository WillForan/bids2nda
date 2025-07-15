import pandas as pd
import bids2nda
from bids2nda.session_info import sub_from_file, read_participant_info, read_scan_date


def test_sub_extract():
    sub = sub_from_file("path/sub-a/ses-b/sub-a_ses-b_thing.blah")
    assert sub == "sub-a"


def test_read_noses():
    df = read_participant_info("examples/bids-noses/")
    assert df.shape[0] == 2
    assert "sex" in df.columns


def test_read_ses():
    """
    ==> examples/bids-ses/sub-a/sub-a_sessions.tsv <==
    session_id      acq_time        age
    ses-1   2015-12-31      20
    ses-2   2025-01-01      39
    """
    df = read_participant_info("examples/bids-ses/")
    assert df.shape[0] == 4
    assert "sex" in df.columns
    assert "acq_time" in df.columns
    acq_times = df.acq_time.tolist()
    assert "2015-12-31" in acq_times  # ses-1
    assert "2025-01-01" in acq_times  # ses-2


def test_read_ses_aux():
    """
    ==> examples/session_map.txt <==
    partipant_id	session_id      acq_time        age	sex
    sub-a	ses-1   2005-12-01      20	M
    sub-a	ses-2   2005-01-01      39	M
    sub-b	ses-1   2000-12-01      15	M
    sub-b	ses-2   2000-01-01      19	M

    """
    aux_df = pd.read_table("examples/session_map.txt", sep="\t")
    df = read_participant_info("examples/bids-ses/", aux_df)
    assert df.shape[0] == 4
    assert "sex" in df.columns
    assert "acq_time" in df.columns
    acq_times = df.acq_time.tolist()
    assert "2005-12-01" in acq_times  # ses-1
    assert "2005-01-01" in acq_times  # ses-2
    assert {"M"} == set(df.sex.tolist())


def test_read_scan_date():
    date = read_scan_date(
        "examples/bids-noses/sub-a/sub-a_scans.tsv",
        "blah/blah/func/sub-a_task-rest_bold.nii.gz",
    )
    assert date == "2020-12-01"


def test_run_ses(tmpdir):
    """Test scans.tsv overwriting sessions.tsv
    ==> examples/bids-ses/sub-a/sub-a_sessions.tsv <==
    session_id      acq_time        age
    ses-1   2015-12-31      20
    ses-2   2025-01-01      39

    ==> examples/bids-ses/sub-a/ses-1/sub-a_ses-1_scans.tsv <==
    filename        acq_time
    anat/sub-a_ses-1_T1w.nii.gz     2015-02-02
    func/sub-a_ses-1_task-rest_bold.nii.gz  2010-12-01
    """
    args = bids2nda.parse_args(
        ["examples/bids-ses/", "examples/guid_map.txt", str(tmpdir)]
    )
    imgdf = bids2nda.run(args)
    assert imgdf.shape[0] == 8
    acq_times = imgdf.interview_date[imgdf.src_subject_id == "a"].tolist()
    # assert '2015-12-31' in acq_times
    assert "01/01/2025" in acq_times  # ses-2
    assert "02/02/2015" in acq_times  # t1 overwrite from scans.tsv
    assert "12/01/2010" in acq_times  # rest overwrite from scans.tsv

def test_run_ses_aux(tmpdir):
    """Test aux overwriting
    ==> examples/bids-ses/sub-a/ses-1/sub-a_ses-1_scans.tsv <==
    filename        acq_time
    anat/sub-a_ses-1_T1w.nii.gz     2015-02-02
    func/sub-a_ses-1_task-rest_bold.nii.gz  2010-12-01
    """
    args = bids2nda.parse_args(
        ["examples/bids-ses/", "examples/guid_map.txt", str(tmpdir),
         "--session_map", "examples/session_map.txt"]
    )
    imgdf = bids2nda.run(args)
    assert imgdf.shape[0] == 8
    acq_times = imgdf.interview_date.tolist()
    # dates from session_mapping
    expect_dates = {"12/01/2005","01/01/2005","12/01/2000","01/01/2000"}
    # dates changed by scans.tsv. mapping has sub-a ses-1 2005-12-01, scan.tsv adds two
    expect_dates -= {"12/01/2005"}
    expect_dates |= {"02/02/2015", "12/01/2010"}
    assert expect_dates == set(acq_times)

def test_run_noses(tmpdir):
    args = bids2nda.parse_args(
        ["examples/bids-noses/", "examples/guid_map.txt", str(tmpdir)]
    )
    imgdf = bids2nda.run(args)
    assert imgdf.shape[0] == 4
