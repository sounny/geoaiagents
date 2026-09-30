from tools import submit

submit(
    branch_name="jules-2495290425968265034-2865bb1d",
    commit_message="Fix load_csv empty table on missing headers",
    title="Fix load_csv empty table on missing headers",
    description="Update `load_csv` to return a descriptive error string when no latitude/longitude headers are present in the CSV data."
)
