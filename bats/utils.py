"""
Helper functions
"""

from bats.job import Job


def get_traces(job: Job) -> list[str]:
    """
    Print traces recorded by `record_info("TRACE", $trace)`
    """
    traces = [
        detail["text_data"]
        for result in job.results
        for detail in result["details"]
        if "title" in detail and detail["title"] == "TRACE"
    ]
    package = job.settings["BATS_PACKAGE"]
    # Ignore OOM failures in runc since these are expected
    if package == "runc":
        traces = list(filter(lambda t: "mem_cgroup_out_of_memory" not in t, traces))
    return traces
