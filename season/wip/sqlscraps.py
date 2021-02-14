df.to_sql("schedule", con, index=False, if_exists="replace")

con = sqlite3.connect("season/data.db")

pd.read_sql(
    """
    SELECT
    *
    FROM schedule
    WHERE
    fetched_at = (
        SELECT
        max(fetched_at)
        FROM schedule
    )
""",
    con,
)
